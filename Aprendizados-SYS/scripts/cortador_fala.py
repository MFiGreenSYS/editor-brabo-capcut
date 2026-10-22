#!/usr/bin/env python3
"""cortador_fala.py — corte de fala (talking head / narração) com as regras MEDIDAS nos cortes do próprio Matheus.

Porte do `MR-Editor.SYS/05_ferramentas/mreditor/audio.py` + `corte.py` (regras CRT-01, CRT-02, CRT-04; medição de 447 cortes em
10 projetos: `MR-Editor.SYS/00_sistema/auditoria-edicao/corte-de-respiro/resumo.md`), sem scipy (bloqueado nesta máquina).

  python cortador_fala.py <pasta_wav> <selecao.json> <saida_dir> [--fps 23.976] [--so H05] [--modelo small] [--sem-whisper]

selecao.json = {"H05": [[clip, t0, t1, "nota", "!"/"!i"/"!f" opcional], ...]} — os TAKES escolhidos (lendo a transcrição);
o cortador decide sozinho, dentro de cada take, onde está a voz, que pausas/respiros saem e que falsos inícios caem.

DETECÇÃO DE VOZ (CRT-01, §0 da medição): RMS 10 ms, mediana de 3 quadros; N = p5; S = mediana dos quadros > N+20 dB
(nível da fala da pessoa); voz = ≥ S−15 dB; silêncio puro = < S−30 dB; aglomerado = quadros de voz com lacunas ≤ 40 ms
fundidas e ≥ 50 ms; é FALA se tiver ≥ 30 ms com periodicidade ≥ 0,5 (autocorrelação 80–400 Hz); senão é RESPIRO/ruído.
CORTE (CRT-01): pausa ≥ 0,40 s entre falas sai (dentro do take fica ≤ 0,40 s; nunca > 0,50 s); SAÍDA = fim da voz + 80 ms
(mín. 40 ms, sem invadir a voz seguinte); ENTRADA = até 1 quadro antes do início da voz, nunca depois; remoção mínima 0,10 s;
respiro sai junto com a pausa. Clipe mantido com voz < 0,30 s é proibido (CRT-02) → junta ou cai.
FALSO INÍCIO / TROPEÇO (CRT-04): aglomerado curto (≤ 0,7 s) isolado por pausa ≥ 0,25 s cuja transcrição ISOLADA (trecho
curto: a passada longa engole a repetição) casa com o começo da frase seguinte ou é hesitação ("é", "ahn", "hum", "o", "a",
"e") → sai. Ex.: H05 "O… O que precisa ser analisado" (o whisper longo só viu um "O").
LIMPEZA POR SUB-AGLOMERADO (2026-10-11, Matheus: "voz do filmmaker de fundo" e "a ÚLTIMA repetição é a correta"): pedaços de voz
separados por ≥ 0,12 s transcritos isolados → sai voz da equipe (palavras de direção), voz solta fraca no início do take que não
é o começo do roteiro, murmúrio sem palavra, repetição (fica a última) e repetição na emenda (rabo de A = começo de B).
Use --modelo medium (o small erra palavra curta isolada).
Saída: <ID>.edl.json (formato do decupagem.py) e <ID>.cortes.md (o que saiu e por quê, para o Matheus conferir).
"""
import json, os, re, sys, wave, unicodedata
import numpy as np

QS = 0.010                      # quadro de energia (10 ms)
SR = 16000
HOP = int(SR * QS)
P = {"voz": -15.0, "sil": -30.0, "fundir_q": 4, "aglo_min_q": 5, "per_lim": 0.5, "per_min_q": 3, "f_lo": 80.0, "f_hi": 400.0,
     "pausa_remover": 0.40, "cauda": 0.080, "cauda_min": 0.040, "remocao_min": 0.10, "clipe_min": 0.30,
     "fi_dur_max": 0.70, "fi_pausa_min": 0.25}
# hesitação pura (sai mesmo sem repetição). "o", "a", "e" NÃO: são começo legítimo de frase ("O que muita gente faz", H01) e só
# saem quando se repetem no início da frase seguinte (regra "casa": "O… / O que precisa", H05).
HES = {"eh", "ah", "ahn", "hum", "hm", "uh", "humm", "ahm"}
ENFASE = {"muito", "mais", "bem", "nunca", "sempre", "todo", "toda", "todos", "nada", "super", "demais", "sim", "nao"}
# voz da equipe (filmmaker/diretor): fala só com estas palavras e pelo menos uma "forte" sai
DIRECAO = {"gravando", "grava", "gravou", "gravar", "valendo", "vai", "corta", "corte", "boa", "beleza", "perfeito", "otimo", "ok",
           "okay", "rodando", "acao", "bora", "isso", "foi", "de", "novo", "mais", "um", "uma", "vez", "pode", "ir", "muito", "bom",
           "show", "tranquilo", "vamos", "la", "e", "agora"}
DIRECAO_FORTE = {"gravando", "grava", "gravou", "valendo", "corta", "boa", "beleza", "perfeito", "otimo", "ok", "okay", "rodando",
                 "acao", "bora", "show"}

def norm(w):
    w = unicodedata.normalize("NFKD", w.lower()).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]", "", w)

def ler_wav(p):
    w = wave.open(p); sr = w.getframerate(); nc = w.getnchannels()
    x = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).astype(np.float32) / 32768
    if nc > 1:
        x = x.reshape(-1, nc).mean(1)
    if sr != SR:
        raise SystemExit("WAV precisa ser %d Hz (ffmpeg -ac 1 -ar 16000)" % SR)
    return x

class Voz:
    def __init__(self, x):
        self.x = x
        n = len(x) // HOP
        db = 10 * np.log10(np.mean(x[: n * HOP].reshape(n, HOP).astype(np.float64) ** 2, axis=1) + 1e-12)
        pad = np.concatenate([[db[0]], db, [db[-1]]])
        self.db = np.median(np.stack([pad[:-2], pad[1:-1], pad[2:]]), axis=0)   # mediana móvel de 3
        N = np.percentile(self.db, 5)
        self.S = float(np.median(self.db[self.db > N + 20])) if np.any(self.db > N + 20) else float(N + 25)
        self.Tvoz, self.Tsil = self.S + P["voz"], self.S + P["sil"]
        self.n = n

    def periodicidade(self, frames):
        W = 512; win = np.hanning(W)
        wac = np.correlate(win, win, "full")[W - 1:]; wac = wac / wac[0]
        lo, hi = int(round(SR / P["f_hi"])), int(round(SR / P["f_lo"]))
        out = np.zeros(len(frames))
        for k in range(0, len(frames), 2048):
            fr = np.asarray(frames[k:k + 2048])
            c = ((fr + 0.5) * HOP).astype(int)
            idx = np.clip(c[:, None] + np.arange(-W // 2, W // 2)[None, :], 0, len(self.x) - 1)
            y = self.x[idx].astype(np.float64); y = (y - y.mean(1, keepdims=True)) * win
            F = np.fft.rfft(y, 1024, axis=1)
            ac = np.fft.irfft(np.abs(F) ** 2, 1024, axis=1)[:, :W]
            ac = ac / np.maximum(ac[:, :1], 1e-12) / np.maximum(wac[None, :], 1e-3)
            out[k:k + 2048] = ac[:, lo:hi + 1].max(1)
        return out

    def aglomerados(self, a, b):
        """[(ini, fim, 'fala'|'respiro')] em segundos dentro de [a, b]"""
        f0, f1 = max(0, int(a / QS)), min(self.n, int(b / QS) + 1)
        m = self.db[f0:f1] >= self.Tvoz
        d = np.diff(np.concatenate([[0], m.astype(np.int8), [0]]))
        runs = list(zip(np.where(d == 1)[0] + f0, np.where(d == -1)[0] + f0))
        fund = []
        for s, e in runs:
            if fund and s - fund[-1][1] <= P["fundir_q"]:
                fund[-1][1] = e
            else:
                fund.append([s, e])
        fund = [(s, e) for s, e in fund if e - s >= P["aglo_min_q"]]
        out = []
        for s, e in fund:
            per = self.periodicidade(list(range(s, e)))
            tipo = "fala" if np.sum(per >= P["per_lim"]) >= P["per_min_q"] else "respiro"
            out.append((s * QS, e * QS, tipo))
        return out

def f0_trecho(V, x, s, e):
    """altura mediana da voz (Hz) nos quadros de voz de [s, e] — separa quem fala (videomaker × apresentadora)"""
    W = 640; win = np.hanning(W); lo, hi = int(SR / 400), int(SR / 70); out = []
    for f in range(int(s / QS), int(e / QS)):
        if f >= V.n or V.db[f] < V.Tvoz:
            continue
        c = int((f + 0.5) * HOP); y = x[max(0, c - W // 2): c + W // 2]
        if len(y) < W:
            continue
        y = (y - y.mean()) * win; ac = np.fft.irfft(np.abs(np.fft.rfft(y, 2048)) ** 2)[:W]; ac = ac / (ac[0] + 1e-12)
        k = lo + int(np.argmax(ac[lo:hi]))
        if ac[k] > 0.5:
            out.append(SR / k)
    return float(np.median(out)) if len(out) >= 8 else None

_MODELO = None
_CACHE = {}
def transcreve_curto(x, a, b, modelo):
    """transcrição de um trecho curto isolado (o whisper longo engole repetições)"""
    global _MODELO
    chave = (id(x), round(a, 2), round(b, 2))
    if chave in _CACHE:
        return _CACHE[chave]
    import whisper
    if _MODELO is None:
        _MODELO = whisper.load_model(modelo)
    seg = x[max(0, int(a * SR)):int(b * SR)]
    seg = np.concatenate([np.zeros(int(0.2 * SR), np.float32), seg, np.zeros(int(0.2 * SR), np.float32)])
    r = _MODELO.transcribe(seg, language="pt", fp16=False, condition_on_previous_text=False, temperature=0)
    _CACHE[chave] = [norm(t) for t in r["text"].split() if norm(t)]
    return _CACHE[chave]

def cortar_take(V, x, t0, t1, exato, fps, usar_whisper, modelo, log, nota="", f0_ref=None, segs_brutos=None):
    q = 1.0 / fps
    ag = V.aglomerados(t0 - 1.0, t1 + 1.0)   # janela larga: aglomerado que cruza a borda do take não pode ser truncado
    fala = [(s, e) for s, e, tp in ag if tp == "fala" and (min(e, t1) - max(s, t0)) > 0.5 * (e - s)]
    resp = [(s, e) for s, e, tp in ag if tp == "respiro"]
    for s, e in resp:
        log.append("respiro/ruído %.2f–%.2f (sem periodicidade de voz) → sai" % (s, e))
    if not fala:
        return []
    # fala COLADA à borda do take (≤ 0,15 s) é o resto da mesma palavra/frase: entra (senão a borda amputa a palavra)
    # só se for resto de palavra (≤ 0,35 s) ou tiver palavra de verdade (vocalização "hmm" antes de falar fica fora: H05 1,2 s)
    todas = sorted((s, e) for s, e, tp in ag if tp == "fala")
    def vale(s, e):
        if e - s <= 0.35:
            return True
        return bool(usar_whisper and transcreve_curto(x, s, e, modelo))
    if exato not in ("!", "!f"):
        for s, e in todas:
            if s > fala[-1][1] and s - fala[-1][1] <= 0.15:
                if vale(s, e):
                    fala.append((s, e)); log.append("fala colada no fim do take %.2f–%.2f → entra" % (s, e))
                else:
                    log.append("som de voz colado no fim %.2f–%.2f sem palavra → fora" % (s, e))
    if exato not in ("!", "!i"):
        for s, e in reversed(todas):
            if e < fala[0][0] and fala[0][0] - e <= 0.15:
                if vale(s, e):
                    fala.insert(0, (s, e)); log.append("fala colada no início do take %.2f–%.2f → entra" % (s, e))
                else:
                    log.append("som de voz colado no início %.2f–%.2f sem palavra → fora" % (s, e))
    # LIMPEZA POR SUB-AGLOMERADO (Matheus, 2026-10-11: "voz do filmmaker de fundo dando instruções" e "ela repete palavras, a
    # ÚLTIMA repetição é a correta"). A passada longa do whisper engole as duas coisas; aqui cada pedaço de voz separado por
    # lacuna ≥ 0,12 s é transcrito ISOLADO e comparado com o vizinho.
    U = [[fala[0][0], fala[0][1]]]
    for s, e in fala[1:]:
        if s - U[-1][1] < 0.12:
            U[-1][1] = e
        else:
            U.append([s, e])
    fora = []                                   # intervalos removidos (ataque suave não pode voltar para dentro deles)
    # VOZ DE OUTRA PESSOA pelo TIMBRE (Matheus, 2026-10-11, H01: o videomaker DITA a frase e ela repete; o ditado tem o mesmo texto,
    # então nem a transcrição nem o nível bastam). Altura da voz do pedaço < 0,75× ou > 1,35× a do apresentador → sai.
    # DITADO = timbre fora do apresentador E o mesmo texto repetido logo depois NA VOZ DELE (Pedro, 2026-10-11: voz masculina
    # expressiva varia 131–276 Hz; só a altura derrubava frases dele). O ditado do H01 (147–176 Hz, ela 235 Hz) continua saindo.
    def repetido_depois(a, b, toks_a):
        if len(toks_a) < 4 or not segs_brutos:      # ≥ 4 palavras: "é pra você" se repete em qualquer fala (A1 Pedro)
            return None
        dur = max(b - a, 1.0)
        for k, sg in enumerate(segs_brutos):
            if not (b - 0.2 <= sg["start"] <= b + 60):
                continue
            # a repetição pode vir em vários segmentos e PARAFRASEADA (H01: "devidamente formalizado" → "registrado formalmente
            # pela empresa"): junta os segmentos que começam até 1,6× a duração do ditado depois e exige ≥ 50 % das palavras
            jun = [g for g in segs_brutos[k:] if g["start"] <= sg["start"] + 1.6 * dur + 1]
            tb = [norm(w) for g in jun for w in g["text"].split() if norm(w)]
            if tb and sum(1 for t in toks_a if t in tb) >= 0.5 * len(toks_a):
                fr = f0_trecho(V, x, jun[0]["start"], jun[-1]["end"])
                if fr and 0.85 * f0_ref <= fr <= 1.2 * f0_ref:
                    return {"start": jun[0]["start"], "text": " ".join(g["text"].strip() for g in jun)}
        return None
    if f0_ref:
        ft = f0_trecho(V, x, t0, t1)
        if ft and (ft < 0.80 * f0_ref or ft > 1.30 * f0_ref):
            rep = repetido_depois(t0, t1, transcreve_curto(x, t0, t1, modelo) if usar_whisper else [])
            if rep:
                log.append("DITADO DE OUTRA PESSOA (take inteiro, timbre %.0f Hz; apresentador %.0f Hz; ele repete em %.1f s «%s») → sai; use o take dele" % (
                    ft, f0_ref, rep["start"], rep["text"].strip()[:50]))
                return []
            log.append("timbre do take %.0f Hz fora do apresentador (%.0f Hz), mas o texto não é repetido depois → fica (variação da voz)" % (ft, f0_ref))
        fica = []
        for u in U:   # pedaço isolado: só frase (≥ 0,6 s), bem fora do timbre E repetido depois na voz do apresentador
            f = f0_trecho(V, x, u[0], u[1]) if u[1] - u[0] >= 0.6 else None
            if f and (f < 0.72 * f0_ref or f > 1.40 * f0_ref) and                     repetido_depois(u[0], u[1], transcreve_curto(x, u[0], u[1], modelo) if usar_whisper else []):
                log.append("VOZ DE OUTRA PESSOA %.2f–%.2f (timbre %.0f Hz; apresentador %.0f Hz) → sai" % (u[0], u[1], f, f0_ref))
                fora.append((u[0], u[1]))
            else:
                fica.append(u)
        U = fica
        if not U:
            return []
    if usar_whisper and len(U) > 1:
        tk = [transcreve_curto(x, s, e, modelo) for s, e in U]
        rel = [float(np.median(V.db[int(s / QS):int(e / QS)]) - V.S) for s, e in U]
        roteiro = [norm(w) for w in re.sub(r"^[A-Z]+:\s*", "", nota or "").split() if norm(w)][:3]
        rm = set()
        for i in range(len(U)):
            s, e = U[i]
            # (a) EQUIPE: só palavras de direção ("gravando", "boa", "vai", "corta"…)
            if tk[i] and all(t in DIRECAO for t in tk[i]) and any(t in DIRECAO_FORTE for t in tk[i]) and e - s <= 1.5:
                rm.add(i); log.append("VOZ DA EQUIPE %.2f–%.2f «%s» → sai" % (s, e, " ".join(tk[i]))); continue
            # (b) voz solta no começo do take: curta, fraca, separada, e não é o começo do roteiro (D05 "Gravando." do
            # filmmaker, transcrito isolado como "bravo"; H01 murmúrio antes de "Em primeiro lugar")
            if i == 0 and exato not in ("!", "!i") and e - s <= 0.6 and rel[i] <= -4 and U[1][0] - e >= 0.30 \
                    and not (tk[i] and roteiro and tk[i][0] == roteiro[0]):
                rm.add(i); log.append("VOZ SOLTA NO INÍCIO %.2f–%.2f (%.1f dB abaixo da fala, «%s») → sai" % (s, e, rel[i], " ".join(tk[i]))); continue
            # (c) murmúrio sem palavra colado a uma fala (≤ 0,45 s, fraco)
            if (not tk[i] or all(t in HES for t in tk[i])) and e - s <= 0.45 and rel[i] <= -5:
                rm.add(i); log.append("murmúrio sem palavra %.2f–%.2f (%.1f dB) → sai" % (s, e, rel[i])); continue
        # (d) REPETIÇÃO → fica a última: B começa com o começo de um A anterior (até 3 pedaços e 2,5 s para trás) → sai de A até B
        for j in range(1, len(U)):
            if j in rm or not tk[j]:
                continue
            for i in range(j - 1, max(-1, j - 4), -1):
                if U[j][0] - U[i][0] > 2.5 or i in rm or not tk[i]:
                    continue
                m = 0
                while m < min(len(tk[i]), len(tk[j])) and tk[i][m] == tk[j][m]:
                    m += 1
                if (m >= 2 or m == len(tk[i])) and any(len(t) >= 4 for t in tk[i][:m]):
                    for k in range(i, j):
                        if k not in rm:
                            rm.add(k); log.append("REPETIÇÃO %.2f–%.2f «%s» (refeita em %.2f «%s») → sai, fica a última" % (
                                U[k][0], U[k][1], " ".join(tk[k]), U[j][0], " ".join(tk[j][:4])))
                    break
        # (e) REPETIÇÃO NA EMENDA: A termina com a palavra que abre B ("existir no, / no seu caso", H01) → corta o rabo de A
        #     no vale de energia antes da palavra repetida
        for i in range(len(U) - 1):
            j = i + 1
            while j in rm and j < len(U) - 1:
                j += 1
            if i in rm or j in rm or not tk[i] or not tk[j] or U[j][0] - U[i][1] > 1.0 or tk[j][0] not in tk[i][-3:]:
                continue
            # 1 letra sem acento confunde ("você é. / E se…" → "e" = "e") e intensificador repetido é ÊNFASE ("vender muito, muito
            # mesmo"), não erro (Pedro A1/A2, 2026-10-11)
            if len(tk[j][0]) < 2 or tk[j][0] in ENFASE:
                continue
            s, e = U[i]
            f0, f1 = int(s / QS), int(e / QS)
            # o RABO isolado alucina ("tchau gente"); quem decide é a CABEÇA: transcrita até o vale, tem que terminar na palavra
            # que vem antes da repetida (H01: "…podem existir | no m- / no seu caso" → corte em 264,50)
            n = len(tk[i]) - 1 - tk[i][::-1].index(tk[j][0])
            if n == 0:
                continue
            antes = tk[i][n - 1]
            vales = [f for f in range(max(f0 + 20, f1 - 120), f1 - 6)
                     if V.db[f] == V.db[f - 3:f + 4].min() and V.db[f] < V.S - 4]
            for f in sorted(vales, reverse=True):
                cab = transcreve_curto(x, s, f * QS, modelo)
                if cab and cab[-1] == antes and len(cab) >= n - 1:
                    log.append("REPETIÇÃO NA EMENDA: «…%s | %s» repete o começo de «%s» → sai %.2f–%.2f" % (
                        " ".join(cab[-2:]), " ".join(tk[i][n:]), " ".join(tk[j][:3]), f * QS, e))
                    fora.append((f * QS, e)); U[i][1] = f * QS
                    break
        fora += [tuple(U[i]) for i in rm]
        # pedaço removido no meio vira corte mesmo com pausa curta
        U2 = []
        for i, u in enumerate(U):
            if i in rm:
                continue
            ant = U2[-1][1] if U2 else -1e9
            U2.append([u[0], u[1], any(a >= ant - 1e-6 and b <= u[0] + 1e-6 for a, b in fora)])
        U = U2
    else:
        U = [[u[0], u[1], any(a >= (U[i - 1][1] if i else -1e9) - 1e-6 and b <= u[0] + 1e-6 for a, b in fora)] for i, u in enumerate(U)]
    if not U:
        return []
    # grupos: falas com pausa < 0,40 s ficam juntas (pedaço removido entre elas = corte)
    G = [[U[0][0], U[0][1]]]
    for s, e, quebra in U[1:]:
        if s - G[-1][1] < P["pausa_remover"] and not quebra:
            G[-1][1] = e
        else:
            if not quebra:
                log.append("pausa %.2f s em %.2f → corte (≥ %.2f s)" % (s - G[-1][1], G[-1][1], P["pausa_remover"]))
            G.append([s, e])
    # falso início / tropeço: grupo curto isolado antes de outro grupo
    if usar_whisper and len(G) > 1:
        keep = []
        for i, (s, e) in enumerate(G):
            prox = G[i + 1] if i + 1 < len(G) else None
            if prox and (e - s) <= P["fi_dur_max"] and prox[0] - e >= P["fi_pausa_min"]:
                frag = transcreve_curto(x, s, e, modelo)
                ini = transcreve_curto(x, prox[0], min(prox[1], prox[0] + 1.6), modelo)
                casa = frag and ini and all(t in ini[:len(frag) + 1] for t in frag)
                if not frag or casa or all(t in HES for t in frag):
                    log.append("FALSO INÍCIO/TROPEÇO %.2f–%.2f «%s» (próxima começa «%s») → sai" % (s, e, " ".join(frag), " ".join(ini[:4])))
                    continue
            keep.append([s, e])
        G = keep
    # ATAQUE SUAVE × MURMÚRIO (Matheus, 2026-10-11): o que vem fraco antes da fala forte só fica se ACRESCENTA PALAVRA.
    #  - H05 15:06: "hm" fraco (S−17…−12 dB) antes de "O que precisa" → sai (transcrever com ou sem ele dá o mesmo texto);
    #  - H01: o "O" de "O que muita gente faz" é sussurrado (S−25…−16 dB, abaixo do limiar de voz) → entra (sem ele vira "que…").
    def toks(a, b):
        return transcreve_curto(x, a, b, modelo) if usar_whisper else []
    for g in G:
        f0 = int(g[0] / QS)
        # (a) ataque suave antes do aglomerado: anda para trás enquanto ≥ S−30 dB, até 0,25 s
        k = f0
        lim = max([int(b / QS) + 4 for a, b in fora if b <= g[0] + 1e-6] or [0])
        while k > lim and f0 - k < 25 and V.db[k - 1] >= V.Tsil:
            k -= 1
        # ≤ 0,15 s contínuo entra sempre (entrada nunca depois do início da voz; cabeça medida até 0,174 s); mais longo só se
        # acrescentar palavra
        if (f0 - k) * QS > 0.03 and (f0 - k) * QS <= 0.15:
            log.append("ataque suave %.2f–%.2f (≤ 0,15 s) → entra" % (k * QS, g[0]))
            g[0] = k * QS
            continue
        if usar_whisper and (f0 - k) * QS > 0.15:
            com, sem = toks(k * QS, g[0] + 1.2), toks(g[0], g[0] + 1.2)
            if len(com) > len(sem):
                log.append("ataque suave com palavra %.2f–%.2f «%s» → entra" % (k * QS, g[0], " ".join(com[:3])))
                g[0] = k * QS
                continue
        # (b) murmúrio dentro do aglomerado: trecho fraco (< S−5 dB) > 120 ms antes do primeiro quadro forte
        f1 = int(g[1] / QS)
        forte = np.where(V.db[f0:f1] >= V.S - 5)[0]   # D05 "E novos riscos": 0,4 s de murmúrio a S−16…−9 antes do ataque a S+13
        if len(forte) and forte[0] * QS > 0.12:
            novo = (f0 + forte[0]) * QS - 0.04
            if not usar_whisper or toks(g[0], novo + 1.2) == toks(novo, novo + 1.2):
                log.append("murmúrio de ataque %.2f–%.2f (fraco, sem palavra própria) → entrada em %.2f" % (g[0], novo + 0.04, novo))
                g[0] = novo
    # bordas no quadro: entrada ≤ início da voz (até 1 quadro antes); saída = fim + 80 ms, sem invadir a próxima voz
    pecas = []
    for i, (s, e) in enumerate(G):
        k_in = int(np.floor(s * fps + 1e-6))
        if s - k_in * q > q:
            k_in += 0
        k_out = int(round((e + P["cauda"]) * fps))
        if k_out * q < e + P["cauda_min"]:
            k_out += 1
        nxt = G[i + 1][0] if i + 1 < len(G) else None
        if nxt is not None and k_out * q > nxt:
            k_out = int(np.floor(nxt * fps))
        de, ate = k_in * q, k_out * q
        if exato in ("!", "!i") and i == 0 and not any(b <= s + 1e-6 for a, b in fora):
            de = t0
        if exato in ("!", "!f") and i == len(G) - 1 and not any(a >= e - 1e-6 for a, b in fora):
            ate = t1
        pecas.append([de, ate, s, e])
    # remoção mínima: peças quase encostadas viram uma; peça com voz < 0,30 s sem vizinha cai
    jun = []
    for p in pecas:
        if jun and p[0] - jun[-1][1] < P["remocao_min"]:
            jun[-1][1] = p[1]; jun[-1][3] = p[3]
        else:
            jun.append(p)
    out = []
    for de, ate, s, e in jun:
        if ate - de < P["clipe_min"]:
            log.append("clipe curto %.2f–%.2f (< %.2f s, CRT-02) → sai" % (de, ate, P["clipe_min"]))
            continue
        out.append((round(de, 4), round(ate, 4), round(s, 3), round(e, 3)))
    return out

def main():
    a = sys.argv
    if len(a) < 4:
        sys.exit(__doc__)
    pa, sel_p, out = a[1:4]
    fps = float(a[a.index("--fps") + 1]) if "--fps" in a else 24000 / 1001
    so = a[a.index("--so") + 1].split(",") if "--so" in a else None
    modelo = a[a.index("--modelo") + 1] if "--modelo" in a else "small"
    usar_w = "--sem-whisper" not in a
    os.makedirs(out, exist_ok=True)
    S = json.load(open(sel_p, encoding="utf-8"))
    cache = {}
    for vid, takes in S.items():
        if so and vid not in so:
            continue
        edl, md = [], ["# %s — corte de fala (CRT-01/04)" % vid, ""]
        # timbre do apresentador = mediana da altura da voz em todos os takes do reel (quem fala mais é o apresentador)
        fs = []
        for tr in takes:
            if tr[0] not in cache:
                xx = ler_wav(os.path.join(pa, tr[0] + ".wav")); cache[tr[0]] = (xx, Voz(xx))
            xx, VV = cache[tr[0]]
            f = f0_trecho(VV, xx, float(tr[1]), float(tr[2]))
            if f:
                fs.append(f)
        f0_ref = float(np.median(fs)) if fs else None
        md += ["timbre do apresentador: %s" % ("%.0f Hz" % f0_ref if f0_ref else "?"), ""]
        for n, tr in enumerate(takes):
            clip, t0, t1 = tr[0], float(tr[1]), float(tr[2])
            ex = tr[4] if len(tr) > 4 else ""
            if clip not in cache:
                x = ler_wav(os.path.join(pa, clip + ".wav")); cache[clip] = (x, Voz(x))
            x, V = cache[clip]
            log = []
            wj = os.path.join(os.path.dirname(os.path.abspath(pa)), "whisper", clip + ".json")
            segs = json.load(open(wj, encoding="utf-8"))["segments"] if os.path.exists(wj) else None
            pec = cortar_take(V, x, t0, t1, ex, fps, usar_w, modelo, log, tr[3] if len(tr) > 3 else "", f0_ref, segs)
            md.append("## take %d · %s %.2f–%.2f · %s" % (n + 1, clip, t0, t1, tr[3] if len(tr) > 3 else ""))
            md += ["- " + l for l in log] or ["- (nada removido dentro do take)"]
            for de, ate, s, e in pec:
                md.append("  - mantém %.3f–%.3f (voz %.3f–%.3f, cabeça %.0f ms, cauda %.0f ms)" % (de, ate, s, e, (s - de) * 1000, (ate - e) * 1000))
                edl.append({"trecho": n + 1, "clip": clip, "de": de, "ate": ate, "voz": [s, e], "texto": tr[3] if len(tr) > 3 else "", "nota": ""})
            md.append("")
        json.dump(edl, open(os.path.join(out, vid + ".edl.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        open(os.path.join(out, vid + ".cortes.md"), "w", encoding="utf-8").write("\n".join(md) + "\n")
        print("%s: %d cortes, %.1f s" % (vid, len(edl), sum(e["ate"] - e["de"] for e in edl)))

if __name__ == "__main__":
    main()
