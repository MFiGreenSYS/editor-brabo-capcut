#!/usr/bin/env python3
"""test_motor.py — teste do capcut_brabo.py num rascunho de TESTE (cópia do rascunho vazio em pasta temporária; os projetos do
CapCut não são tocados). Tem que terminar com MOTOR OK. Bug novo corrigido no motor → vira um teste novo aqui.

  python test_motor.py [--rascunho-vazio 1019]
"""
import json, os, shutil, subprocess, sys, tempfile

sys.stdout.reconfigure(encoding="utf-8")
AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AQUI)
import capcut_brabo as M

MOTOR = os.path.join(AQUI, "capcut_brabo.py")
falhas = []


def roda(*args, ok=True):
    r = subprocess.run([sys.executable, "-I", MOTOR] + list(args), capture_output=True, text=True, encoding="utf-8", errors="replace")
    if (r.returncode == 0) != ok:
        falhas.append("%s → código %d\n%s%s" % (" ".join(args[:2]), r.returncode, r.stdout, r.stderr))
    return r.stdout + r.stderr


def checa(cond, msg):
    if not cond:
        falhas.append(msg)


def main():
    # o teste só grava numa cópia fora da pasta do CapCut: pode rodar com o CapCut aberto
    vazio = sys.argv[sys.argv.index("--rascunho-vazio") + 1] if "--rascunho-vazio" in sys.argv else None
    todos = os.path.join(M.BACKUPS, "_todos")
    antes_todos = set(os.listdir(todos)) if os.path.isdir(todos) else set()
    tmp = tempfile.mkdtemp(prefix="capcut_brabo_")
    proj = os.path.join(tmp, "teste_motor")
    # base = o rascunho pedido ou o mais recente da tela inicial (cópia esvaziada; o original só é lido). O 1001 sumiu em 20/10/2026.
    raiz_meta = os.path.join(M.DRAFTS, "root_meta_info.json")
    meta = json.load(open(raiz_meta, encoding="utf-8-sig"))["all_draft_store"] if os.path.exists(raiz_meta) else []
    meta = [m for m in meta if os.path.exists(os.path.join(m.get("draft_fold_path", ""), "draft_content.json"))]
    # máquina nova (editor que acabou de clonar o repositório, sem projeto no CapCut): base = esqueletos/rascunho_base (CapCut 9.5)
    base_repo = os.path.join(M.AQUI, "esqueletos", "rascunho_base")
    real = bool(vazio or meta)
    fonte = M.pasta_projeto(vazio) if vazio else (os.path.normpath(max(meta, key=lambda x: x.get("tm_draft_modified", 0))["draft_fold_path"])
                                                 if meta else base_repo)
    print("base do teste:", fonte)
    shutil.copytree(fonte, proj, ignore=shutil.ignore_patterns(".locked"))
    _, d = M.carregar(proj)
    d.update({"tracks": [], "duration": 0})
    for k, v in d["materials"].items():
        if isinstance(v, list):
            v.clear()
    txt = json.dumps(d, ensure_ascii=False)
    for f in M.copias_conteudo(proj, d):
        open(f, "w", encoding="utf-8").write(txt)
    vid = os.path.join(tmp, "A01.mp4")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i", "testsrc2=s=1080x1920:r=30:d=8", "-f", "lavfi", "-i",
                    "sine=f=220:d=8", "-shortest", "-c:v", "libx264", "-pix_fmt", "yuv420p", "-c:a", "aac", vid], check=True)
    sfx = os.path.join(tmp, "whoosh.wav")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i", "anoisesrc=d=0.6:a=0.3", sfx], check=True)
    edl = [{"trecho": 1, "clip": "A01", "de": 0.20, "ate": 2.10}, {"trecho": 2, "clip": "A01", "de": 2.60, "ate": 4.90},
           {"trecho": 3, "clip": "A01", "de": 5.30, "ate": 7.80}]
    json.dump(edl, open(os.path.join(tmp, "edl.json"), "w", encoding="utf-8"))
    pal = [{"word": w, "start": s, "end": s + 0.3} for w, s in
           [("Sua", 0.3), ("conta", 0.65), ("de", 1.0), ("luz", 1.2), ("até", 1.5), ("20%", 1.75), ("menor.", 2.7),
            ("Sem", 3.1), ("obra", 3.45), ("e", 3.8), ("sem", 4.0), ("investimento.", 4.3), ("Quero", 5.4), ("economizar", 5.8),
            ("agora", 6.3), ("mesmo.", 6.7)]]
    json.dump(pal, open(os.path.join(tmp, "palavras.json"), "w", encoding="utf-8"))

    roda("cortes", proj, os.path.join(tmp, "edl.json"), "--midia", tmp)
    roda("cortes", proj, os.path.join(tmp, "edl.json"), "--midia", tmp)          # 2ª vez substitui, não duplica
    _, d = M.carregar(proj)
    tr = [t for t in d["tracks"] if t.get("name") == "Brabo · Cortes"]
    checa(len(tr) == 1, "cortes duplicou a trilha")
    checa(len(tr[0]["segments"]) == 3, "esperava 3 cortes")
    checa(len(d["materials"]["videos"]) == 1, "material de vídeo repetido (%d)" % len(d["materials"]["videos"]))
    soma = sum(M.us(e["ate"]) - M.us(e["de"]) for e in edl)
    checa(abs(d["duration"] - soma) <= 3, "duração %d ≠ soma dos cortes %d" % (d["duration"], soma))
    checa(d["tracks"][0]["name"] == "Brabo · Cortes", "trilha de cortes não ficou como principal")

    out = roda("paginar", os.path.join(tmp, "palavras.json"), "--edl", os.path.join(tmp, "edl.json"), "--destaques", "20%,economizar",
               "-o", os.path.join(tmp, "paginas.json"))
    pg = json.load(open(os.path.join(tmp, "paginas.json"), encoding="utf-8"))
    checa(all(3 <= len(p["texto"].split()) <= 7 for p in pg), "página fora de 3–7 palavras: %s" % [p["texto"] for p in pg])
    checa(not any(M.re.sub(r"[^\wà-ú%]", "", p["texto"].split()[-1].lower()) in M.NAO_TERMINA for p in pg),
          "página terminando em palavra proibida: %s" % [p["texto"] for p in pg])
    checa(all(p["t0"] < 5.9 for p in pg), "tempo da montagem errado (EDL não aplicada): %s" % pg)
    checa(any("20%" in p["destaque"] for p in pg), "destaque 20%% não marcado")

    roda("legendas", proj, os.path.join(tmp, "paginas.json"), "--esqueleto", "basico")
    _, d = M.carregar(proj)
    leg = [t for t in d["tracks"] if t.get("name") == "Brabo · Legenda"][0]
    idx = M.indice_materiais(d)
    c = json.loads(idx[leg["segments"][0]["material_id"]][1]["content"])
    checa(c["styles"][-1]["range"][1] == M.u16(c["text"]), "faixa do estilo não cobre o texto")
    dest = [json.loads(idx[s["material_id"]][1]["content"]) for s in leg["segments"]]
    checa(any(len(x["styles"]) > 1 for x in dest), "destaque não virou 2º estilo")
    for x in dest:
        pos = 0
        for st in x["styles"]:
            checa(st["range"][0] == pos, "faixas de estilo com buraco/sobreposição em «%s»" % x["text"]); pos = st["range"][1]

    # captura → clone (o caminho do MODELO iGreen): molde tirado da própria legenda, reaplicado com o destaque
    roda("capturar", proj, "--texto", pg[0]["texto"], "--como", "_teste_leg")
    roda("legendas", proj, os.path.join(tmp, "paginas.json"), "--esqueleto", "_teste_leg")
    os.remove(os.path.join(M.ESQ_DIR, "_teste_leg.json"))
    _, d = M.carregar(proj)
    legs = [t for t in d["tracks"] if t.get("name") == "Brabo · Legenda"]
    checa(len(legs) == 1 and len(legs[0]["segments"]) == len(pg), "legenda recapturada duplicou ou perdeu páginas")
    idx = M.indice_materiais(d)
    checa([M.texto_de(idx[s["material_id"]][1]) for s in legs[0]["segments"]] == [p["texto"] for p in pg], "texto da legenda clonada errado")

    roda("audio", proj, sfx, "--em", "1.85", "--volume", "0.55")
    roda("audio", proj, sfx, "--em", "2.0", "--volume", "0.55")                  # sobreposto → abre outra trilha de SFX
    roda("punch", proj, "--escala", "1.12", "--rosto-y", "0.25")
    _, d = M.carregar(proj)
    segs = sorted(d["tracks"][0]["segments"], key=lambda s: s["target_timerange"]["start"])
    checa([s["clip"]["scale"]["x"] for s in segs] == [1.0, 1.12, 1.0], "punch não alternou a escala")
    roda("zoom", proj, "--em", "0.5", "--dur", "0.6", "--de", "1.0", "--para", "1.08")
    _, d = M.carregar(proj)
    ck = {c["property_type"]: c["keyframe_list"] for c in d["tracks"][0]["segments"][0]["common_keyframes"]}
    # escala uniforme no JSON do CapCut = KFTypeScaleX (UNIFORM_SCALE não anima: medido no CapCut 9.5 em 20/10/2026)
    esc = ck.get("KFTypeScaleX", [])
    checa(len(esc) >= 5 and abs(esc[-1]["values"][0] - 1.08) < 1e-6 and esc[0]["values"][0] == 1.0,
          "zoom sem a curva amostrada em KFTypeScaleX (1,0 → 1,08)")
    vals = [k["values"][0] for k in esc]
    checa(all(b >= a - 1e-9 for a, b in zip(vals, vals[1:])), "curva do zoom não é monotônica")
    checa("KFTypePositionY" in ck, "zoom sem compensar a posição do rosto")

    # letreiro com 2 partes (estilos), fonte Inter e animação pop
    let = [{"t0": 0.5, "t1": 3.0, "x": -0.6, "y": 0.28, "alinhar": "esquerda", "anim": "pop",
            "partes": [{"texto": "CARTEIRA\n", "tamanho": 9, "cor": "branco"}, {"texto": "ATIVA", "tamanho": 20, "cor": "verde", "peso": "impacto"}]},
           {"t0": 1.0, "t1": 2.5, "x": 0.6, "y": 0.28, "alinhar": "direita", "anim": "sobe",
            "partes": [{"texto": "SOBREPOSTO", "tamanho": 12}]}]
    json.dump(let, open(os.path.join(tmp, "let.json"), "w", encoding="utf-8"))
    roda("letreiros", proj, os.path.join(tmp, "let.json"))
    _, d = M.carregar(proj)
    lt = [t for t in d["tracks"] if (t.get("name") or "").startswith("Brabo · Letreiros")]
    checa(len(lt) == 2, "letreiros sobrepostos deviam ir para 2 trilhas (foram %d)" % len(lt))
    idx = M.indice_materiais(d)
    c = json.loads(idx[lt[0]["segments"][0]["material_id"]][1]["content"])
    checa(c["text"] == "CARTEIRA\nATIVA" and len(c["styles"]) == 2 and c["styles"][1]["range"] == [9, 14], "partes do letreiro erradas: %s" % c)
    checa(all("Inter" in s.get("font", {}).get("path", "") for s in c["styles"]), "letreiro sem a fonte Inter")
    pop = {k["property_type"]: k["keyframe_list"] for k in lt[0]["segments"][0]["common_keyframes"]}["KFTypeScaleX"]
    checa(pop[0]["values"][0] == 0.0 and max(k["values"][0] for k in pop) > 1.05, "pop sem nascer do 0 e passar de 105 %")

    # sons em lote recriam as trilhas de SFX (sem duplicar ao rodar de novo)
    json.dump([{"arquivo": sfx, "em": 0.2, "volume": 0.5}, {"arquivo": sfx, "em": 0.4, "volume": 0.5}],
              open(os.path.join(tmp, "sons.json"), "w", encoding="utf-8"))
    roda("audio", proj, "--lote", os.path.join(tmp, "sons.json"))
    roda("audio", proj, "--lote", os.path.join(tmp, "sons.json"))
    _, d = M.carregar(proj)
    n_sfx = sum(len(t["segments"]) for t in d["tracks"] if (t.get("name") or "").startswith("Brabo · SFX"))
    checa(n_sfx == 2, "audio --lote devia deixar 2 sons, deixou %d" % n_sfx)
    # 22/10/2026 "não saiu os sons": trilha de som do motor nunca muda (attribute 1 = mudo) e o material é de import novo
    sfx = [x for x in d["tracks"] if (x.get("name") or "").startswith("Brabo · SFX")]
    sfx[0]["attribute"] = 1                                           # simula o CapCut devolvendo a trilha muda
    M.salvar(proj, d, "teste-mudo")
    _, d = M.carregar(proj)
    sfx = [x for x in d["tracks"] if (x.get("name") or "").startswith("Brabo · SFX")]
    checa(all(not x["attribute"] & 1 for x in sfx), "trilha de SFX do motor ficou MUDA")
    ma = [m for m in d["materials"]["audios"] if m["id"] == sfx[0]["segments"][0]["material_id"]][0]
    checa(ma["check_flag"] == 3 and ma["music_id"] == ma["id"], "material de som com as marcas do esqueleto (check_flag/music_id)")

    roda("formato", proj, "16:9")
    roda("legendas", proj, os.path.join(tmp, "paginas.json"), "--esqueleto", "basico", "--y", "-0.62")
    _, d = M.carregar(proj)
    checa((d["canvas_config"]["width"], d["canvas_config"]["height"], d["canvas_config"]["ratio"]) == (1920, 1080, "16:9"), "formato não trocou")
    legs = [t for t in d["tracks"] if t.get("name") == "Brabo · Legenda"][0]["segments"]
    checa(all(abs(s["clip"]["transform"]["y"] + 0.62) < 1e-9 for s in legs), "--y não posicionou a legenda")

    # legenda Apple: um segmento por palavra, texto inteiro em todos, palavras futuras com alfa 0
    roda("legenda-apple", proj, os.path.join(tmp, "paginas.json"), "--y", "-0.62")
    _, d = M.carregar(proj)
    idx = M.indice_materiais(d)
    leg = [t for t in d["tracks"] if t.get("name") == "Brabo · Legenda"][0]["segments"]
    p0 = pg[0]
    segs0 = [s for s in leg if M.us(p0["t0"]) <= s["target_timerange"]["start"] < M.us(p0["t1"])]
    checa(len(segs0) >= len(p0["palavras"]) - 1, "legenda-apple devia ter ~1 segmento por palavra (%d)" % len(segs0))
    c0 = json.loads(idx[segs0[0]["material_id"]][1]["content"])
    checa(c0["text"] == p0["texto"], "legenda-apple: texto da página mudou entre segmentos")
    alfas = [st["fill"]["alpha"] for st in c0["styles"]]
    checa(1.0 in alfas and 0.0 in alfas, "1º segmento devia ter palavras visíveis e escondidas: %s" % alfas)
    cN = json.loads(idx[segs0[-1]["material_id"]][1]["content"])
    checa(all(st["fill"]["alpha"] == 1.0 for st in cN["styles"] if p0["texto"][st["range"][0]:st["range"][1]].strip()),
          "último segmento da página devia mostrar todas as palavras")

    # tremida no corte entre o 1º e o 2º trecho + flash
    corte = (M.us(edl[0]["ate"]) - M.us(edl[0]["de"])) / M.US
    roda("tremida", proj, "--em", "%.3f" % corte)
    roda("flash", proj, "--em", "%.3f" % corte, "--pico", "0.5")
    _, d = M.carregar(proj)
    v0 = [t for t in d["tracks"] if t.get("name") == "Brabo · Cortes"][0]
    segs = sorted(v0["segments"], key=lambda s: s["target_timerange"]["start"])
    kx = {k["property_type"]: k["keyframe_list"] for k in segs[1]["common_keyframes"]}.get("KFTypePositionX", [])
    checa(len(kx) >= 10 and max(abs(k["values"][0]) for k in kx) > 0.01, "tremida sem keys de posição no corte seguinte")
    fl = [t for t in d["tracks"] if t.get("name") == "Brabo · Flash"]
    checa(len(fl) == 1 and len(fl[0]["segments"]) == 1, "flash devia criar 1 segmento")
    fk = {k["property_type"]: k["keyframe_list"] for k in fl[0]["segments"][0]["common_keyframes"]}["KFTypeAlpha"]
    checa(abs(max(k["values"][0] for k in fk) - 0.5) < 1e-6 and fl[0]["segments"][0]["volume"] == 0.0, "flash: pico/volume errados")
    ordem = [t.get("name") for t in d["tracks"]]
    checa(ordem.index("Brabo · Flash") < ordem.index("Brabo · Legenda"), "flash devia ficar abaixo da legenda")

    # texto atrás da pessoa: letreiro + recorte com alfa, camadas na ordem, recorte mudo e com o enquadramento do corte
    json.dump([{"t0": 0.51, "t1": 1.5, "x": 0, "y": 0.6, "alinhar": "centro", "anim": "pop",
                "partes": [{"texto": "ATRÁS", "tamanho": 30, "cor": "branco", "peso": "impacto"}]}],
              open(os.path.join(tmp, "atras.json"), "w", encoding="utf-8"))
    roda("atras", proj, os.path.join(tmp, "atras.json"), "--midia", tmp)
    _, d = M.carregar(proj)
    ordem = [t.get("name") for t in d["tracks"]]
    checa(ordem.index("Brabo · Cortes") < ordem.index("Brabo · Atrás texto") < ordem.index("Brabo · Atrás pessoa") < ordem.index("Brabo · Legenda"),
          "ordem das camadas do texto atrás errada: %s" % ordem)
    ap = [t for t in d["tracks"] if t.get("name") == "Brabo · Atrás pessoa"][0]["segments"]
    idx = M.indice_materiais(d)
    checa(len(ap) == 1 and ap[0]["volume"] == 0.0 and idx[ap[0]["material_id"]][1]["path"].endswith(".mov"),
          "recorte da pessoa ausente, com som, ou sem o .mov")
    checa(ap[0]["clip"]["scale"] == segs[0]["clip"]["scale"], "recorte não herdou a escala do corte")
    # 22/10/2026 "a máscara mexe": recorte no quadro da timeline e no MESMO instante do bruto que o vídeo de baixo
    a0 = ap[0]["target_timerange"]["start"]
    checa(abs(a0 / M.QUADRO - round(a0 / M.QUADRO)) < 0.01, "recorte fora do quadro (%.4f s): a pessoa fica atrás do vídeo" % (a0 / M.US))
    base = M.segmento_em([t for t in d["tracks"] if t.get("name") == "Brabo · Cortes"][0], a0)
    checa(abs((a0 - base["target_timerange"]["start"]) / M.QUADRO - round((a0 - base["target_timerange"]["start"]) / M.QUADRO)) < 0.01,
          "recorte desalinhado do corte de baixo")
    # a voz do apresentador nunca sai: vídeo do motor sem áudio extraído
    copias = [m for m in d["materials"]["videos"] if m["id"] == base["material_id"]]
    checa(copias and copias[0].get("extra_type_option") == 0 and copias[0].get("check_flag") == 63487,
          "material do vídeo principal com as marcas do esqueleto de som extraído (extra_type_option/check_flag)")
    checa(len(copias) == 1 and not copias[0].get("has_sound_separated") and base["volume"] > 0,
          "vídeo principal MUDO ou material duplicado (%d cópias; o CapCut lê a 1ª)" % len(copias))

    # legenda POR PALAVRA (o jeito do After): 1 segmento por palavra, x crescente na linha, entrada com alfa 0, página saindo junta
    roda("legenda-palavras", proj, os.path.join(tmp, "paginas.json"))
    _, d = M.carregar(proj)
    idx = M.indice_materiais(d)
    trs = [t for t in d["tracks"] if (t.get("name") or "").startswith("Brabo · Legenda ")]
    segs = [s for t in trs for s in t["segments"]]
    n_pal = sum(len(p["palavras"]) for p in pg)
    checa(len(segs) == n_pal, "legenda-palavras: %d segmentos para %d palavras" % (len(segs), n_pal))
    checa(not [t for t in d["tracks"] if t.get("name") == "Brabo · Legenda"], "legenda-palavras devia substituir a legenda antiga")
    p0 = sorted([s for s in segs if M.us(pg[0]["t0"]) <= s["target_timerange"]["start"] < M.us(pg[0]["t1"])],
                key=lambda s: s["target_timerange"]["start"])
    xs = [s["clip"]["transform"]["x"] for s in p0]
    checa(len(xs) > 1 and all(b > a for a, b in zip(xs, xs[1:])), "palavras da página fora de ordem no x: %s" % xs)
    fimp = {s["target_timerange"]["start"] + s["target_timerange"]["duration"] for s in p0}
    checa(len(fimp) == 1, "palavras da mesma página deviam sair juntas")
    ka = {k["property_type"]: k["keyframe_list"] for k in p0[1]["common_keyframes"]}["KFTypeAlpha"]
    checa(ka[0]["values"][0] == 0.0 and ka[-1]["values"][0] == 0.0, "palavra devia entrar e sair pela opacidade")
    checa(json.loads(idx[p0[0]["material_id"]][1]["content"])["text"] == pg[0]["palavras"][0][0], "1ª palavra errada")
    pil = [t for t in d["tracks"] if t.get("name") == "Brabo · Pílula"]
    if d["canvas_config"]["width"] > d["canvas_config"]["height"]:
        checa(pil and pil[0]["segments"] and pil[0]["segments"][0]["clip"]["scale"]["x"] < 0.7,
              "pílula sem a escala da largura real (o CapCut ajusta a imagem à largura da tela)")

    # efeito de texto nativo nos letreiros (animação de entrada/saída referenciada no segmento)
    json.dump([{"t0": 0.5, "t1": 3.0, "x": -0.6, "y": 0.28, "alinhar": "esquerda", "efeito": {"entrada": "desfoque", "saida": "desfoque"},
                "partes": [{"texto": "EFEITO", "tamanho": 12}]}], open(os.path.join(tmp, "let2.json"), "w", encoding="utf-8"))
    roda("letreiros", proj, os.path.join(tmp, "let2.json"))
    _, d = M.carregar(proj)
    idx = M.indice_materiais(d)
    sl = [t for t in d["tracks"] if (t.get("name") or "").startswith("Brabo · Letreiros")][0]["segments"][0]
    an = [idx[r][1] for r in sl["extra_material_refs"] if idx.get(r, ("",))[0] == "material_animations"]
    checa(an and {x["type"] for x in an[0]["animations"]} == {"in", "out"}, "letreiro com efeito sem animação nativa de entrada/saída")
    checa(not sl.get("common_keyframes"), "letreiro com efeito nativo não devia ter keys próprias")
    # 22/10/2026 "linhas nos A": a fonte do letreiro é a Inter LIMPA (sem contornos sobrepostos), e continua sendo texto
    arq_fonte = json.loads(idx[sl["material_id"]][1]["content"])["styles"][0]["font"]["path"].replace("\\", "/")
    checa("/fontes/Inter-limpa/" in arq_fonte and os.path.exists(arq_fonte), "letreiro sem a Inter limpa: %s" % arq_fonte)
    from fontTools.ttLib import TTFont
    ft = TTFont(arq_fonte); gl = ft["glyf"]; ga = gl[ft.getBestCmap()[ord("A")]]; ga.expand(gl)
    checa(not ga.flags[0] & 0x40, "Inter limpa ainda marcada com contorno sobreposto")
    # tirar trilhas do motor e religar caminhos
    roda("tirar", proj, "Brabo · Legenda", "Brabo · Pílula")
    _, d = M.carregar(proj)
    checa(not [t for t in d["tracks"] if (t.get("name") or "").startswith(("Brabo · Legenda", "Brabo · Pílula"))], "tirar não removeu")
    roda("tirar", proj, "Minha trilha", ok=False)
    antigo = os.path.dirname(vid).replace("\\", "/")
    roda("religar", proj, "--de", antigo, "--para", "Z:/lugar/novo")
    _, d = M.carregar(proj)
    caminhos = [m["path"] for m in d["materials"]["videos"]]
    checa(any(c.startswith("Z:/lugar/novo") for c in caminhos) and not any(c.startswith(antigo) for c in caminhos), "religar não trocou")
    roda("religar", proj, "--de", "Z:/lugar/novo", "--para", antigo)

    # câmera do After: deriva crescente, salto que parte do fim do corte anterior e fica, nunca < 100 %, posição = rosto × (1 − escala)
    json.dump({"rosto": [0.0, 0.5], "deriva": 0.05, "salto": 1.22, "teto": 1.6, "blocos": [0], "gancho": {"fator": 1.3, "q": 10}},
              open(os.path.join(tmp, "cam.json"), "w", encoding="utf-8"))
    roda("camera", proj, os.path.join(tmp, "cam.json"))
    _, d = M.carregar(proj)
    cs = sorted([t for t in d["tracks"] if t.get("name") == "Brabo · Cortes"][0]["segments"], key=lambda s: s["target_timerange"]["start"])
    k = lambda s, p: {c["property_type"]: c["keyframe_list"] for c in s["common_keyframes"]}[p]
    e0, e1 = k(cs[0], "KFTypeScaleX"), k(cs[1], "KFTypeScaleX")
    checa(abs(e0[0]["values"][0] - 1.3) < 0.01 and abs(e0[-1]["values"][0] - 1.05) < 0.01, "gancho+deriva do 1º corte errados")
    checa(abs(e1[0]["values"][0] - e0[-1]["values"][0]) < 0.01, "salto devia partir de onde o corte anterior terminou")
    checa(abs(max(x["values"][0] for x in e1) - 1.05 * 1.22 * 1.05) < 0.02, "salto ×1,22 + deriva errados no 2º corte")
    checa(min(x["values"][0] for c in cs for x in k(c, "KFTypeScaleX")) >= 1.0, "câmera abaixo de 100 % (borda preta)")
    # 22/10/2026: no arquivo, a key de vídeo conta o tempo NO BRUTO (início do trecho + tempo no segmento); dentro do motor, do segmento
    cru = json.load(open(os.path.join(proj, "draft_content.json"), encoding="utf-8"))
    cc = [s for s in [t for t in cru["tracks"] if t.get("name") == "Brabo · Cortes"][0]["segments"] if s["id"] == cs[1]["id"]][0]
    kc = {c["property_type"]: c["keyframe_list"] for c in cc["common_keyframes"]}["KFTypeScaleX"]
    checa(cs[1]["source_timerange"]["start"] > 0 and kc[0]["time_offset"] == cs[1]["source_timerange"]["start"] + e1[0]["time_offset"],
          "key de vídeo gravada sem o início do trecho no bruto: o CapCut segura o último valor (câmera parada)")
    checa(e1[0]["time_offset"] == 0, "keys dentro do motor deviam contar do começo do segmento")
    ky = k(cs[1], "KFTypePositionY")
    checa(abs(ky[-1]["values"][0] - 0.5 * (1 - e1[-1]["values"][0])) < 1e-6, "posição não segue o rosto")

    # click de câmera alternado, longe dos outros sons, e sons.json continua a lista completa
    json.dump([{"arquivo": "x.wav", "em": 0.0, "volume": 0.5}], open(os.path.join(tmp, "sons.json"), "w", encoding="utf-8"))
    roda("cliques-camera", proj, os.path.join(tmp, "cam.json"), os.path.join(tmp, "sons.json"), "--a-cada", "1")
    sj = json.load(open(os.path.join(tmp, "sons.json"), encoding="utf-8"))
    cl = [x for x in sj if x.get("origem") == "camera"]
    checa(cl and len(sj) == len(cl) + 1 and all(x["em"] >= 0.35 for x in cl), "cliques-camera: clicks ausentes ou em cima de outro som")
    roda("cliques-camera", proj, os.path.join(tmp, "cam.json"), os.path.join(tmp, "sons.json"), "--a-cada", "2")
    cl2 = [x for x in json.load(open(os.path.join(tmp, "sons.json"), encoding="utf-8")) if x.get("origem") == "camera"]
    checa(len(cl2) == (len(cl) + 1) // 2, "cliques-camera --a-cada 2 devia alternar (e não duplicar ao rodar de novo)")
    # nivelar-sons: o click fica 'acima' dB por cima da voz daquele instante (ou no teto), nunca abaixo sem estar no teto
    roda("nivelar-sons", proj, os.path.join(tmp, "sons.json"), "--so", "click", "--acima", "5")
    nv = [x for x in json.load(open(os.path.join(tmp, "sons.json"), encoding="utf-8")) if x.get("origem") == "camera"]
    checa(nv and all("acima_da_voz_db" in x for x in nv), "nivelar-sons não mediu os clicks")
    checa(all(abs(x["acima_da_voz_db"] - 5) < 0.6 or x["volume"] in (1.0, 0.15) for x in nv),
          "nivelar-sons fora do alvo: %s" % [(x["volume"], x["acima_da_voz_db"]) for x in nv])

    v = roda("validar", proj)
    checa("VALIDAÇÃO OK" in v, "validar reprovou o rascunho de teste:\n" + v)
    if real:
        v = roda("validar", fonte)
        checa("VALIDAÇÃO OK" in v, "validar reprovou o rascunho real %s (só leitura):\n%s" % (fonte, v))

    shutil.rmtree(tmp, ignore_errors=True)
    shutil.rmtree(os.path.join(M.BACKUPS, "teste_motor"), ignore_errors=True)
    for x in (set(os.listdir(todos)) if os.path.isdir(todos) else set()) - antes_todos:   # backups-de-tudo feitos pelo teste
        shutil.rmtree(os.path.join(todos, x), ignore_errors=True)
    if falhas:
        print("\n".join("FALHA: " + f for f in falhas))
        sys.exit("MOTOR COM ERRO (%d)" % len(falhas))
    print("MOTOR OK")


if __name__ == "__main__":
    main()
