#!/usr/bin/env python3
"""capcut_brabo.py — motor do Editor Brabo CapCut (MKT iGreen). Lê e escreve o rascunho do CapCut desktop (draft_content.json,
JSON aberto no CapCut 9.5 desta máquina) para montar cortes, legendas e sons sem clicar, e radiografar o que o Matheus editou.

  python capcut_brabo.py listar
  python capcut_brabo.py raio-x <projeto> [--json saida.json]
  python capcut_brabo.py capturar <projeto> (--texto "LEGENDA" | --segmento ID) --como legenda [--curva]
  python capcut_brabo.py cortes <projeto> <edl.json> --midia <pasta_ou_arquivo> [--trilha "Brabo · Cortes"]
  python capcut_brabo.py paginar <palavras.json> [--edl edl.json] [--destaques "economia,desconto"] -o paginas.json
  python capcut_brabo.py formato <projeto> 9:16|16:9|4:5|1:1
  python capcut_brabo.py legendas <projeto> <paginas.json> --esqueleto legenda|basico [--y -0.62] [--trilha "Brabo · Legenda"]
  python capcut_brabo.py audio <projeto> <arquivo> --em 3.2 [--volume 0.4] [--trilha "Brabo · SFX"]
  python capcut_brabo.py punch <projeto> [--escala 1.12] [--a-cada 2] [--rosto-y 0.25]
  python capcut_brabo.py zoom <projeto> --em 4.0 [--dur 0.4] [--para 1.15] [--curva cam65_100] [--rosto-y 0.5] | --lote zooms.json
  python capcut_brabo.py letreiros <projeto> letreiros.json
  python capcut_brabo.py atras <projeto> atras.json --midia <pasta_dos_brutos>   (texto atrás da pessoa)
  python capcut_brabo.py legenda-palavras <projeto> paginas.json [--px 32]      (LEGENDA DO AFTER: um segmento por palavra)
  python capcut_brabo.py legenda-apple <projeto> paginas.json [--y -0.62]       (antiga: página com palavras reveladas)
  python capcut_brabo.py camera <projeto> camera.json                         (CÂMERA DO AFTER: deriva, salto que fica, ênfase, out)
  python capcut_brabo.py tremida <projeto> --em 57.6[,110.0] [--amount 43]
  python capcut_brabo.py flash <projeto> --em 57.6[,...] [--cor white] [--pico 0.5]
  python capcut_brabo.py tirar <projeto> "Brabo · Legenda" ["Brabo · Pílula" …]
  python capcut_brabo.py religar <projeto> --de C:/caminho/antigo --para D:/caminho/novo
  python capcut_brabo.py validar <projeto>

<projeto> = nome do rascunho na tela inicial do CapCut ("1019") ou a pasta dele.
REGRAS DE SEGURANÇA (não negociar):
  - Escrita só com o CapCut FECHADO (ele regrava o rascunho ao fechar e apagaria a edição). O motor recusa se o processo estiver aberto.
  - Toda escrita faz backup antes em MKT/Editor-Brabo/_backups/<projeto>/<data>_<comando>/.
  - Trilhas do motor têm nome "Brabo · …": rodar de novo SUBSTITUI só a trilha de mesmo nome. Trilha do Matheus nunca é tocada.
Tempos no rascunho = microssegundos (1 s = 1_000_000). Posição do clipe: transform x/y normalizado (0 = centro, ±1 = borda;
y positivo = para cima).
"""
import copy, glob, json, math, os, re, shutil, subprocess, sys, time, uuid

sys.stdout.reconfigure(encoding="utf-8")
AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ_SISTEMA = os.path.abspath(os.path.join(AQUI, "..", ".."))
ESQ_DIR = os.path.join(AQUI, "esqueletos")
BACKUPS = os.path.join(RAIZ_SISTEMA, "_backups")
DRAFTS = os.environ.get("CAPCUT_DRAFTS") or os.path.join(
    os.environ.get("LOCALAPPDATA", ""), "CapCut", "User Data", "Projects", "com.lveditor.draft")
US = 1_000_000
# palavras que nunca fecham página de legenda (Crivo do Matheus, fórmula viral)
NAO_TERMINA = {"o", "a", "os", "as", "de", "do", "da", "dos", "das", "em", "no", "na", "nos", "nas", "que", "pra", "para", "com",
               "e", "um", "uma", "por", "pelo", "pela", "se", "seu", "sua", "seus", "suas", "ao", "à", "mais", "muito", "é", "não",
               "te", "me", "lhe", "nos", "vai", "vão", "faz", "pode", "deve", "cada", "esse", "essa", "este", "esta", "nosso", "nossa"}


# ---------------------------------------------------------------- utilidades
def novo_id():
    u = str(uuid.uuid4()).upper().split("-")
    u[2] = u[2].lower()                      # o CapCut grava o 3º grupo em minúsculas (ex.: 494705A1-55E3-4c85-BDE7-…)
    return "-".join(u)


def us(seg):
    return int(round(float(seg) * US))


def capcut_aberto():
    try:
        out = subprocess.run(["tasklist", "/FI", "IMAGENAME eq CapCut.exe", "/NH"], capture_output=True, text=True).stdout
    except FileNotFoundError:
        return False
    return "capcut.exe" in out.lower()


def pasta_projeto(arg):
    if os.path.isdir(arg):
        return os.path.abspath(arg)
    p = os.path.join(DRAFTS, arg)
    if os.path.isdir(p):
        return p
    meta = os.path.join(DRAFTS, "root_meta_info.json")
    if os.path.exists(meta):
        for it in json.load(open(meta, encoding="utf-8-sig")).get("all_draft_store", []):
            if it.get("draft_name") == arg:
                return os.path.normpath(it["draft_fold_path"])
    sys.exit("Projeto não encontrado: %s (use `listar`)" % arg)


def copias_conteudo(pasta, d=None):
    """Arquivos que guardam a linha do tempo: o da raiz e o da timeline (CapCut 9.x tem Timelines/<id>/)."""
    fs = [os.path.join(pasta, "draft_content.json")]
    tid = (d or {}).get("id")
    if tid:
        t = os.path.join(pasta, "Timelines", tid, "draft_content.json")
        if os.path.exists(t):
            fs.append(t)
    return fs


def carregar(arg):
    pasta = pasta_projeto(arg)
    f = os.path.join(pasta, "draft_content.json")
    with open(f, "rb") as h:
        cab = h.read(1)
    if cab != b"{":
        sys.exit("draft_content.json não é JSON aberto (criptografado?). Esta versão do CapCut não aceita edição pelo motor.")
    d = json.load(open(f, encoding="utf-8-sig"))
    tempo_das_keys(d, -1)
    return pasta, d


def tempo_das_keys(d, sentido):
    """Keys de VÍDEO/ÁUDIO no CapCut 9.5 contam o tempo NO ARQUIVO (time_offset = início do trecho no bruto + tempo no segmento × vel),
    não do começo do segmento (medido em 22/10/2026 no 1020: o vídeo de baixo ficou parado no último valor da câmera, porque o corte
    começa aos 9 s/75 s/320 s do bruto e as keys gravadas de 0 a 7 s caíam "antes"; o recorte, que começa no 0 do .mov, andava certo).
    Dentro do motor as keys ficam relativas ao segmento (o resto do código não muda): sentido −1 ao carregar, +1 ao salvar.
    Texto e imagem sem source_timerange não mudam (texto conta do segmento: pop dos letreiros conferido na tela)."""
    for t in d["tracks"]:
        if t["type"] not in ("video", "audio"):
            continue
        for sg in t["segments"]:
            st = sg.get("source_timerange")
            if not st or not sg.get("common_keyframes"):
                continue
            vel = sg.get("speed") or 1.0
            for ck in sg["common_keyframes"]:
                for k in ck.get("keyframe_list") or []:
                    if sentido > 0:
                        k["time_offset"] = int(round(st["start"] + k["time_offset"] * vel))
                    else:
                        k["time_offset"] = int(round((k["time_offset"] - st["start"]) / vel))


def backup_todos(motivo):
    """Cópia de TODOS os rascunhos (arquivos de projeto, sem mídia pesada) antes de qualquer escrita. Regra criada em 20/10/2026,
    depois que o 1001 sumiu sem backup: o motor só guardava o projeto que ia gravar."""
    if not os.path.isdir(DRAFTS):
        return
    destino = os.path.join(BACKUPS, "_todos", time.strftime("%Y%m%d-%H%M%S") + "_" + re.sub(r"\W+", "-", motivo))
    n = 0
    for raiz, _, fs in os.walk(DRAFTS):
        for f in fs:
            p = os.path.join(raiz, f)
            if os.path.getsize(p) > 20_000_000 or os.path.splitext(f)[1].lower() in (".mp4", ".mov", ".mp3", ".wav", ".m4a"):
                continue
            alvo = os.path.join(destino, os.path.relpath(p, DRAFTS))
            os.makedirs(os.path.dirname(alvo), exist_ok=True)
            shutil.copy2(p, alvo)
            n += 1
    print("backup de todos os rascunhos: %d arquivos → %s" % (n, destino))


def salvar(pasta, d, motivo):
    na_pasta_do_capcut = os.path.normcase(os.path.abspath(pasta)).startswith(os.path.normcase(os.path.abspath(DRAFTS)))
    if na_pasta_do_capcut and capcut_aberto():           # cópia fora da pasta do CapCut (testes) pode gravar com ele aberto
        # 20/10/2026: o teste "ao vivo" (gravar com o CapCut na tela inicial) foi seguido da remoção dos projetos 1001 e 1019
        # da pasta de rascunhos (causa em apuração). Escrita com o CapCut aberto está PROIBIDA até a causa ser entendida.
        sys.exit("CapCut ABERTO: feche o CapCut inteiro e rode de novo. Nada foi gravado.")
    if na_pasta_do_capcut and os.path.exists(os.path.join(pasta, ".locked")):   # .locked = aberto no editor (vigia, 20/10)
        sys.exit("Projeto com .locked (aberto no CapCut ou o CapCut caiu com ele aberto). Nada foi gravado.")
    nome = os.path.basename(pasta)
    bk = os.path.join(BACKUPS, nome, time.strftime("%Y%m%d-%H%M%S") + "_" + re.sub(r"\W+", "-", motivo))
    os.makedirs(bk, exist_ok=True)
    backup_todos(motivo)
    for f in copias_conteudo(pasta, d) + [os.path.join(pasta, "draft_meta_info.json")]:
        if os.path.exists(f):
            rel = os.path.relpath(f, pasta).replace(os.sep, "__")
            shutil.copy2(f, os.path.join(bk, rel))
    d["duration"] = max([0] + [s["target_timerange"]["start"] + s["target_timerange"]["duration"]
                               for t in d["tracks"] for s in t["segments"]])
    garantir_voz(d)
    gravar = copy.deepcopy(d)
    tempo_das_keys(gravar, +1)
    txt = json.dumps(gravar, ensure_ascii=False, separators=(",", ":"))
    for f in copias_conteudo(pasta, d):
        for alvo in (f, f + ".bak"):
            with open(alvo, "w", encoding="utf-8") as h:
                h.write(txt)
    # draft_meta_info.json NÃO é reescrito (desde 20/10/2026): é do CapCut, e mexer nele com o CapCut aberto precedeu o sumiço do
    # 1001/1019. O card da tela inicial pode mostrar a duração antiga até o CapCut abrir o projeto.
    print("gravado (%s) · backup em %s" % (motivo, bk))


def garantir_voz(d):
    """A voz do apresentador NUNCA sai (Matheus, 22/10/2026). O esqueleto `video` veio do 1001, onde o áudio tinha sido extraído
    (`has_sound_separated: true`): todo vídeo clonado dele tocava MUDO no CapCut. Nas trilhas do motor o vídeo sempre leva o próprio som
    (camadas de efeito ficam mudas pelo volume 0, não pela extração). Trilhas do Matheus não são tocadas."""
    # o 1020 tinha 44 CÓPIAS do mesmo material (mesmo id): o motor desmutou a última e o CapCut leu a primeira (22/10/2026).
    # Cópias de id repetido saem (fica a 1ª, a que o CapCut usa) e a marca vale para todas.
    for k in ("videos", "audios"):
        vistos, unicos = set(), []
        for m in d["materials"].get(k, []):
            if m.get("id") not in vistos:
                vistos.add(m.get("id")); unicos.append(m)
        d["materials"][k] = unicos
    ids = {sg["material_id"] for t in d["tracks"] if t["type"] == "video" and t.get("name", "").startswith("Brabo · ")
           for sg in t["segments"]}
    n = 0
    for m in d["materials"].get("videos", []):
        if m["id"] not in ids:
            continue
        if m.get("has_sound_separated"):
            m["has_sound_separated"] = False; n += 1
        # 22/10/2026: só desligar has_sound_separated não trouxe a voz de volta (sem forma de onda no clipe). O material do esqueleto
        # (1001, com o som extraído) traz também extra_type_option 1 e check_flag 62978047; um import novo (pyCapCut) é 0 e 63487.
        if m.get("type") == "video" and (m.get("extra_type_option") or m.get("check_flag") != 63487):
            m["extra_type_option"] = 0; m["check_flag"] = 63487; n += 1
    # 22/10/2026 "não saiu os sons": a trilha «Brabo · SFX» voltou do CapCut com attribute 1 (= MUDA; pyCapCut: attribute = int(mute)) e
    # o material de som era o do esqueleto do 1001 (check_flag 1, music_id vazio). Trilha do motor nunca fica muda; som como import novo.
    for t in d["tracks"]:
        if t["type"] in ("audio", "video") and t.get("name", "").startswith("Brabo · ") and t.get("attribute", 0) & 1:
            if t["type"] == "audio" or any(sg.get("volume", 1) > 0 for sg in t["segments"]):
                t["attribute"] &= ~1; n += 1
    ids_a = {sg["material_id"] for t in d["tracks"] if t["type"] == "audio" and t.get("name", "").startswith("Brabo · ") for sg in t["segments"]}
    for m in d["materials"].get("audios", []):
        if m["id"] in ids_a and m.get("type") == "extract_music" and (m.get("check_flag") != 3 or m.get("music_id") != m["id"]):
            m.update({"check_flag": 3, "music_id": m["id"], "local_material_id": m["id"], "app_id": 0, "category_id": ""}); n += 1
    return n


def indice_materiais(d):
    idx = {}
    for k, v in d["materials"].items():
        if isinstance(v, list):
            for m in v:
                if isinstance(m, dict) and "id" in m:
                    idx[m["id"]] = (k, m)
    return idx


def texto_de(material):
    try:
        return json.loads(material.get("content", "")).get("text", "")
    except (ValueError, AttributeError):
        return material.get("content", "") or ""


def trilha(d, tipo, nome, recriar=True):
    """Trilha do motor por nome. recriar=True remove a anterior de mesmo nome (e seus materiais órfãos ficam; o validar avisa)."""
    for t in list(d["tracks"]):
        if t.get("name") == nome:
            if not recriar:
                return t
            d["tracks"].remove(t)
    t = {"id": novo_id(), "type": tipo, "segments": [], "flag": 0, "attribute": 0, "name": nome, "is_default_name": False}
    d["tracks"].append(t)
    return t


def limpar_orfaos(d):
    usados = set()
    for t in d["tracks"]:
        for s in t["segments"]:
            usados.add(s["material_id"])
            usados.update(s.get("extra_material_refs", []))
    n = 0
    for k, v in d["materials"].items():
        if isinstance(v, list):
            antes = len(v)
            v[:] = [m for m in v if not (isinstance(m, dict) and m.get("id") and m["id"] not in usados)]
            n += antes - len(v)
    return n


# ---------------------------------------------------------------- esqueletos (moldes capturados de rascunhos reais)
def capturar_esqueleto(d, seg, tipo_track):
    idx = indice_materiais(d)
    mats = {}
    for mid in [seg["material_id"]] + seg.get("extra_material_refs", []):
        if mid in idx:
            k, m = idx[mid]
            mats.setdefault(k, []).append(copy.deepcopy(m))
    return {"tipo_track": tipo_track, "segmento": copy.deepcopy(seg), "materiais": mats,
            "capcut": d.get("last_modified_platform", {}).get("app_version", "?"), "capturado_em": time.strftime("%Y-%m-%d %H:%M")}


def esqueleto_texto_basico():
    """Texto mínimo (formato do pyCapCut): branco, fonte padrão do CapCut, centro-baixo da zona segura. Serve para testar e para
    rascunho; o estilo de marca (Inter, verde no destaque, animação) vem do esqueleto capturado do MODELO iGreen."""
    base = ler_esqueleto("video")["segmento"]
    seg = {k: copy.deepcopy(v) for k, v in base.items() if k not in ("source_timerange", "hdr_settings")}
    seg.update({"source_timerange": None, "speed": 1.0, "volume": 1.0, "extra_material_refs": [], "common_keyframes": [],
                "material_id": "TXT", "clip": {"scale": {"x": 1.0, "y": 1.0}, "rotation": 0.0, "transform": {"x": 0.0, "y": -0.35},
                                               "flip": {"vertical": False, "horizontal": False}, "alpha": 1.0}})
    branco = {"fill": {"alpha": 1.0, "content": {"render_type": "solid", "solid": {"alpha": 1.0, "color": [0.949, 1.0, 0.941]}}},
              "range": [0, 1], "size": 8.0, "bold": True, "italic": False, "underline": False, "strokes": []}
    verde = copy.deepcopy(branco)
    verde["fill"]["content"]["solid"]["color"] = [24 / 255, 1.0, 0.0]          # #18FF00, acento iGreen (só no destaque)
    mat = {"id": "TXT", "type": "subtitle", "content": json.dumps({"styles": [branco, verde], "text": "-"}, ensure_ascii=False),
           "typesetting": 0, "alignment": 1, "letter_spacing": 0.0, "line_spacing": 0.02, "line_feed": 1, "line_max_width": 0.70,
           "force_apply_line_max_width": False, "check_flag": 7, "global_alpha": 1.0}
    return {"tipo_track": "text", "segmento": seg, "materiais": {"texts": [mat]}, "origem": "basico"}


def ler_esqueleto(nome):
    if nome == "basico":
        return esqueleto_texto_basico()
    p = nome if os.path.exists(nome) else os.path.join(ESQ_DIR, nome + ".json")
    if not os.path.exists(p):
        sys.exit("Esqueleto '%s' não existe. Capture do rascunho MODELO iGreen: capturar MODELO --texto \"...\" --como %s" % (nome, nome))
    return json.load(open(p, encoding="utf-8-sig"))


def instanciar(d, esq, inicio_us, dur_us):
    """Clona o segmento-molde + materiais com ids novos e o coloca em [inicio, inicio+dur]. Devolve (segmento, materiais)."""
    seg = copy.deepcopy(esq["segmento"])
    troca = {}
    novos = {}
    for k, lst in esq["materiais"].items():
        for m in lst:
            m2 = copy.deepcopy(m)
            troca[m["id"]] = m2["id"] = novo_id()
            novos.setdefault(k, []).append(m2)
            d["materials"].setdefault(k, []).append(m2)
    seg["id"] = novo_id()
    seg["material_id"] = troca.get(seg["material_id"], seg["material_id"])
    seg["extra_material_refs"] = [troca.get(r, r) for r in seg.get("extra_material_refs", [])]
    for ck in seg.get("common_keyframes", []) or []:
        ck["id"] = novo_id()
        for kf in ck.get("keyframe_list", []) or []:
            kf["id"] = novo_id()
    # keyframe de texto/animação ficam relativos ao começo do segmento: só encolhe a animação de saída se não couber
    seg["target_timerange"] = {"start": int(inicio_us), "duration": int(dur_us)}
    if seg.get("source_timerange") is not None and esq["tipo_track"] in ("text", "sticker", "effect", "filter"):
        seg["source_timerange"] = {"start": 0, "duration": int(dur_us)}
    return seg, novos


def u16(s):
    return len(s.encode("utf-16-le")) // 2


def trocar_texto(mat, texto, destaques=()):
    """Troca o texto preservando o estilo do molde. Estilo 0 = base; estilo 1 (se o molde tiver) = DESTAQUE (cor/fonte da palavra
    de valor). Destaques = palavras/trechos do texto que recebem o estilo 1."""
    c = json.loads(mat["content"])
    estilos = c.get("styles") or []
    base = estilos[0] if estilos else None
    dest = estilos[1] if len(estilos) > 1 else None
    c["text"] = texto
    if base is not None:
        faixas = []
        if dest is not None:
            for alvo in destaques:
                for mm in re.finditer(re.escape(alvo), texto, flags=re.I):
                    faixas.append((mm.start(), mm.end()))
        faixas.sort()
        novos, pos = [], 0
        for a, b in faixas:
            if a < pos:
                continue
            if a > pos:
                e = copy.deepcopy(base); e["range"] = [u16(texto[:pos]), u16(texto[:a])]; novos.append(e)
            e = copy.deepcopy(dest); e["range"] = [u16(texto[:a]), u16(texto[:b])]; novos.append(e)
            pos = b
        if pos < len(texto) or not novos:
            e = copy.deepcopy(base); e["range"] = [u16(texto[:pos]), u16(texto)]; novos.append(e)
        c["styles"] = novos
    mat["content"] = json.dumps(c, ensure_ascii=False)
    for k in ("recognize_text", "base_content"):
        if k in mat and isinstance(mat[k], str) and mat[k]:
            mat[k] = ""


# ---------------------------------------------------------------- mídia
def sonda(arq):
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration:stream=codec_type,width,height",
                          "-of", "json", arq], capture_output=True, text=True, encoding="utf-8")
    if out.returncode:
        sys.exit("ffprobe falhou em %s: %s" % (arq, out.stderr))
    j = json.loads(out.stdout)
    v = next((s for s in j.get("streams", []) if s.get("codec_type") == "video"), None)
    a = any(s.get("codec_type") == "audio" for s in j.get("streams", []))
    foto = os.path.splitext(arq)[1].lower() in (".png", ".jpg", ".jpeg", ".webp") or "duration" not in j.get("format", {})
    # imagem: o CapCut trata foto como mídia de 3 h (10 800 s), recortada pelo segmento
    return {"dur": 10800.0 if foto else float(j["format"]["duration"]), "w": (v or {}).get("width", 0), "h": (v or {}).get("height", 0),
            "audio": a, "video": v is not None, "foto": foto}


def material_midia(d, arq, esq):
    """Material de vídeo/áudio para o arquivo (reaproveita se o rascunho já tiver o mesmo caminho)."""
    caminho = os.path.abspath(arq).replace("\\", "/")
    for k in ("videos", "audios"):
        for m in d["materials"].get(k, []):
            if m.get("path", "").replace("\\", "/").lower() == caminho.lower():
                return m
    info = sonda(arq)
    k = "videos" if esq["tipo_track"] == "video" else "audios"
    base = copy.deepcopy(next(m for m in esq["materiais"][k] if m["id"] == esq["segmento"]["material_id"]))
    base.update({"id": novo_id(), "path": caminho, "duration": us(info["dur"])})
    if k == "videos":
        base.update({"has_sound_separated": False, "extra_type_option": 0, "check_flag": 63487})   # vídeo com o próprio som (garantir_voz)
        base.update({"width": info["w"], "height": info["h"], "has_audio": info["audio"], "material_name": os.path.basename(arq),
                     "unique_id": "", "type": "photo" if info.get("foto") else "video"})
    else:
        base.update({"name": os.path.basename(arq), "type": "extract_music", "effect_id": "", "music_id": base["id"], "check_flag": 3,
                     "local_material_id": base["id"], "app_id": 0, "category_id": "", "category_name": "local", "wave_points": []})
    d["materials"][k].append(base)
    return base


def segmento_midia(d, esq, mat, src0_us, dur_us, alvo_us):
    seg, novos = instanciar(d, {"tipo_track": esq["tipo_track"], "segmento": esq["segmento"],
                                "materiais": {k: v for k, v in esq["materiais"].items() if k not in ("videos", "audios")}},
                            alvo_us, dur_us)
    seg["material_id"] = mat["id"]
    seg["source_timerange"] = {"start": int(src0_us), "duration": int(dur_us)}
    seg["common_keyframes"] = []
    return seg


# ---------------------------------------------------------------- comandos
def cmd_listar(a):
    meta = os.path.join(DRAFTS, "root_meta_info.json")
    if not os.path.exists(meta):
        sys.exit("Sem rascunhos em %s" % DRAFTS)
    for it in sorted(json.load(open(meta, encoding="utf-8-sig"))["all_draft_store"], key=lambda x: -x.get("tm_draft_modified", 0)):
        print("%-28s %7.1f s  %s  %s" % (it["draft_name"], it.get("tm_duration", 0) / US,
                                         time.strftime("%d/%m %H:%M", time.localtime(it.get("tm_draft_modified", 0) / US)),
                                         it["draft_fold_path"]))
    print("CapCut aberto agora: %s" % ("SIM (só leitura)" if capcut_aberto() else "não"))


def cmd_raio_x(a):
    pasta, d = carregar(a[0])
    idx = indice_materiais(d)
    cv = d["canvas_config"]
    rel = {"projeto": os.path.basename(pasta), "canvas": "%sx%s %s" % (cv["width"], cv["height"], cv["ratio"]), "fps": d["fps"],
           "duracao_s": round(d["duration"] / US, 3), "trilhas": []}
    for i, t in enumerate(d["tracks"]):
        tr = {"n": i, "tipo": t["type"], "nome": t.get("name", ""), "segmentos": []}
        for s in t["segments"]:
            k, m = idx.get(s["material_id"], ("?", {}))
            tt = s["target_timerange"]
            item = {"id": s["id"], "de": round(tt["start"] / US, 3), "ate": round((tt["start"] + tt["duration"]) / US, 3)}
            if k == "texts":
                item["texto"] = texto_de(m)
            else:
                item["material"] = m.get("material_name") or m.get("name") or os.path.basename(m.get("path", "")) or k
            if s.get("source_timerange"):
                item["fonte"] = [round(s["source_timerange"]["start"] / US, 3),
                                 round((s["source_timerange"]["start"] + s["source_timerange"]["duration"]) / US, 3)]
            cl = s.get("clip") or {}
            if cl:
                item["pos"] = [round(cl["transform"]["x"], 3), round(cl["transform"]["y"], 3)]
                item["escala"] = round(cl["scale"]["x"], 3)
            if s.get("volume") not in (None, 1.0):
                item["volume"] = round(s["volume"], 3)
            if s.get("speed") not in (None, 1.0):
                item["velocidade"] = s["speed"]
            ks = s.get("common_keyframes") or []
            if ks:
                item["keyframes"] = {ck.get("property_type"): [round(kf.get("time_offset", 0) / US, 3) for kf in ck.get("keyframe_list", [])]
                                     for ck in ks}
            anims = [idx[r][1] for r in s.get("extra_material_refs", []) if r in idx and idx[r][0] == "material_animations"]
            nomes = [an.get("name") or an.get("type") for x in anims for an in x.get("animations", [])]
            if nomes:
                item["animacoes"] = nomes
            efs = [idx[r][1].get("name") for r in s.get("extra_material_refs", []) if r in idx and idx[r][0] in ("transitions", "effects", "video_effects")]
            if efs:
                item["efeitos"] = efs
            tr["segmentos"].append(item)
        rel["trilhas"].append(tr)
    if "--json" in a:
        json.dump(rel, open(a[a.index("--json") + 1], "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("%s · %s · %s fps · %.2f s" % (rel["projeto"], rel["canvas"], rel["fps"], rel["duracao_s"]))
    if d.get("time_marks"):                  # marcadores que o Matheus pôs na timeline (a "pinça" do CapCut)
        print("MARCADORES:", json.dumps(d["time_marks"], ensure_ascii=False)[:2000])
    for tr in rel["trilhas"]:
        print("\n[%d] %s %s (%d)" % (tr["n"], tr["tipo"], ("«%s»" % tr["nome"]) if tr["nome"] else "", len(tr["segmentos"])))
        for it in tr["segmentos"][:60]:
            extra = {k: v for k, v in it.items() if k not in ("id", "de", "ate", "texto", "material")}
            print("  %7.2f–%7.2f  %s  %s  #%s" % (it["de"], it["ate"], it.get("texto") or it.get("material"),
                                                 json.dumps(extra, ensure_ascii=False) if extra else "", it["id"][:8]))
        if len(tr["segmentos"]) > 60:
            print("  … +%d segmentos (use --json)" % (len(tr["segmentos"]) - 60))


def cmd_capturar(a):
    pasta, d = carregar(a[0])
    como = a[a.index("--como") + 1]
    idx = indice_materiais(d)
    alvo = None
    for t in d["tracks"]:
        for s in t["segments"]:
            if "--segmento" in a and s["id"].startswith(a[a.index("--segmento") + 1]):
                alvo = (s, t["type"])
            if "--texto" in a:
                k, m = idx.get(s["material_id"], ("", {}))
                if k == "texts" and texto_de(m).strip().lower() == a[a.index("--texto") + 1].strip().lower():
                    alvo = (s, t["type"])
    if not alvo:
        sys.exit("Segmento não achado. Rode raio-x e confira o texto/ID.")
    os.makedirs(ESQ_DIR, exist_ok=True)
    if "--curva" in a:                       # guarda a curva do 1º key do segmento (curva personalizada feita no CapCut)
        kfs = [k for ck in alvo[0].get("common_keyframes", []) for k in ck.get("keyframe_list", [])]
        if not kfs:
            sys.exit("Esse segmento não tem keyframe.")
        p = os.path.join(ESQ_DIR, como + ".json")
        json.dump(kfs[0], open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        print("curva '%s' salva (%s) → %s" % (como, kfs[0].get("curveType"), p))
        return
    esq = capturar_esqueleto(d, alvo[0], alvo[1])
    esq["origem"] = os.path.basename(pasta)
    os.makedirs(ESQ_DIR, exist_ok=True)
    p = os.path.join(ESQ_DIR, como + ".json")
    json.dump(esq, open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    estilos = ""
    if alvo[1] == "text":
        c = json.loads(esq["materiais"]["texts"][0]["content"])
        estilos = " · %d estilo(s) de texto (2º = destaque)" % len(c.get("styles", []))
    print("esqueleto '%s' salvo de %s (%s)%s → %s" % (como, esq["origem"], alvo[1], estilos, p))


def cmd_cortes(a):
    pasta, d = carregar(a[0])
    edl = [e for e in json.load(open(a[1], encoding="utf-8-sig")) if e.get("clip")]
    midia = a[a.index("--midia") + 1]
    nome = a[a.index("--trilha") + 1] if "--trilha" in a else "Brabo · Cortes"
    esq = ler_esqueleto("video")

    def arquivo(clip):
        if os.path.isfile(midia):
            return midia
        c = [f for f in glob.glob(os.path.join(midia, "*")) if os.path.splitext(os.path.basename(f))[0].lower() == clip.lower()
             and os.path.splitext(f)[1].lower() in (".mp4", ".mov", ".mkv", ".m4v", ".mxf")]
        if not c:
            sys.exit("Vídeo do clip %s não achado em %s" % (clip, midia))
        return c[0]

    t = trilha(d, "video", nome)
    pos = 0
    for e in edl:
        mat = material_midia(d, arquivo(e["clip"]), esq)
        dur = us(e["ate"]) - us(e["de"])
        t["segments"].append(segmento_midia(d, esq, mat, us(e["de"]), dur, pos))
        pos += dur
    # a trilha de cortes vira a principal (primeira de vídeo), como no CapCut
    d["tracks"].remove(t)
    d["tracks"].insert(0, t)
    n = limpar_orfaos(d)
    salvar(pasta, d, "cortes")
    print("%d cortes · %.2f s na trilha «%s» (%d materiais órfãos limpos)" % (len(edl), pos / US, nome, n))


def cmd_paginar(a):
    """Palavras (JSON do whisper --word_timestamps, ou lista [{word,start,end}]) → páginas de legenda por frase."""
    j = json.load(open(a[0], encoding="utf-8-sig"))
    pal = j if isinstance(j, list) else [w for s in j.get("segments", []) for w in s.get("words", [])]
    pal = [{"w": w["word"].strip(), "s": float(w["start"]), "e": float(w["end"])} for w in pal if w["word"].strip()]
    junto = []                                # o whisper separa "lembre -se", "tratar -se", "100 %": cola na palavra anterior
    for w in pal:
        if junto and (w["w"].startswith("-") or w["w"] in ("%", "%.", "%,")):
            junto[-1]["w"] += w["w"]; junto[-1]["e"] = w["e"]
        else:
            junto.append(dict(w))
    pal = junto
    if "--edl" in a:                          # tempo do bruto → tempo da montagem
        edl = [e for e in json.load(open(a[a.index("--edl") + 1], encoding="utf-8-sig")) if e.get("clip")]
        out, pos = [], 0.0
        for e in edl:
            for w in pal:
                meio = (w["s"] + w["e"]) / 2
                if e["de"] <= meio <= e["ate"]:
                    out.append({"w": w["w"], "s": max(pos, pos + w["s"] - e["de"]), "e": min(pos + e["ate"] - e["de"], pos + w["e"] - e["de"])})
            pos += e["ate"] - e["de"]
        pal = out
    dest = [x.strip().lower() for x in (a[a.index("--destaques") + 1].split(",") if "--destaques" in a else []) if x.strip()]
    lim = lambda w: re.sub(r"[^\wà-ú%$]", "", w.lower())
    n = len(pal)
    INF = 1e9
    custo = [INF] * (n + 1); custo[0] = 0; prev = [0] * (n + 1)
    for i in range(1, n + 1):
        for k in range(3, 8):                 # 3–7 palavras por página
            j0 = i - k
            if j0 < 0:
                break
            c = custo[j0] + abs(k - 5)
            fim = pal[i - 1]["w"]
            if lim(fim) in NAO_TERMINA:
                c += 6
            if re.search(r"[.!?…]$", fim):
                c -= 2
            elif re.search(r"[,;:]$", fim):
                c -= 1
            if i < n and pal[i]["s"] - pal[i - 1]["e"] > 0.35:
                c -= 2                        # pausa natural fecha página
            elif i < n and not re.search(r"[.!?…,;:]$", fim) and pal[i]["s"] - pal[i - 1]["e"] < 0.12:
                c += 2                        # fala corrida no meio da expressão ("carteira / ativa"): não fecha aqui
            if pal[i - 1]["e"] - pal[j0]["s"] < 0.8:
                c += 4                        # página que fica < 0,8 s na tela não dá para ler
            if any(re.search(r"[.!?]$", pal[x]["w"]) for x in range(j0, i - 1)):
                c += 4                        # frase terminando no meio da página
            if c < custo[i]:
                custo[i], prev[i] = c, j0
        if custo[i] == INF and i < 3:
            custo[i], prev[i] = custo[0] + 10, 0
    cortes, i = [], n
    while i > 0:
        cortes.append((prev[i], i)); i = prev[i]
    paginas = []
    for j0, i in reversed(cortes):
        ws = pal[j0:i]
        texto = re.sub(r"\s+([,.!?;:…])", r"\1", " ".join(w["w"] for w in ws))
        d_ = [w["w"].strip(",.!?;:…") for w in ws if lim(w["w"]) in dest]
        paginas.append({"t0": round(ws[0]["s"], 3), "t1": round(ws[-1]["e"], 3), "texto": texto, "destaque": d_,
                        "palavras": [[w["w"], round(w["s"], 3), round(w["e"], 3)] for w in ws]})
    for p, q in zip(paginas, paginas[1:]):    # página fica até a próxima (sem buraco curto) e nunca encosta
        if q["t0"] - p["t1"] < 0.6:
            p["t1"] = round(q["t0"] - 0.001, 3)
    o = a[a.index("-o") + 1] if "-o" in a else "paginas.json"
    json.dump(paginas, open(o, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    soz = [p["texto"] for p in paginas if len(p["texto"].split()) < 2]
    print("%d páginas → %s%s" % (len(paginas), o, ("  ATENÇÃO palavra sozinha: %s" % soz) if soz else ""))


def cmd_legendas(a):
    pasta, d = carregar(a[0])
    paginas = json.load(open(a[1], encoding="utf-8-sig"))
    esq = ler_esqueleto(a[a.index("--esqueleto") + 1] if "--esqueleto" in a else "legenda")
    nome = a[a.index("--trilha") + 1] if "--trilha" in a else "Brabo · Legenda"
    y = float(a[a.index("--y") + 1]) if "--y" in a else None
    t = trilha(d, esq["tipo_track"], nome)
    for p in paginas:
        seg, novos = instanciar(d, esq, us(p["t0"]), us(p["t1"]) - us(p["t0"]))
        trocar_texto(novos["texts"][0], p["texto"], p.get("destaque") or [])
        if y is not None and seg.get("clip"):
            seg["clip"]["transform"]["y"] = y
        t["segments"].append(seg)
    n = limpar_orfaos(d)
    salvar(pasta, d, "legendas")
    print("%d legendas na trilha «%s» (%d órfãos limpos)" % (len(paginas), nome, n))


def cmd_audio(a):
    """audio <proj> <arquivo> --em 3.2 [--volume 0.4]      (acrescenta um som)
    audio <proj> --lote sons.json                          (RECRIA as trilhas "Brabo · SFX…": [{arquivo, em, volume}])"""
    pasta, d = carregar(a[0])
    nome = a[a.index("--trilha") + 1] if "--trilha" in a else "Brabo · SFX"
    esq = ler_esqueleto("audio")
    if "--lote" in a:
        base = os.path.dirname(os.path.abspath(a[a.index("--lote") + 1]))
        lote = json.load(open(a[a.index("--lote") + 1], encoding="utf-8-sig"))
        for x in [x for x in d["tracks"] if (x.get("name") or "").startswith(nome)]:
            d["tracks"].remove(x)
    else:
        base = os.getcwd()
        lote = [{"arquivo": a[1], "em": float(a[a.index("--em") + 1]),
                 "volume": float(a[a.index("--volume") + 1]) if "--volume" in a else 1.0}]
    for som in sorted(lote, key=lambda s: s["em"]):
        arq = som["arquivo"] if os.path.isabs(som["arquivo"]) else os.path.join(base, som["arquivo"])
        mat = material_midia(d, arq, esq)
        em = us(som["em"]); fim = em + mat["duration"]
        seg = segmento_midia(d, esq, mat, 0, mat["duration"], em)
        seg["volume"] = float(som.get("volume", 1.0))
        livre = lambda tr: all(fim <= s["target_timerange"]["start"] or em >= s["target_timerange"]["start"] + s["target_timerange"]["duration"]
                               for s in tr["segments"])
        t = next((x for x in d["tracks"] if (x.get("name") or "").startswith(nome) and livre(x)), None)
        if not t:
            n = sum(1 for x in d["tracks"] if (x.get("name") or "").startswith(nome))
            t = trilha(d, "audio", nome if n == 0 else "%s %d" % (nome, n + 1), recriar=False)
        t["segments"].append(seg)
        t["segments"].sort(key=lambda s: s["target_timerange"]["start"])
    limpar_orfaos(d)
    salvar(pasta, d, "audio")
    print("%d som(ns) nas trilhas «%s…»" % (len(lote), nome))


FORMATOS = {"9:16": (1080, 1920), "16:9": (1920, 1080), "4:5": (1080, 1350), "1:1": (1080, 1080)}


def cmd_formato(a):
    """Proporção da tela do projeto (o CapCut cria 9:16 ou "original"; aula/YouTube = 16:9, feed = 4:5)."""
    pasta, d = carregar(a[0])
    if len(a) < 2 or a[1] not in FORMATOS:
        sys.exit("Formatos: %s" % ", ".join(FORMATOS))
    w, h = FORMATOS[a[1]]
    d["canvas_config"].update({"ratio": a[1], "width": w, "height": h})
    salvar(pasta, d, "formato")
    print("tela %s (%dx%d)" % (a[1], w, h))


def trilha_por_nome(d, nome):
    t = next((x for x in d["tracks"] if x.get("name") == nome), None)
    if not t:
        sys.exit("Trilha «%s» não existe (raio-x mostra os nomes)." % nome)
    return t


def cmd_punch(a):
    """Zoom de corte (jump zoom) do talking head: alterna a escala dos cortes (1,00 / 1,12…) sem keyframe. --rosto-y = altura do
    olho no quadro (normalizado, 0 = centro, + = acima): o corte ampliado desloca para o olho ficar no mesmo lugar."""
    pasta, d = carregar(a[0])
    t = trilha_por_nome(d, a[a.index("--trilha") + 1] if "--trilha" in a else "Brabo · Cortes")
    esc = float(a[a.index("--escala") + 1]) if "--escala" in a else 1.12
    cada = int(a[a.index("--a-cada") + 1]) if "--a-cada" in a else 2
    ry = float(a[a.index("--rosto-y") + 1]) if "--rosto-y" in a else 0.0
    rx = float(a[a.index("--rosto-x") + 1]) if "--rosto-x" in a else 0.0
    n = 0
    for i, s in enumerate(sorted(t["segments"], key=lambda s: s["target_timerange"]["start"])):
        e = esc if i % cada == cada - 1 else 1.0
        s["clip"]["scale"] = {"x": e, "y": e}
        s["clip"]["transform"]["x"] = rx * (1.0 - e)
        s["clip"]["transform"]["y"] = ry * (1.0 - e)
        n += e != 1.0
    salvar(pasta, d, "punch")
    print("%d de %d cortes em %.0f %%" % (n, len(t["segments"]), esc * 100))


# ---------------------------------------------------------------- animação por keyframe (curvas do Editor Brabo)
# Curvas da casa (After: keyframe velocity, velocidade 0) como cubic-bezier: influência de SAÍDA = x1, de CHEGADA = 1 − x2.
CURVAS = {"cam65": (0.65, 0.0, 0.35, 1.0), "cam65_100": (0.65, 0.0, 0.0, 1.0), "cam40_100": (0.40, 0.0, 0.0, 1.0),
          "cam100_10": (1.0, 0.0, 0.90, 1.0), "linear": (0.0, 0.0, 1.0, 1.0)}
QUADRO = US / 30.0
PASSO_Q = 2          # o CapCut só interpola linear entre keys: a curva é amostrada a cada 2 quadros (15 keys/s)
# propriedades de keyframe no JSON do CapCut (escala uniforme = KFTypeScaleX com uniform_scale ligado, como o pyCapCut faz)
KF = {"escala": "KFTypeScaleX", "x": "KFTypePositionX", "y": "KFTypePositionY", "rot": "KFTypeRotation", "alfa": "KFTypeAlpha"}


def bezier(c, x):
    """y da cubic-bezier(c) para o progresso de tempo x (0–1), por bisseção em t."""
    if x <= 0 or x >= 1:
        return 0.0 if x <= 0 else 1.0
    x1, y1, x2, y2 = c
    bx = lambda t: 3 * (1 - t) ** 2 * t * x1 + 3 * (1 - t) * t ** 2 * x2 + t ** 3
    by = lambda t: 3 * (1 - t) ** 2 * t * y1 + 3 * (1 - t) * t ** 2 * y2 + t ** 3
    lo, hi = 0.0, 1.0
    for _ in range(40):
        m = (lo + hi) / 2
        lo, hi = (m, hi) if bx(m) < x else (lo, m)
    return by((lo + hi) / 2)


def pontos(t0, t1, v0, v1, curva="cam65"):
    """[(tempo_us, valor)] de t0 a t1 seguindo a curva (keys a cada PASSO_Q quadros + o último exato)."""
    c = CURVAS[curva]
    n = max(1, int(round((t1 - t0) / (QUADRO * PASSO_Q))))
    return [(int(round(t0 + (t1 - t0) * i / n)), v0 + (v1 - v0) * bezier(c, i / n)) for i in range(n + 1)]


def por_keys(seg, prop, pts):
    """Grava/acrescenta keys de uma propriedade no segmento (tempo relativo ao começo do segmento). Mesmo tempo: fica a última."""
    tipo = KF.get(prop, prop)
    lst = seg.setdefault("common_keyframes", [])
    k = next((x for x in lst if x.get("property_type") == tipo), None)
    if not k:
        k = {"id": novo_id(), "keyframe_list": [], "material_id": "", "property_type": tipo}
        lst.append(k)
    porT = {kf["time_offset"]: kf for kf in k["keyframe_list"]}
    for tt, v in pts:
        porT[int(round(tt))] = {"curveType": "Line", "graphID": "", "left_control": {"x": 0.0, "y": 0.0},
                         "right_control": {"x": 0.0, "y": 0.0}, "id": novo_id(), "time_offset": int(round(tt)), "values": [float(v)]}
    k["keyframe_list"] = [porT[x] for x in sorted(porT)]
    if prop == "escala":
        seg["uniform_scale"] = {"on": True, "value": 1.0}


def segmento_em(t, em):
    return next((s for s in t["segments"] if s["target_timerange"]["start"] <= em < s["target_timerange"]["start"] + s["target_timerange"]["duration"]), None)


def aplicar_zoom(t, z):
    """z = {em, dur, para, curva, rosto_x, rosto_y, volta}: a escala do corte vai de onde está até 'para' mantendo o rosto no lugar
    (transform = rosto × (1 − escala)); segura até o fim do corte (ou volta depois de 'volta' s). Devolve o segmento."""
    em = us(z["em"])
    s = segmento_em(t, em)
    if not s:
        return None
    ini = s["target_timerange"]["start"]; fim = ini + s["target_timerange"]["duration"]
    e0 = s["clip"]["scale"]["x"]
    e1 = e0 * float(z["fator"]) if "fator" in z else float(z.get("para", 1.15))     # fator: relativo ao punch do corte
    rx, ry = float(z.get("rosto_x", 0.0)), float(z.get("rosto_y", 0.0))
    a = em - ini
    b = min(fim - ini, a + us(z.get("dur", 0.4)))
    pts = pontos(a, b, e0, e1, z.get("curva", "cam65_100"))
    if a > 0:
        pts = [(0, e0)] + pts
    por_keys(s, "escala", pts)
    por_keys(s, "x", [(tt, rx * (1 - v)) for tt, v in pts])
    por_keys(s, "y", [(tt, ry * (1 - v)) for tt, v in pts])
    if z.get("volta"):
        c = min(fim - ini, b + us(z["volta"]))
        pv = pontos(c - us(0.35), c, e1, e0, "cam65")
        por_keys(s, "escala", pv)
        por_keys(s, "x", [(tt, rx * (1 - v)) for tt, v in pv])
        por_keys(s, "y", [(tt, ry * (1 - v)) for tt, v in pv])
    return s


def cmd_zoom(a):
    """Zoom de impacto por keyframe (curva da casa amostrada):
      zoom <proj> --em 56.4 [--dur 0.4] [--para 1.18] [--curva cam65_100] [--rosto-x -0.04] [--rosto-y 0.52] [--volta 1.5]
      zoom <proj> --lote zooms.json      (lista de {em, dur, para, curva, rosto_x, rosto_y, volta})"""
    pasta, d = carregar(a[0])
    t = trilha_por_nome(d, a[a.index("--trilha") + 1] if "--trilha" in a else "Brabo · Cortes")
    if "--lote" in a:
        lote = json.load(open(a[a.index("--lote") + 1], encoding="utf-8-sig"))
        # o lote é a lista COMPLETA de zooms da trilha: limpa os keys de escala/posição antes (rodar de novo não acumula)
        for s in t["segments"]:
            s["common_keyframes"] = [k for k in (s.get("common_keyframes") or [])
                                     if k.get("property_type") not in (KF["escala"], KF["x"], KF["y"])]
    else:
        g = lambda k, pad: a[a.index(k) + 1] if k in a else pad
        lote = [{"em": float(g("--em", 0)), "dur": float(g("--dur", 0.4)), "para": float(g("--para", 1.15)),
                 "curva": g("--curva", "cam65_100"), "rosto_x": float(g("--rosto-x", 0)), "rosto_y": float(g("--rosto-y", 0)),
                 "volta": float(g("--volta", 0)) or None}]
    ok = 0
    for z in lote:
        if aplicar_zoom(t, z):
            ok += 1
        else:
            print("AVISO: nenhum corte em %.2f s" % z["em"])
    salvar(pasta, d, "zoom")
    print("%d zoom(s) com curva amostrada a cada %d quadros" % (ok, PASSO_Q))


# ---------------------------------------------------------------- letreiros (lettering) animados
CORES = {"branco": [0.949, 1.0, 0.941], "verde": [24 / 255, 1.0, 0.0], "verde_fundo_claro": [11 / 255, 122 / 255, 0.0],
         "tinta": [0.071, 0.075, 0.09], "cinza": [0.725, 0.788, 0.714]}
# Marca: cópia exata dos oficiais em <repo>/marca/ (vai no Git); na máquina do Matheus também existe iGreen.SYS\07_Marca-Assets
MARCA = os.path.join(RAIZ_SISTEMA, "marca")
FONTES_MARCA = os.path.abspath(os.path.join(RAIZ_SISTEMA, "..", "..", "07_Marca-Assets", "Marketing", "Inter", "static"))
# Inter da marca com os contornos unidos (fonte_limpa.py): a estática original tem contornos sobrepostos e o CapCut desenhava emendas
# (risco na haste do D, riscos no A, "texto recortado" — Matheus, 22/10/2026). Mesmo desenho, texto continua editável.
FONTES_LIMPAS = os.path.join(RAIZ_SISTEMA, "Aprendizados-SYS", "fontes", "Inter-limpa")
FONTES = FONTES_LIMPAS if os.path.isdir(FONTES_LIMPAS) else FONTES_MARCA
PESO = {"medio": "Inter_18pt-SemiBold.ttf", "bold": "Inter_18pt-Bold.ttf", "titulo": "Inter_18pt-ExtraBold.ttf",
        "impacto": "Inter_18pt-Black.ttf"}


# tamanho do CapCut → px: 1 unidade = 9,07 px de "em" num quadro de 1080 de altura (medido no 1020, 20/10/2026: "DÓLAR" tam. 21,5
# = 683 px; "CARTEIRA" tam. 12,5 = 597 px). Em 9:16 ainda não medido (o motor usa a mesma regra pela altura do quadro; conferir).
EM_POR_TAMANHO = 9.07
MARGEM = 0.05            # fração da largura do quadro que o letreiro nunca invade


def largura_letreiro(partes, alt_quadro):
    """Largura (px) do bloco: a maior linha, somando as partes de cada linha com a fonte/tamanho de cada uma (PIL + Inter)."""
    try:
        from PIL import ImageFont
    except ImportError:
        return None
    linhas, atual = [], 0.0
    for p in partes:
        f = os.path.join(FONTES, PESO.get(p.get("peso", "titulo"), PESO["titulo"]))
        fonte = ImageFont.truetype(f, max(1, int(round(EM_POR_TAMANHO * float(p.get("tamanho", 12)) * alt_quadro / 1080))))
        pedacos = p["texto"].split("\n")
        for i, ped in enumerate(pedacos):
            atual += fonte.getlength(ped)
            if i < len(pedacos) - 1:
                linhas.append(atual); atual = 0.0
    linhas.append(atual)
    return max(linhas)


def cabe_no_lado(it, W, H):
    """Letreiro lateral não passa da faixa livre (`max_larg`, fração da largura; padrão 0,34 = o lado de fora do rosto num plano
    centrado): reduz todos os tamanhos na mesma proporção. Devolve o fator aplicado."""
    if it.get("alinhar", "centro") == "centro":
        return 1.0
    larg = largura_letreiro(it["partes"], H)
    lim = float(it.get("max_larg", 0.34)) * W
    if not larg or larg <= lim:
        return 1.0
    f = lim / larg
    for p in it["partes"]:
        p["tamanho"] = round(float(p.get("tamanho", 12)) * f, 2)
    return f


def encaixa_x(it, W, H):
    """x do centro para o bloco alinhado à esquerda/direita ficar inteiro dentro da margem (20/10: "ESTADOS UNIDOS" saía cortado)."""
    al = it.get("alinhar", "centro")
    larg = largura_letreiro(it["partes"], H)
    x = float(it.get("x", 0))
    if larg is None:
        return x
    meia = 1.08 * larg / 2 / (W / 2)             # meia largura (com a folga do pico de 108 % do pop) em unidades de meia tela
    lim = 1 - 2 * MARGEM
    if al == "esquerda":
        return round(-lim + meia, 4) if x - meia < -lim or it.get("encostar", True) else x
    if al == "direita":
        return round(lim - meia, 4) if x + meia > lim or it.get("encostar", True) else x
    return round(max(-lim + meia, min(lim - meia, x)), 4)


def estilo(base, ini, fim, parte):
    e = copy.deepcopy(base)
    e["range"] = [ini, fim]
    e["size"] = float(parte.get("tamanho", 12))
    e["bold"] = False
    cor = parte.get("cor", "branco")
    rgb = CORES[cor] if isinstance(cor, str) else [c / 255 for c in cor]
    e["fill"] = {"alpha": 1.0, "content": {"render_type": "solid", "solid": {"alpha": 1.0, "color": rgb}}}
    f = os.path.join(FONTES, PESO.get(parte.get("peso", "titulo"), PESO["titulo"]))
    if os.path.exists(f):
        e["font"] = {"id": "", "path": f.replace("\\", "/")}
    else:
        e["bold"] = True
    return e


def teto_escala(it, W, H):
    """Maior escala que o bloco aguenta sem nenhuma letra sair da margem (5 %), pela posição e largura/altura medidas.
    20/10/2026: a entrada 'zoom' (1,6×) jogava os blocos largos do texto atrás para fora da tela."""
    larg = largura_letreiro(it["partes"], H)
    if not larg:
        return 1.08
    linhas = max(1, sum(p["texto"].count("\n") for p in it["partes"]) + 1)
    alt = linhas * 1.25 * EM_POR_TAMANHO * max(float(p.get("tamanho", 12)) for p in it["partes"]) * H / 1080
    cx = W / 2 + float(it.get("x", 0)) * W / 2
    cy = H / 2 - float(it.get("y", 0)) * H / 2
    mx, my = MARGEM * W, MARGEM * H
    t = min((cx - mx) / (larg / 2), (W - mx - cx) / (larg / 2), (cy - my) / (alt / 2), (H - my - cy) / (alt / 2))
    return max(1.0, round(t, 3))


def animar_texto(seg, dur_us, anim, saida=True, teto=1.6):
    """Entradas da casa: 'pop' (escala 0 → 108 % em 8 q cam65_100 → 100 % em 6 q: o pop de 3 keys do After), 'sobe' (sobe 0,06
    + escala 0,94 → 1 em 10 q cam65_100), 'zoom' (min(1,6, teto) → 1 em 12 q cam40_100). Saída em 6 q terminando no fim do segmento.
    `teto` = maior escala sem sair da tela (teto_escala): o pico do pop e o início do zoom nunca passam dele."""
    q = QUADRO
    y0 = seg["clip"]["transform"]["y"]
    if anim == "pop":
        pico = min(1.08, teto)
        por_keys(seg, "escala", pontos(0, 8 * q, 0.0, pico, "cam65_100") + pontos(8 * q, 14 * q, pico, 1.0, "cam65")[1:])
    elif anim == "sobe":
        por_keys(seg, "escala", pontos(0, 10 * q, 0.94, 1.0, "cam65_100"))
        por_keys(seg, "y", pontos(0, 10 * q, y0 - 0.06, y0, "cam65_100"))
        por_keys(seg, "alfa", pontos(0, 6 * q, 0.0, 1.0, "linear"))
    elif anim == "zoom":
        ini = min(1.6, teto)
        if ini < 1.15:                     # sem espaço para crescer: entra encolhendo de leve + aparecendo (não sai da tela)
            por_keys(seg, "escala", pontos(0, 12 * q, 0.92, 1.0, "cam40_100"))
        else:
            por_keys(seg, "escala", pontos(0, 12 * q, ini, 1.0, "cam40_100"))
        por_keys(seg, "alfa", pontos(0, 6 * q, 0.0, 1.0, "linear"))
    if saida and dur_us > 30 * q:
        e = dur_us - 7 * q
        por_keys(seg, "escala", [(e - q, 1.0)] + pontos(e, dur_us - q, 1.0, 0.0 if anim == "pop" else 0.9, "cam65"))
        if anim != "pop":
            por_keys(seg, "alfa", [(e, 1.0)] + pontos(e, dur_us - q, 1.0, 0.0, "linear"))


def cmd_letreiros(a):
    """letreiros <proj> letreiros.json [--trilha "Brabo · Letreiros"]
    Item: {t0, t1, x, y, alinhar: esquerda|centro|direita, anim: pop|sobe|zoom, saida: true,
           partes: [{texto, tamanho, cor: branco|verde|tinta|cinza|[r,g,b], peso: medio|bold|titulo|impacto}]}
    As partes viram UM texto com vários estilos (linha nova = "\\n" dentro do texto). Itens sobrepostos vão para trilhas extras."""
    pasta, d = carregar(a[0])
    itens = json.load(open(a[1], encoding="utf-8-sig"))
    nome = a[a.index("--trilha") + 1] if "--trilha" in a else "Brabo · Letreiros"
    for x in [x for x in d["tracks"] if (x.get("name") or "").startswith(nome)]:
        d["tracks"].remove(x)
    esq = esqueleto_texto_basico()
    trilhas = []
    for it in sorted(itens, key=lambda i: i["t0"]):
        t0, t1 = us(it["t0"]), us(it["t1"])
        cabe_no_lado(it, d["canvas_config"]["width"], d["canvas_config"]["height"])   # nunca invade o rosto (20/10)
        tr = next((x for x in trilhas if x["segments"][-1]["target_timerange"]["start"]
                   + x["segments"][-1]["target_timerange"]["duration"] <= t0), None)
        if not tr:
            tr = trilha(d, "text", nome if not trilhas else "%s %d" % (nome, len(trilhas) + 1))
            trilhas.append(tr)
        seg, novos = instanciar(d, esq, t0, t1 - t0)
        mat = novos["texts"][0]
        c = json.loads(mat["content"]); base = c["styles"][0]
        texto, estilos = "", []
        for parte in it["partes"]:
            ini = u16(texto); texto += parte["texto"]
            estilos.append(estilo(base, ini, u16(texto), parte))
        c["text"], c["styles"] = texto, estilos
        mat["content"] = json.dumps(c, ensure_ascii=False)
        mat["alignment"] = {"esquerda": 0, "centro": 1, "direita": 2}[it.get("alinhar", "centro")]
        mat["type"] = "text"
        mat["line_max_width"] = 0.9
        mat["line_spacing"] = float(it.get("entrelinha", 0.02))
        seg["clip"]["transform"] = {"x": encaixa_x(it, d["canvas_config"]["width"], d["canvas_config"]["height"]), "y": float(it.get("y", 0))}
        seg["common_keyframes"] = []
        if it.get("efeito"):                    # efeito de texto nativo do CapCut (desfoque, ampliar, brilho…) no lugar das keys
            ef = it["efeito"]
            anim_nativa(d, seg, ef.get("entrada"), ef.get("saida") if it.get("saida", True) else None, ef.get("dur_entrada"), ef.get("dur_saida"))
        else:
            animar_texto(seg, t1 - t0, it.get("anim", "pop"), it.get("saida", True),
                         teto_escala(dict(it, x=seg["clip"]["transform"]["x"]), d["canvas_config"]["width"], d["canvas_config"]["height"]))
        tr["segments"].append(seg)
    n = limpar_orfaos(d)
    salvar(pasta, d, "letreiros")
    print("%d letreiros em %d trilha(s) «%s…» (%d órfãos limpos)" % (len(itens), len(trilhas), nome, n))


# ---------------------------------------------------------------- texto ATRÁS da pessoa
def valor_em(keys, t):
    """valor interpolado (linear, como o CapCut) de uma lista de keys no tempo t (µs relativo ao segmento)."""
    ks = sorted(keys, key=lambda k: k["time_offset"])
    if t <= ks[0]["time_offset"]:
        return ks[0]["values"][0]
    for a, b in zip(ks, ks[1:]):
        if a["time_offset"] <= t <= b["time_offset"]:
            f = (t - a["time_offset"]) / max(1, b["time_offset"] - a["time_offset"])
            return a["values"][0] + (b["values"][0] - a["values"][0]) * f
    return ks[-1]["values"][0]


def recorta_keys(cks, off, dur):
    """keys do segmento-base vistas a partir de 'off' (µs), dentro de 'dur': o recorte da pessoa anda junto com o zoom do corte."""
    novos = []
    for ck in cks or []:
        ks = ck.get("keyframe_list") or []
        if not ks:
            continue
        pts = [(0, valor_em(ks, off))] + [(k["time_offset"] - off, k["values"][0]) for k in ks if off < k["time_offset"] < off + dur]
        pts.append((dur, valor_em(ks, off + dur)))
        novos.append({"id": novo_id(), "material_id": "", "property_type": ck["property_type"],
                      "keyframe_list": [{"curveType": "Line", "graphID": "", "left_control": {"x": 0.0, "y": 0.0},
                                         "right_control": {"x": 0.0, "y": 0.0}, "id": novo_id(), "time_offset": int(t),
                                         "values": [float(v)]} for t, v in pts]})
    return novos


def montar_letreiro(d, esq, it):
    """segmento de texto de um item no formato dos letreiros (partes/estilos/fonte/animação). Devolve o segmento."""
    t0, t1 = us(it["t0"]), us(it["t1"])
    seg, novos = instanciar(d, esq, t0, t1 - t0)
    mat = novos["texts"][0]
    c = json.loads(mat["content"]); base = c["styles"][0]
    texto, estilos = "", []
    for parte in it["partes"]:
        ini = u16(texto); texto += parte["texto"]
        estilos.append(estilo(base, ini, u16(texto), parte))
    c["text"], c["styles"] = texto, estilos
    mat["content"] = json.dumps(c, ensure_ascii=False)
    mat["alignment"] = {"esquerda": 0, "centro": 1, "direita": 2}[it.get("alinhar", "centro")]
    mat["type"] = "text"
    mat["line_max_width"] = float(it.get("largura", 0.9))
    mat["line_spacing"] = float(it.get("entrelinha", 0.02))
    seg["clip"]["transform"] = {"x": float(it.get("x", 0)), "y": float(it.get("y", 0))}
    seg["common_keyframes"] = []
    if it.get("efeito"):
        ef = it["efeito"]
        anim_nativa(d, seg, ef.get("entrada"), ef.get("saida") if it.get("saida", True) else None, ef.get("dur_entrada"), ef.get("dur_saida"))
    else:
        animar_texto(seg, t1 - t0, it.get("anim", "pop"), it.get("saida", True),
                     teto_escala(it, d["canvas_config"]["width"], d["canvas_config"]["height"]))
    return seg


def cmd_atras(a):
    """atras <proj> atras.json --midia <pasta_dos_brutos>
    Item = item de letreiro (t0, t1, partes, x, y, alinhar, anim) — normalmente GIGANTE e centrado atrás da cabeça.
    Para cada item: letreiro na trilha «Brabo · Atrás texto» + a pessoa recortada (MODNet, recorte_pessoa.py, .mov com alfa) na
    trilha «Brabo · Atrás pessoa», no mesmo tempo, com a escala/posição/keys do corte de baixo e volume 0. Ordem das camadas:
    vídeo → texto atrás → pessoa → legenda e letreiros (estes continuam por cima). Recortes ficam em <pasta do json>/recortes/."""
    pasta, d = carregar(a[0])
    itens = json.load(open(a[1], encoding="utf-8-sig"))
    midia = a[a.index("--midia") + 1]
    dir_rec = os.path.join(os.path.dirname(os.path.abspath(a[1])), "recortes")
    os.makedirs(dir_rec, exist_ok=True)
    base_t = trilha_por_nome(d, a[a.index("--trilha") + 1] if "--trilha" in a else "Brabo · Cortes")
    for nome in ("Brabo · Atrás texto", "Brabo · Atrás pessoa"):
        for x in [x for x in d["tracks"] if x.get("name") == nome]:
            d["tracks"].remove(x)
    tt = {"id": novo_id(), "type": "text", "segments": [], "flag": 0, "attribute": 0, "name": "Brabo · Atrás texto", "is_default_name": False}
    tp = {"id": novo_id(), "type": "video", "segments": [], "flag": 0, "attribute": 0, "name": "Brabo · Atrás pessoa", "is_default_name": False}
    i = d["tracks"].index(base_t)
    d["tracks"][i + 1:i + 1] = [tt, tp]
    esq_txt, esq_vid = esqueleto_texto_basico(), ler_esqueleto("video")
    idx = indice_materiais(d)
    for it in sorted(itens, key=lambda x: x["t0"]):
        # no quadro da timeline: o CapCut põe o segmento no quadro, e o recorte (src0) e as keys têm que sair do MESMO instante,
        # senão a pessoa recortada fica meio quadro atrás do vídeo e a máscara "mexe" (22/10/2026)
        t0 = int(round(round(it["t0"] * 30) * QUADRO))
        it = dict(it, t0=t0 / US)
        s = segmento_em(base_t, t0)
        if not s:
            print("AVISO: nenhum corte em %.2f s" % it["t0"]); continue
        fim_seg = s["target_timerange"]["start"] + s["target_timerange"]["duration"]
        t1 = min(us(it["t1"]), fim_seg)
        it = dict(it, t1=t1 / US)
        off = t0 - s["target_timerange"]["start"]
        vel = s.get("speed") or 1.0
        src0 = s["source_timerange"]["start"] + off * vel
        bruto = idx[s["material_id"]][1]["path"]
        if not os.path.exists(bruto):
            bruto = os.path.join(midia, os.path.basename(bruto))
        mov = os.path.join(dir_rec, "atras_%07.2f.mov" % it["t0"])
        if not os.path.exists(mov):
            subprocess.run([sys.executable, "-I", os.path.join(AQUI, "recorte_pessoa.py"), bruto, "%.4f" % (src0 / US),
                            "%.4f" % ((src0 + (t1 - t0) * vel) / US), mov], check=True)
        tt["segments"].append(montar_letreiro(d, esq_txt, it))
        mat = material_midia(d, mov, esq_vid)
        dur = min(t1 - t0, mat["duration"])
        seg = segmento_midia(d, esq_vid, mat, 0, dur, t0)
        seg["clip"] = copy.deepcopy(s["clip"])
        seg["uniform_scale"] = copy.deepcopy(s.get("uniform_scale") or {"on": True, "value": 1.0})
        seg["common_keyframes"] = recorta_keys(s.get("common_keyframes"), off, dur)
        seg["volume"] = 0.0
        seg["last_nonzero_volume"] = 1.0
        tp["segments"].append(seg)
    n = limpar_orfaos(d)
    salvar(pasta, d, "atras")
    print("%d texto(s) atrás da pessoa · camadas: vídeo → texto → pessoa recortada → legenda/letreiros (%d órfãos limpos)"
          % (len(tt["segments"]), n))


# ---------------------------------------------------------------- legenda estilo Apple (revelação palavra a palavra no lugar)
def faixas_palavras(texto, palavras):
    """[(ini, fim)] em UTF-16 de cada palavra da página dentro do texto montado pelo paginar."""
    out, cur = [], 0
    for w in palavras:
        p = texto.find(w, cur)
        if p < 0:
            p = texto.lower().find(w.lower(), cur)
        if p < 0:
            out.append(None); continue
        out.append((u16(texto[:p]), u16(texto[:p + len(w)])))
        cur = p + len(w)
    return out


def estilos_revelados(base, dest, texto, faixas, visiveis, destaques):
    """Estilos do texto inteiro: palavras já faladas visíveis, as próximas com alfa 0 (o layout não muda quando a palavra entra)."""
    marca = [False] * u16(texto)
    for alvo in destaques:
        for mm in re.finditer(re.escape(alvo), texto, flags=re.I):
            for i in range(u16(texto[:mm.start()]), u16(texto[:mm.end()])):
                marca[i] = True
    vis = [False] * u16(texto)
    for k, f in enumerate(faixas):
        if f and k < visiveis:
            for i in range(f[0], len(vis) if k == len(faixas) - 1 else f[1]):
                vis[i] = True
        if f and k == visiveis - 1:            # pontuação colada na palavra visível também aparece
            j = f[1]
            while j < len(vis) and texto[j:j + 1] in ",.!?;:…":
                vis[j] = True; j += 1
    estilos, ini = [], 0
    chave = lambda i: (vis[i], marca[i])
    for i in range(1, len(vis) + 1):
        if i == len(vis) or chave(i) != chave(ini):
            e = copy.deepcopy(dest if (marca[ini] and dest is not None) else base)
            e["range"] = [ini, i]
            a = 1.0 if vis[ini] else 0.0
            e.setdefault("fill", {"alpha": 1.0, "content": {"render_type": "solid", "solid": {"alpha": 1.0, "color": [1, 1, 1]}}})
            e["fill"]["alpha"] = a
            e["fill"]["content"].setdefault("solid", {"alpha": 1.0, "color": [1, 1, 1]})["alpha"] = a
            for k in ("strokes", "shadows"):
                for s in e.get(k) or []:
                    if isinstance(s, dict) and "alpha" in s:
                        s["alpha"] = s["alpha"] * a
            estilos.append(e)
            ini = i
    return estilos


def cmd_legenda_apple(a):
    """legenda-apple <proj> paginas.json [--esqueleto legenda|basico] [--y -0.62] [--antes 0.1]
    Para cada página: um segmento por palavra falada; cada um mostra a página inteira com as palavras já ditas visíveis (as próximas com
    alfa 0), então cada palavra APARECE NO LUGAR no seu tempo. A página entra com escala 106 → 100 % e sobe 16 px (8 q cam65_100) e sai
    em 6 q (escala 100 → 98 %, alfa → 0) — a parte "Apple" que o motor faz. O blur 24 → 0 da palavra é animação nativa: capturar.
    Recria a trilha «Brabo · Legenda»."""
    pasta, d = carregar(a[0])
    paginas = json.load(open(a[1], encoding="utf-8-sig"))
    esq = ler_esqueleto(a[a.index("--esqueleto") + 1] if "--esqueleto" in a else "basico")
    y = float(a[a.index("--y") + 1]) if "--y" in a else None
    antes = us(float(a[a.index("--antes") + 1]) if "--antes" in a else 0.1)   # a palavra aparece 3 q antes do som (WTC)
    nome = a[a.index("--trilha") + 1] if "--trilha" in a else "Brabo · Legenda"
    t = trilha(d, esq["tipo_track"], nome)
    q = QUADRO
    n = 0
    for p in paginas:
        pal = p.get("palavras") or [[w, p["t0"], p["t1"]] for w in p["texto"].split()]
        texto = p["texto"]
        faixas = faixas_palavras(texto, [w[0] for w in pal])
        T0, T1 = us(p["t0"]), us(p["t1"])
        inicios = [max(T0, us(w[1]) - antes) for w in pal]
        inicios[0] = T0
        for k in range(len(pal)):
            s0 = inicios[k]
            s1 = inicios[k + 1] if k + 1 < len(pal) else T1
            if s1 - s0 < q:                       # palavra colada na anterior: entra junto
                continue
            seg, novos = instanciar(d, esq, s0, s1 - s0)
            if k > 0:      # animação nativa do esqueleto (ex.: entrada com desfoque) só no 1º segmento da página, senão a página pisca a cada palavra
                anims = {m["id"] for m in novos.get("material_animations", [])}
                seg["extra_material_refs"] = [r for r in seg.get("extra_material_refs", []) if r not in anims]
            mat = novos["texts"][0]
            c = json.loads(mat["content"]); base = c["styles"][0]; dest = c["styles"][1] if len(c["styles"]) > 1 else None
            c["text"] = texto
            vis = max(i + 1 for i in range(len(pal)) if inicios[i] <= s0)
            c["styles"] = estilos_revelados(base, dest, texto, faixas, vis, p.get("destaque") or [])
            mat["content"] = json.dumps(c, ensure_ascii=False)
            if y is not None:
                seg["clip"]["transform"]["y"] = y
            seg["common_keyframes"] = []
            y0 = seg["clip"]["transform"]["y"]
            if k == 0:                                # entrada da página
                por_keys(seg, "escala", pontos(0, 8 * q, 1.06, 1.0, "cam65_100"))
                por_keys(seg, "y", pontos(0, 8 * q, y0 - 0.03, y0, "cam65_100"))
                por_keys(seg, "alfa", pontos(0, 5 * q, 0.0, 1.0, "linear"))
            if k == len(pal) - 1 and s1 - s0 > 10 * q:  # saída da página
                e = s1 - s0 - 6 * q
                por_keys(seg, "escala", [(e, 1.0)] + pontos(e, s1 - s0 - q, 1.0, 0.98, "linear")[1:])
                por_keys(seg, "alfa", [(e, 1.0)] + pontos(e, s1 - s0 - q, 1.0, 0.0, "linear")[1:])
            t["segments"].append(seg)
            n += 1
    lim = limpar_orfaos(d)
    salvar(pasta, d, "legenda-apple")
    print("%d páginas · %d segmentos (palavra a palavra) na trilha «%s» (%d órfãos limpos)" % (len(paginas), n, nome, lim))


# ---------------------------------------------------------------- tremida e flash no corte (transição de impacto)
def cmd_tremida(a):
    """tremida <proj> --em <tempo do corte> [--amount 43] [--sobe 16] [--desce 14]
    Receita do After: Amount 0 → pico no quadro do corte (subida em 16 q) → 0 (14 q); posição ±a·1,5 px (x, 10 Hz) e ±a·0,6 px (y),
    escala até +8 % no pico para a borda não aparecer. Keys quadro a quadro somados ao enquadramento do corte. Pode repetir com --em várias
    vezes separado por vírgula. Um por virada de bloco (1–2 por vídeo)."""
    pasta, d = carregar(a[0])
    t = trilha_por_nome(d, a[a.index("--trilha") + 1] if "--trilha" in a else "Brabo · Cortes")
    amt = float(a[a.index("--amount") + 1]) if "--amount" in a else 43.0
    sobe = int(a[a.index("--sobe") + 1]) if "--sobe" in a else 16
    desce = int(a[a.index("--desce") + 1]) if "--desce" in a else 14
    W = d["canvas_config"]["width"]; H = d["canvas_config"]["height"]
    q = QUADRO
    for em_s in a[a.index("--em") + 1].split(","):
        corte = us(float(em_s))
        for f in range(-sobe, desce + 1):
            tt = corte + f * q
            s = segmento_em(t, int(tt))
            if not s:
                continue
            env = (sobe + f) / sobe if f < 0 else (1 - f / desce)
            env = max(0.0, env) ** (2 if f < 0 else 1.5)   # spike: sobe acelerando, cai rápido (whipOut/whipIn liberados em efeito)
            am = amt * env
            sec = tt / US
            dx = am * 1.5 * math.sin(2 * math.pi * 10 * sec) / (W / 2)
            dy = am * 0.6 * math.cos(2 * math.pi * 8.5 * sec) / (H / 2)
            off = int(round(tt - s["target_timerange"]["start"]))
            e0 = s["clip"]["scale"]["x"]
            ks = {k["property_type"]: k["keyframe_list"] for k in s.get("common_keyframes") or []}
            ex = valor_em(ks[KF["escala"]], off) if KF["escala"] in ks else e0
            bx = valor_em(ks[KF["x"]], off) if KF["x"] in ks else s["clip"]["transform"]["x"]
            by = valor_em(ks[KF["y"]], off) if KF["y"] in ks else s["clip"]["transform"]["y"]
            por_keys(s, "escala", [(off, ex * (1 + 0.08 * env))])
            por_keys(s, "x", [(off, bx + dx)])
            por_keys(s, "y", [(off, by + dy)])
    salvar(pasta, d, "tremida")
    print("tremida em %s (amount %.0f, %d/%d q)" % (a[a.index("--em") + 1], amt, sobe, desce))


def solido(cor, W, H):
    """MP4 de 2 s numa cor (o flash). Fica em Aprendizados-SYS/sons/../solidos."""
    pasta = os.path.join(RAIZ_SISTEMA, "Aprendizados-SYS", "solidos")
    os.makedirs(pasta, exist_ok=True)
    f = os.path.join(pasta, "solido_%s_%dx%d.mp4" % (cor.strip("#"), W, H))
    if not os.path.exists(f):
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i", "color=c=%s:s=%dx%d:r=30:d=2" % (cor, W, H),
                        "-c:v", "libx264", "-pix_fmt", "yuv420p", f], check=True)
    return f


def cmd_flash(a):
    """flash <proj> --em <tempo do corte>[,...] [--cor white] [--pico 0.5] [--curva 0.5,1,1,0.85,0.6,0.35,0.15,0]
    Sólido na cor com opacidade quadro a quadro a partir do corte (padrão: sobe 1 q antes, pico 3 q, cai 5 q — ranking do After). Alto
    padrão = pico 0,10–0,15; marca forte 0,35–0,6. Flash creme da construtora: --cor #E4D080 --curva 0.85,0.81,0.77,0.71,0.64,0.55,0.40,0.21,0.05,0 --pico 1.
    Trilha «Brabo · Flash» logo acima do vídeo (abaixo de legenda e letreiros). Rodar de novo recria a trilha."""
    pasta, d = carregar(a[0])
    cor = a[a.index("--cor") + 1] if "--cor" in a else "white"
    pico = float(a[a.index("--pico") + 1]) if "--pico" in a else 0.5
    curva = [float(x) for x in (a[a.index("--curva") + 1] if "--curva" in a else "0.5,1,1,1,0.85,0.6,0.35,0.15,0").split(",")]
    W = d["canvas_config"]["width"]; H = d["canvas_config"]["height"]
    arq = solido(cor, W, H)
    for x in [x for x in d["tracks"] if x.get("name") == "Brabo · Flash"]:
        d["tracks"].remove(x)
    tf = {"id": novo_id(), "type": "video", "segments": [], "flag": 0, "attribute": 0, "name": "Brabo · Flash", "is_default_name": False}
    ref = next((x for x in d["tracks"] if x.get("name") == "Brabo · Atrás pessoa"), None) or next(x for x in d["tracks"] if x["type"] == "video")
    d["tracks"].insert(d["tracks"].index(ref) + 1, tf)
    esq = ler_esqueleto("video")
    q = QUADRO
    for em_s in a[a.index("--em") + 1].split(","):
        t0 = us(float(em_s)) - int(q)
        dur = int(round(len(curva) * q))
        mat = material_midia(d, arq, esq)
        seg = segmento_midia(d, esq, mat, 0, dur, t0)
        seg["volume"] = 0.0
        por_keys(seg, "alfa", [(int(round(i * q)), v * pico) for i, v in enumerate(curva)])
        tf["segments"].append(seg)
    tf["segments"].sort(key=lambda s: s["target_timerange"]["start"])
    salvar(pasta, d, "flash")
    print("flash %s em %s (pico %.2f, %d q)" % (cor, a[a.index("--em") + 1], pico, len(curva)))


# ---------------------------------------------------------------- CÂMERA medida nos renders aprovados do After
# Fichas: Aprendizados-SYS/06-referencias/CAMERA-*.md (ANTARES, D HAUSS, SANTORINI, ARANTES; erro 0,01–2,7 % contra os builds).
# A câmera 3D do After anda em DISTÂNCIA: o que segue a curva é 1/escala → s(t) = 1/(1/s0 + y(t)·(1/s1 − 1/s0)).
def fator_t(t, t0, dur, f0, f1, curva):
    if t <= t0:
        return f0
    if t >= t0 + dur:
        return f1
    y = bezier(CURVAS[curva], (t - t0) / dur)
    return 1.0 / (1.0 / f0 + y * (1.0 / f1 - 1.0 / f0))


def cmd_camera(a):
    """camera <proj> camera.json   — câmera inteira da trilha principal, no jeito do After:
      {"rosto": [-0.045, 0.59],            olho em meia tela (âncora fixa: posição = rosto × (1 − escala))
       "deriva": 0.05,                     toda fala anda +5 % no corte (cam65) — "a fala nunca fica parada"
       "salto": 1.22, "salto_q": 5,        corte na MESMA tomada = zoom IN que FICA ×1,22 em 5 q30 (cam40_100), nunca volta
       "teto": 1.6,                        teto do salto acumulado (corta a cabeça acima disso)
       "blocos": [0, 51.067, ...],         cortes que abrem bloco novo (assunto novo) = "tomada nova": volta à base
       "base": 1.0,
       "gancho": {"fator": 1.5, "q": 27.5},              abertura: começa ampliado e abre (cam40_100)
       "enfases": [{"em": 57.86, "fator": 1.16}],         push de ênfase ×1,16 em 17,5 q30 cam65_100, começa 5 q30 ANTES da palavra
       "outs": [{"em": 219.167, "fator": 0.85}]}          zoom OUT com motivo, 12,5 q30 cam40_100 (o bloco nasce em 1/fator)
    Limpa punch/zoom antigos da trilha e escreve escala + posição a cada 2 quadros. Rodar ANTES de tremida e de atras."""
    pasta, d = carregar(a[0])
    cfg = json.load(open(a[1], encoding="utf-8-sig"))
    t = trilha_por_nome(d, cfg.get("trilha", "Brabo · Cortes"))
    rx, ry = cfg.get("rosto", [0.0, 0.0])
    q = QUADRO
    deriva = float(cfg.get("deriva", 0.05)); salto = float(cfg.get("salto", 1.22)); salto_q = float(cfg.get("salto_q", 5))
    teto = float(cfg.get("teto", 1.6)); base = float(cfg.get("base", 1.0))
    blocos = [us(x) for x in cfg.get("blocos", [])]
    enf = [(us(e["em"]), float(e.get("fator", 1.16))) for e in cfg.get("enfases", [])]
    outs = [(us(o["em"]), float(o.get("fator", 0.85))) for o in cfg.get("outs", [])]
    ganc = cfg.get("gancho")
    segs = sorted(t["segments"], key=lambda s: s["target_timerange"]["start"])
    fim_ant = None
    resumo = []
    for i, s in enumerate(segs):
        ini = s["target_timerange"]["start"]; dur = s["target_timerange"]["duration"]
        s["common_keyframes"] = [k for k in (s.get("common_keyframes") or []) if k.get("property_type") not in (KF["escala"], KF["x"], KF["y"])]
        novo_bloco = i == 0 or any(abs(ini - b) < 60_000 for b in blocos)
        if not novo_bloco and fim_ant is not None and fim_ant * salto > teto + 1e-6:
            novo_bloco = True          # bateu no teto: o corte seguinte vira "tomada nova" (volta à base) — aula longa de uma tomada só
        out_aqui = [(em - ini, f) for em, f in outs if ini - 60_000 <= em < ini + dur]
        if novo_bloco or fim_ant is None:
            L = base / min([f for _, f in out_aqui] or [1.0])          # bloco com zoom out nasce ampliado e abre
            j0 = 1.0
        else:
            L = min(teto, fim_ant * salto)
            j0 = fim_ant / L                                            # salto animado: começa onde o corte anterior terminou
        fatores = []
        if j0 != 1.0:
            fatores.append((0, salto_q * q, j0, 1.0, "cam40_100"))
        if i == 0 and ganc:
            fatores.append((0, float(ganc.get("q", 27.5)) * q, float(ganc.get("fator", 1.5)), 1.0, "cam40_100"))
        for em, f in enf:
            if ini <= em < ini + dur:
                fatores.append((em - ini - 5 * q, 17.5 * q, 1.0, f, "cam65_100"))
        for rel, f in out_aqui:
            fatores.append((max(0, rel), 12.5 * q, 1.0, f, "cam40_100"))
        def esc(tt):
            v = L * fator_t(tt, 0, dur, 1.0, 1.0 + deriva, "cam65")
            for t0, du, f0, f1, cv in fatores:
                v *= fator_t(tt, t0, du, f0, f1, cv)
            return max(1.0, min(teto * 1.2, v))
        marcas = {0, dur}
        for t0, du, *_ in fatores:
            marcas.update({max(0, min(dur, t0)), max(0, min(dur, t0 + du))})
        n = max(1, int(dur / (PASSO_Q * q)))
        tempos = sorted(marcas | {int(dur * k / n) for k in range(n + 1)})
        pts = [(tt, esc(tt)) for tt in tempos]
        por_keys(s, "escala", pts)
        por_keys(s, "x", [(tt, rx * (1 - v)) for tt, v in pts])
        por_keys(s, "y", [(tt, ry * (1 - v)) for tt, v in pts])
        s["clip"]["scale"] = {"x": pts[0][1], "y": pts[0][1]}
        s["clip"]["transform"] = {"x": rx * (1 - pts[0][1]), "y": ry * (1 - pts[0][1])}
        fim_ant = pts[-1][1]
        resumo.append("%7.2f %s %.2f→%.2f%s" % (ini / US, "BLOCO" if novo_bloco else "salto", pts[0][1], fim_ant,
                                               " +" + ",".join("%.2f" % f1 for _, _, _, f1, _ in fatores if f1 != 1.0) if fatores else ""))
    salvar(pasta, d, "camera")
    print("\n".join(resumo[:60]))
    print("câmera em %d cortes (deriva %+.0f %%, salto ×%.2f, teto %.2f, %d ênfases, %d outs)" % (len(segs), deriva * 100, salto, teto, len(enf), len(outs)))


# ---------------------------------------------------------------- pílula de vidro atrás da legenda 16:9 (assinatura da Capa iGreen)
def pilula_png(larg, alt, pasta):
    """PNG da pílula (medidas da Capa: véu #050F0A a 46 %, raio = altura/2, fio branco 1 px a 16 %). Cache por tamanho."""
    from PIL import Image, ImageDraw
    os.makedirs(pasta, exist_ok=True)
    larg = int(round(larg / 4) * 4); alt = int(alt)
    f = os.path.join(pasta, "pilula_%dx%d.png" % (larg, alt))
    if not os.path.exists(f):
        k = 4                                                     # supersampling para a borda lisa
        im = Image.new("RGBA", (larg * k, alt * k), (0, 0, 0, 0))
        dr = ImageDraw.Draw(im)
        dr.rounded_rectangle([0, 0, larg * k - 1, alt * k - 1], radius=alt * k // 2, fill=(5, 15, 10, int(255 * 0.46)),
                             outline=(255, 255, 255, int(255 * 0.16)), width=k)
        im.resize((larg, alt), Image.LANCZOS).save(f)
    return f, larg


# ---------------------------------------------------------------- legenda dinâmica POR PALAVRA (o jeito do After, medido nos renders)
# Fonte: Aprendizados-SYS/06-referencias/LEGENDA-APPLE-DO-AFTER.md — Capa iGreen 16:9 (`2026-09-25_legenda_sol.jsx`, render q3655–3733)
# e fórmula 9:16 (`formula_reels.jsx` FR.legenda, Arantes q195–235). A página nasce diagramada inteira; cada PALAVRA acende no lugar no
# quadro em que é falada; a página sai inteira em 6 q. (Antes eu animava a página: errado — a animação é por palavra.)
LEG_PERFIL = {
    "16:9": {"px": 32, "peso": "Inter_18pt-Medium.ttf", "cor": [1.0, 1.0, 1.0], "y_px": 918, "larg_max": 1200, "passo": 1.3,
             # entrada 6 q, cubicOut: opacidade e subida de 7 px (blur 9→0 = animação nativa a capturar)
             "alfa": [0, 0.42, 0.70, 0.88, 0.96, 1.0], "dy_px": [7, 4.1, 2.1, 0.9, 0.3, 0.0], "esc": None, "saida_q": 6},
    "9:16": {"px": 52, "peso": "Inter_18pt-Medium.ttf", "cor": [0.953, 0.953, 0.953], "y_fim_px": 1400, "larg_max": 760, "passo": 66 / 52,
             # entrada 8 q, cam65_100: y +16→0, escala 106→100, opacidade linear em 5 q (blur 24→0 = animação nativa)
             "alfa": [0, 0.2, 0.4, 0.6, 0.8, 1.0], "dy_px": None, "esc": None, "saida_q": 6},
}


def _quebra_linhas(larguras, espaco, palavras, larg_max):
    """1 linha se couber; senão 2 linhas equilibradas, sem terminar a 1ª em palavra de ligação nem deixar palavra sozinha."""
    total = sum(larguras) + espaco * (len(larguras) - 1)
    if total <= larg_max or len(larguras) < 4:
        return [list(range(len(larguras)))]
    melhor = None
    for k in range(2, len(larguras) - 1):
        a = sum(larguras[:k]) + espaco * (k - 1); b = sum(larguras[k:]) + espaco * (len(larguras) - k - 1)
        custo = abs(a - b) + (700 if re.sub(r"[^\wà-ú]", "", palavras[k - 1].lower()) in NAO_TERMINA else 0) - (120 if re.search(r"[,.;:!?]$", palavras[k - 1]) else 0)
        if max(a, b) > larg_max:
            custo += 2000
        if melhor is None or custo < melhor[0]:
            melhor = (custo, k)
    k = melhor[1]
    return [list(range(k)), list(range(k, len(larguras)))]


def cmd_legenda_palavras(a):
    """legenda-palavras <proj> paginas.json [--px 32] [--y-px 918]
    Um segmento de texto por PALAVRA, no x/y final da página diagramada (Inter Medium medida com PIL), aparecendo no início da palavra
    falada com a entrada medida no After (16:9: 6 q opacidade 0→42→70→88→96→100 % + sobe 7 px; 9:16: 8 q cam65_100, +16 px, 106→100 %,
    opacidade em 5 q) e saindo com a página inteira nos 6 q antes da próxima. Destaque da página na cor de destaque (#18FF00).
    Trilhas «Brabo · Legenda 1…N» (uma por posição de palavra na página; recria todas)."""
    from PIL import ImageFont
    pasta, d = carregar(a[0])
    paginas = json.load(open(a[1], encoding="utf-8-sig"))
    W, H = d["canvas_config"]["width"], d["canvas_config"]["height"]
    perfil = dict(LEG_PERFIL["9:16" if H > W else "16:9"])
    if "--px" in a: perfil["px"] = float(a[a.index("--px") + 1])
    if "--y-px" in a: perfil["y_px"] = float(a[a.index("--y-px") + 1])
    for x in [x for x in d["tracks"] if (x.get("name") or "").startswith("Brabo · Legenda")]:
        d["tracks"].remove(x)
    fonte_arq = os.path.join(FONTES, perfil["peso"])
    fonte = ImageFont.truetype(fonte_arq, int(round(perfil["px"])))
    tam = perfil["px"] / (EM_POR_TAMANHO * H / 1080)          # tamanho do CapCut que dá esse px de "em"
    esq = esqueleto_texto_basico()
    q = QUADRO
    trilhas = {}
    n = 0
    for x in [x for x in d["tracks"] if x.get("name") == "Brabo · Pílula"]:
        d["tracks"].remove(x)
    pil, fim_pil = None, 0
    if ("--sem-pilula" not in a) and W > H:                       # pílula só no 16:9 (no 9:16 a fórmula não tem pílula)
        pil = trilha(d, "video", "Brabo · Pílula")
        esq_v = ler_esqueleto("video")
    for pi, p in enumerate(paginas):
        pal = p.get("palavras") or [[w, p["t0"], p["t1"]] for w in p["texto"].split()]
        palavras = [w[0] for w in pal]
        larg = [fonte.getlength(w) for w in palavras]
        esp = fonte.getlength(" ")
        linhas = _quebra_linhas(larg, esp, palavras, perfil["larg_max"])
        passo = perfil["px"] * perfil["passo"]
        if "y_fim_px" in perfil:                               # 9:16: o bloco TERMINA em y 1400
            y_base = perfil["y_fim_px"] - passo * (len(linhas) - 1) - perfil["px"] * 0.5
        else:                                                  # 16:9: centro do bloco em y 918
            y_base = perfil["y_px"] - passo * (len(linhas) - 1) / 2
        dest = {x.strip(",.!?;:…").lower() for x in (p.get("destaque") or [])}
        T1 = us(p["t1"])
        for li, idxs in enumerate(linhas):
            tot = sum(larg[i] for i in idxs) + esp * (len(idxs) - 1)
            xcur = W / 2 - tot / 2
            ypx = y_base + li * passo
            for i in idxs:
                cx = xcur + larg[i] / 2
                xcur += larg[i] + esp
                t0w = max(us(p["t0"]), us(pal[i][1]))
                if T1 - t0w < 2 * q:
                    t0w = T1 - int(2 * q)
                seg, novos = instanciar(d, esq, t0w, T1 - t0w)
                mat = novos["texts"][0]
                c = json.loads(mat["content"]); e = copy.deepcopy(c["styles"][0])
                cor = CORES["verde"] if palavras[i].strip(",.!?;:…").lower() in dest else perfil["cor"]
                e.update({"range": [0, u16(palavras[i])], "size": round(tam, 3), "bold": False,
                          "fill": {"alpha": 1.0, "content": {"render_type": "solid", "solid": {"alpha": 1.0, "color": cor}}},
                          "font": {"id": "", "path": fonte_arq.replace("\\", "/")}})
                c["text"], c["styles"] = palavras[i], [e]
                mat["content"] = json.dumps(c, ensure_ascii=False)
                mat.update({"type": "text", "alignment": 1, "line_max_width": 1.0})
                y_norm = (H / 2 - ypx) / (H / 2)
                seg["clip"]["transform"] = {"x": round((cx - W / 2) / (W / 2), 5), "y": round(y_norm, 5)}
                seg["common_keyframes"] = []
                dur = T1 - t0w
                # entrada da palavra
                if perfil["dy_px"]:
                    por_keys(seg, "y", [(int(round(k * q)), y_norm - dy / (H / 2)) for k, dy in enumerate(perfil["dy_px"])])
                else:
                    por_keys(seg, "y", pontos(0, 8 * q, y_norm - 16 / (H / 2), y_norm, "cam65_100"))
                    por_keys(seg, "escala", pontos(0, 8 * q, 1.06, 1.0, "cam65_100"))
                por_keys(seg, "alfa", [(int(round(k * q)), v) for k, v in enumerate(perfil["alfa"])])
                # saída da página (todas as palavras juntas), terminando no fim da página
                sq = perfil["saida_q"]
                if dur > (len(perfil["alfa"]) + sq + 2) * q:
                    ini_s = dur - sq * q
                    por_keys(seg, "alfa", [(int(round(ini_s - q)), 1.0)] + [(int(round(ini_s + k * q)), 1 - k / sq) for k in range(1, sq + 1)])
                pos_na_pag = sum(len(l) for l in linhas[:li]) + idxs.index(i)
                tr = trilhas.get(pos_na_pag)
                if tr is None:
                    tr = trilha(d, "text", "Brabo · Legenda %d" % (pos_na_pag + 1))
                    trilhas[pos_na_pag] = tr
                tr["segments"].append(seg)
                n += 1
        if pil is not None:                                        # pílula de vidro da página (Capa: altura 62, largura = frase + 2×34)
            larg_bloco = max(sum(larg[i] for i in idxs) + esp * (len(idxs) - 1) for idxs in linhas)
            alt_p = perfil["px"] * 62 / 32 + passo * (len(linhas) - 1)
            png, larg_png = pilula_png(larg_bloco + 2 * 34 * perfil["px"] / 32, alt_p, os.path.join(RAIZ_SISTEMA, "Aprendizados-SYS", "pilulas"))
            e_png = larg_png / W          # o CapCut AJUSTA a imagem à largura do quadro: escala = largura real / largura da tela (20/10)
            yc = y_base + passo * (len(linhas) - 1) / 2
            t0p = max(us(p["t0"]), us(pal[0][1])) - int(4 * q)
            t0p = max(t0p, fim_pil)
            if T1 - t0p > 6 * q:
                matp = material_midia(d, png, esq_v)
                sp = segmento_midia(d, esq_v, matp, 0, T1 - t0p, t0p)
                sp["volume"] = 0.0
                sp["clip"]["transform"] = {"x": 0.0, "y": round((H / 2 - yc) / (H / 2), 5)}
                sp["clip"]["scale"] = {"x": e_png, "y": e_png}
                du = T1 - t0p
                por_keys(sp, "alfa", pontos(0, 8 * q, 0.0, 1.0, "linear") + ([(du - 5 * q, 1.0)] + pontos(du - 4 * q, du - q, 1.0, 0.0, "linear") if du > 20 * q else []))
                por_keys(sp, "escala", pontos(0, 10 * q, 0.94 * e_png, e_png, "cam65"))
                pil["segments"].append(sp)
                fim_pil = T1
    lim = limpar_orfaos(d)
    salvar(pasta, d, "legenda-palavras")
    print("%d páginas · %d palavras em %d trilhas «Brabo · Legenda N» · %s %.0f px (tamanho CapCut %.2f) (%d órfãos limpos)"
          % (len(paginas), n, len(trilhas), "9:16" if H > W else "16:9", perfil["px"], tam, lim))


# ---------------------------------------------------------------- efeitos de texto nativos do CapCut (animação de entrada/saída)
# IDs da biblioteca do CapCut (metadados do pyCapCut, migrados do Jianying; só os GRATUITOS). Conferir no CapCut: se um não carregar,
# o texto aparece sem animação (não quebra). Nome → (título na biblioteca, effect_id = resource_id, duração padrão s).
EFEITO_ENTRADA = {
    "desfoque": ("模糊", "6923135604519604737", 0.5),        # sai do blur (o "Apple" da casa)
    "ampliar": ("放大", "6724919499042066958", 0.5),         # cresce do pequeno
    "surgir": ("渐显", "6724916044072227332", 0.5),          # fade
    "pular": ("向上弹入", "7145435451946439170", 0.5),       # pop subindo
    "brilho": ("辉光入场", "7529389011673124113", 0.5),      # entra com glow
    "varredura": ("扫光入场", "7532793713785916673", 0.5),   # faixa de luz passando
}
EFEITO_SAIDA = {
    "desfoque": ("模糊", "6923134492760609282", 0.4),
    "sumir": ("渐隐", "6724919382104871427", 0.4),
    "encolher": ("缩小", "7428455252141100293", 0.4),
    "brilho": ("辉光渐隐", "7529376407676275969", 0.4),
}


def anim_nativa(d, seg, entrada=None, saida=None, dur_ent=None, dur_sai=None):
    """Põe no segmento de texto a animação nativa (material_animations do tipo sticker_animation, como o CapCut grava)."""
    dur = seg["target_timerange"]["duration"]
    lst = []
    if entrada:
        nome, eid, pad = EFEITO_ENTRADA[entrada]
        de = min(us(dur_ent or pad), dur // 2)
        lst.append({"anim_adjust_params": None, "platform": "all", "panel": "", "material_type": "sticker", "name": nome,
                    "id": eid, "type": "in", "resource_id": eid, "start": 0, "duration": de})
    if saida:
        nome, eid, pad = EFEITO_SAIDA[saida]
        ds = min(us(dur_sai or pad), dur // 3)
        lst.append({"anim_adjust_params": None, "platform": "all", "panel": "", "material_type": "sticker", "name": nome,
                    "id": eid, "type": "out", "resource_id": eid, "start": dur - ds, "duration": ds})
    if not lst:
        return
    m = {"id": novo_id(), "type": "sticker_animation", "multi_language_current": "none", "animations": lst}
    d["materials"].setdefault("material_animations", []).append(m)
    seg["extra_material_refs"] = [r for r in seg.get("extra_material_refs", [])
                                  if indice_materiais(d).get(r, ("",))[0] != "material_animations"] + [m["id"]]


def cmd_tirar(a):
    """tirar <proj> "Brabo · Legenda" ["Brabo · Pílula" …]   — remove as trilhas do motor cujo nome COMEÇA com cada prefixo.
    Só trilhas "Brabo · …" (as do Matheus nunca)."""
    pasta, d = carregar(a[0])
    pref = [p for p in a[1:] if p.startswith("Brabo · ")]
    if len(pref) != len(a[1:]):
        sys.exit("Só trilhas do motor (nome começando com 'Brabo · ').")
    fora = [t.get("name") for t in d["tracks"] if any((t.get("name") or "").startswith(p) for p in pref)]
    d["tracks"] = [t for t in d["tracks"] if t.get("name") not in fora]
    n = limpar_orfaos(d)
    salvar(pasta, d, "tirar")
    print("%d trilha(s) removida(s): %s (%d materiais órfãos limpos)" % (len(fora), ", ".join(fora) or "nenhuma", n))


def cmd_religar(a):
    """religar <proj> --de "C:/Users/iGreen/Desktop/iGreen.SYS" --para "D:/iGreen.SYS"
    Troca o prefixo de caminho em TODO o rascunho (mídia, recortes, sons, fontes dos textos) — pastas mudadas de disco (21/10/2026)."""
    pasta, d = carregar(a[0])
    de = a[a.index("--de") + 1].replace("\\", "/").rstrip("/")
    para = a[a.index("--para") + 1].replace("\\", "/").rstrip("/")
    txt = json.dumps(d, ensure_ascii=False)
    n = 0
    for x, y in ((de, para), (de.replace("/", "\\\\"), para.replace("/", "\\\\"))):   # "/" e "\\" (como fica dentro do JSON)
        n += txt.count(x)
        txt = txt.replace(x, y)
    d = json.loads(txt)
    salvar(pasta, d, "religar")
    print("%d caminho(s) trocado(s): %s → %s" % (n, de, para))


def cmd_migrar_keys(a):
    """migrar-keys <proj> — rascunho gravado pelo motor ANTES de 22/10/2026 (keys de vídeo contadas do começo do segmento): passa as keys
    das trilhas «Brabo · …» para o tempo no arquivo. Só mexe em segmento cujas keys caem todas antes do trecho (idempotente)."""
    pasta, d = carregar(a[0])
    n = 0
    for t in d["tracks"]:
        if t["type"] not in ("video", "audio") or not t.get("name", "").startswith("Brabo · "):
            continue
        for sg in t["segments"]:
            st = sg.get("source_timerange")
            ks = [k for ck in sg.get("common_keyframes") or [] for k in ck.get("keyframe_list") or []]
            if not st or not ks or max(k["time_offset"] for k in ks) >= 0:
                continue
            vel = sg.get("speed") or 1.0
            for k in ks:
                k["time_offset"] = int(round(k["time_offset"] + st["start"] / vel))
            n += 1
    if n:
        salvar(pasta, d, "migrar-keys")
    print("%d segmento(s) com as keys passadas para o tempo do arquivo" % n)


def cmd_cliques_camera(a):
    """cliques-camera <proj> camera.json sons.json [--som click.wav] [--a-cada 2] [--volume 0.35] [--folga 0.35]
    Sound design da câmera (Matheus, 22/10/2026: "click quando mudar a posição da câmera com zoom… não em todos, alternando"):
    momentos em que a câmera muda (salto ou volta à base no corte, ênfase, zoom out) → um click a cada N, pulando o que cai a menos de
    'folga' s de outro som da lista. Regrava sons.json (lista completa, itens com "origem": "camera") — depois `audio --lote sons.json`."""
    pasta, d = carregar(a[0])
    cam = json.load(open(a[1], encoding="utf-8-sig"))
    arq_sons = a[2]
    sons = [x for x in json.load(open(arq_sons, encoding="utf-8-sig")) if x.get("origem") != "camera"]
    pasta_sons = os.path.join(RAIZ_SISTEMA, "Aprendizados-SYS", "sons").replace("\\", "/")
    # "tem que ser dinâmicos" (22/10/2026): clicks em rodízio de variações (timbre/altura/lado) em vez do mesmo som repetido
    som = a[a.index("--som") + 1] if "--som" in a else None
    variacoes = [som] if som else sorted(glob.glob(os.path.join(pasta_sons, "click_*.wav"))) or [os.path.join(pasta_sons, "click.wav")]
    cada = int(a[a.index("--a-cada") + 1]) if "--a-cada" in a else 2
    vol = float(a[a.index("--volume") + 1]) if "--volume" in a else 0.35
    folga = float(a[a.index("--folga") + 1]) if "--folga" in a else 0.35
    principal = trilha_por_nome(d, "Brabo · Cortes")
    eventos = [s["target_timerange"]["start"] / US for s in sorted(principal["segments"], key=lambda s: s["target_timerange"]["start"])][1:]
    eventos += [e["em"] - 5 / 30 for e in cam.get("enfases", [])] + [o["em"] for o in cam.get("outs", [])]
    ocupados = [x["em"] for x in sons]
    novos, k = [], 0
    for em in sorted(eventos):
        if any(abs(em - o) < folga for o in ocupados):
            continue
        if k % cada == 0:
            arq = variacoes[len(novos) % len(variacoes)].replace("\\", "/")
            novos.append({"arquivo": arq, "em": round(em, 3), "volume": round(vol * (1.0, 0.85, 1.15)[len(novos) % 3], 3), "origem": "camera"})
            ocupados.append(em)
        k += 1
    # whoosh/pop repetidos também entram em rodízio com as variações que existirem (whoosh_a/b/c, pop_a/b/c)
    rodizio = {}
    for x in sorted(sons, key=lambda x: x["em"]):
        base_nome = os.path.splitext(os.path.basename(x["arquivo"]))[0].split("_")[0]
        var = sorted(glob.glob(os.path.join(pasta_sons, base_nome + "_[a-z].wav")))
        if var and os.path.basename(x["arquivo"]) in (base_nome + ".wav",) + tuple(os.path.basename(v) for v in var):
            k = rodizio.get(base_nome, 0); rodizio[base_nome] = k + 1
            x["arquivo"] = var[k % len(var)].replace("\\", "/")
    json.dump(sorted(sons + novos, key=lambda x: x["em"]), open(arq_sons, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("%d momentos de câmera · %d clicks (1 a cada %d, longe de outros sons) → %s" % (len(eventos), len(novos), cada, arq_sons))


def cmd_nivelar_sons(a):
    """nivelar-sons <proj> sons.json [--acima 5] [--so click,pop] [--teto 1.0] [--piso 0.15]
    Volume de cada som pela VOZ daquele instante (Matheus, 22/10/2026: "ainda não tá saindo os efeitos, apenas os whoosh"): os clicks
    ficavam 5,5 dB abaixo da voz e sumiam. Mede os 80 ms mais fortes do som e a voz da trilha principal no mesmo trecho (do bruto) e
    acerta o volume para o som ficar 'acima' dB por cima (limitado entre piso e teto). Em pausa da fala usa a voz média do vídeo.
    Regrava sons.json — depois `audio --lote sons.json`."""
    import numpy as np, wave
    pasta, d = carregar(a[0])
    arq_sons = a[1]
    acima = float(a[a.index("--acima") + 1]) if "--acima" in a else 5.0
    so = a[a.index("--so") + 1].split(",") if "--so" in a else None
    teto = float(a[a.index("--teto") + 1]) if "--teto" in a else 1.0
    piso = float(a[a.index("--piso") + 1]) if "--piso" in a else 0.15
    sons = json.load(open(arq_sons, encoding="utf-8-sig"))
    principal = sorted(trilha_por_nome(d, "Brabo · Cortes")["segments"], key=lambda s: s["target_timerange"]["start"])
    idx = indice_materiais(d)
    db = lambda x: 20 * math.log10(math.sqrt(float(np.mean(np.square(x)))) + 1e-9)

    def voz(t0, t1):
        partes = []
        for sg in principal:
            ini = sg["target_timerange"]["start"] / US; fim = ini + sg["target_timerange"]["duration"] / US
            lo, hi = max(ini, t0), min(fim, t1)
            if lo < hi:
                src = sg["source_timerange"]["start"] / US + (lo - ini) * (sg.get("speed") or 1.0)
                r = subprocess.run(["ffmpeg", "-v", "error", "-ss", "%.4f" % src, "-t", "%.4f" % (hi - lo), "-i", idx[sg["material_id"]][1]["path"],
                                    "-vn", "-ac", "1", "-ar", "48000", "-f", "s16le", "-"], capture_output=True)
                partes.append(np.frombuffer(r.stdout, "<i2") / 32768.0 * sg.get("volume", 1.0))
        return np.concatenate(partes) if partes else np.zeros(1)

    media = db(voz(0, 30))
    n = 0
    for x in sons:
        nome = os.path.basename(x["arquivo"]).split("_")[0].split(".")[0]
        if so and nome not in so:
            continue
        w = wave.open(x["arquivo"]); ch = w.getnchannels()
        som = np.frombuffer(w.readframes(w.getnframes()), "<i2").reshape(-1, ch).mean(1) / 32768.0; w.close()
        k = min(len(som), int(0.08 * 48000)); e = np.convolve(som ** 2, np.ones(k), "valid"); i = int(np.argmax(e))
        nivel_som = db(som[i:i + k])
        v = voz(x["em"] + i / 48000, x["em"] + (i + k) / 48000)
        nivel_voz = max(db(v), media - 6)                        # pausa: não deixa o som estourar no silêncio
        x["volume"] = round(min(teto, max(piso, 10 ** ((nivel_voz + acima - nivel_som) / 20))), 3)
        x["acima_da_voz_db"] = round(20 * math.log10(x["volume"]) + nivel_som - nivel_voz, 1)
        n += 1
    json.dump(sons, open(arq_sons, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    ac = [x["acima_da_voz_db"] for x in sons if "acima_da_voz_db" in x and (not so or os.path.basename(x["arquivo"]).split("_")[0].split(".")[0] in so)]
    print("%d som(ns) nivelados · acima da voz: mín %+.1f / mediana %+.1f dB → %s" % (n, min(ac), sorted(ac)[len(ac) // 2], arq_sons) if ac else "nada a nivelar")


def cmd_validar(a):
    pasta, d = carregar(a[0])
    idx = indice_materiais(d)
    erros, avisos = [], []
    for i, t in enumerate(d["tracks"]):
        segs = sorted(t["segments"], key=lambda s: s["target_timerange"]["start"])
        for s, s2 in zip(segs, segs[1:]):
            if s["target_timerange"]["start"] + s["target_timerange"]["duration"] > s2["target_timerange"]["start"] + 1:
                erros.append("trilha %d (%s): segmentos sobrepostos em %.2f s" % (i, t["type"], s2["target_timerange"]["start"] / US))
        for s in segs:
            if s["material_id"] not in idx:
                erros.append("trilha %d: segmento %s aponta material inexistente" % (i, s["id"][:8]))
                continue
            for r in s.get("extra_material_refs", []):
                if r not in idx:
                    erros.append("trilha %d: segmento %s com extra_material_ref inexistente" % (i, s["id"][:8]))
            if s["target_timerange"]["duration"] <= 0:
                erros.append("trilha %d: segmento %s com duração zero" % (i, s["id"][:8]))
            k, m = idx[s["material_id"]]
            st = s.get("source_timerange")
            if k in ("videos", "audios") and st and m.get("type") != "photo" and m.get("duration"):
                if st["start"] + st["duration"] > m["duration"] + 50_000:
                    erros.append("trilha %d: segmento %s passa do fim da mídia %s" % (i, s["id"][:8], m.get("material_name") or m.get("name")))
            if k in ("videos", "audios") and m.get("path") and not os.path.exists(m["path"]):
                if "/Cache/" not in m["path"].replace("\\", "/"):
                    avisos.append("mídia offline: %s" % m["path"])
            if k in ("videos", "audios") and st:
                for ck in s.get("common_keyframes") or []:
                    ts = [x["time_offset"] for x in ck.get("keyframe_list") or []]
                    if ts and (max(ts) < -QUADRO or min(ts) > s["target_timerange"]["duration"] + QUADRO):
                        erros.append("trilha %d (%s): keys de %s fora do trecho em %.2f s — o CapCut segura o último valor e o movimento "
                                     "não anda (rascunho antigo? rode `migrar-keys`)" % (i, t.get("name"), ck.get("property_type"),
                                                                                         s["target_timerange"]["start"] / US))
                        break
            if k == "texts" and d["canvas_config"]["height"] > d["canvas_config"]["width"]:
                y = (s.get("clip") or {}).get("transform", {}).get("y", 0)
                ypx = 960 - y * 960
                if not 420 <= ypx <= 1500:
                    avisos.append("texto fora da zona segura do Reels (y≈%d px): «%s»" % (ypx, texto_de(m)[:40]))
                tx = texto_de(m).split()
                if len(tx) == 1 and t.get("name", "").startswith("Brabo · Legenda"):
                    avisos.append("legenda com UMA palavra sozinha: «%s»" % tx[0])
    # voz do apresentador (22/10/2026: o 1020 inteiro estava mudo pelo has_sound_separated do esqueleto)
    princ = next((t for t in d["tracks"] if t["type"] == "video" and t["segments"]), None)
    if princ:
        for s in princ["segments"]:
            k, m = idx.get(s["material_id"], (None, {}))
            copias = [x for x in d["materials"].get("videos", []) if x.get("id") == s["material_id"]]
            if any(x.get("has_sound_separated") for x in copias) and not any(t["type"] == "audio" and t["segments"] for t in d["tracks"]
                                                        if not t.get("name", "").startswith("Brabo · ")):
                erros.append("trilha principal MUDA: o vídeo %s está com o áudio extraído (has_sound_separated) e não há trilha de voz"
                             % (m.get("material_name") or "")); break
            if s.get("volume", 1.0) <= 0.01 and m.get("has_audio"):
                erros.append("trilha principal com volume 0 em %.2f s (a voz do apresentador nunca sai)" % (s["target_timerange"]["start"] / US)); break
    for t in d["tracks"]:
        if t["type"] == "audio" and t["segments"] and t.get("attribute", 0) & 1:
            (erros if t.get("name", "").startswith("Brabo · ") else avisos).append(
                "trilha de som MUDA: %s (%d sons) — no CapCut o alto-falante da trilha está desligado" % (t.get("name"), len(t["segments"])))
    # a timeline encurtou por baixo do texto? (20/10/2026: o 1º corte do 1020 virou 0,9 s com o CapCut aberto e tudo andou 4,7 s)
    vid = [t for t in d["tracks"] if t["type"] == "video" and t["segments"]]
    txt = [t for t in d["tracks"] if t["type"] == "text" and t["segments"]]
    if vid and txt:
        fim_v = max(s["target_timerange"]["start"] + s["target_timerange"]["duration"] for s in vid[0]["segments"])
        fim_t = max(s["target_timerange"]["start"] + s["target_timerange"]["duration"] for t in txt for s in t["segments"])
        if fim_t - fim_v > 500_000:
            erros.append("trilha principal termina em %.2f s mas há texto até %.2f s: os cortes encurtaram/andaram (refazer `cortes` + o resto)"
                         % (fim_v / US, fim_t / US))
    conts = [open(f, encoding="utf-8").read() for f in copias_conteudo(pasta, d)]
    if len(set(conts)) > 1:
        avisos.append("draft_content da raiz e da Timelines/ diferentes (normal se o CapCut gravou por último: ele usa a da timeline)")
    for e in erros:
        print("ERRO  ", e)
    for w in sorted(set(avisos)):
        print("AVISO ", w)
    print("VALIDAÇÃO OK" if not erros else "VALIDAÇÃO FALHOU (%d erros)" % len(erros))
    return not erros


CMDS = {"listar": cmd_listar, "raio-x": cmd_raio_x, "capturar": cmd_capturar, "cortes": cmd_cortes, "paginar": cmd_paginar,
        "legendas": cmd_legendas, "audio": cmd_audio, "punch": cmd_punch, "formato": cmd_formato, "letreiros": cmd_letreiros, "atras": cmd_atras, "legenda-apple": cmd_legenda_apple, "legenda-palavras": cmd_legenda_palavras, "camera": cmd_camera, "tirar": cmd_tirar, "religar": cmd_religar, "migrar-keys": cmd_migrar_keys, "cliques-camera": cmd_cliques_camera, "nivelar-sons": cmd_nivelar_sons, "tremida": cmd_tremida, "flash": cmd_flash, "zoom": cmd_zoom, "validar": cmd_validar}

if __name__ == "__main__":
    if len(sys.argv) < 2 or sys.argv[1] not in CMDS:
        sys.exit(__doc__)
    r = CMDS[sys.argv[1]](sys.argv[2:])
    if r is False:
        sys.exit(1)
