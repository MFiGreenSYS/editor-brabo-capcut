#!/usr/bin/env python3
"""conferir_emendas.py — ouve CADA emenda da EDL como o espectador vai ouvir: os últimos N s do corte A colados nos primeiros N s
do corte B, transcritos isolados com whisper medium. Acusa palavra repetida na emenda (A termina com o que B começa) e emenda que
corta no meio da palavra (transcrição com palavra truncada/“…”). Erro nº 1 da casa (emenda de fala, 7× no After).

  python conferir_emendas.py <pasta_wav> <edl.json> [--seg 1.5] [--modelo medium] [-o emendas.md]
"""
import json, os, re, subprocess, sys, tempfile, unicodedata

sys.stdout.reconfigure(encoding="utf-8")


def norm(w):
    w = unicodedata.normalize("NFD", w.lower())
    return re.sub(r"[^a-z0-9%]", "", "".join(c for c in w if unicodedata.category(c) != "Mn"))


def main():
    a = sys.argv
    if len(a) < 3:
        sys.exit(__doc__)
    pa, edl_p = a[1], a[2]
    n = float(a[a.index("--seg") + 1]) if "--seg" in a else 1.5
    modelo = a[a.index("--modelo") + 1] if "--modelo" in a else "medium"
    saida = a[a.index("-o") + 1] if "-o" in a else os.path.splitext(edl_p)[0] + ".emendas.md"
    edl = [e for e in json.load(open(edl_p, encoding="utf-8-sig")) if e.get("clip")]
    import whisper
    m = whisper.load_model(modelo)
    tmp = tempfile.mkdtemp(prefix="emendas_")
    md = ["# Emendas — %s" % os.path.basename(edl_p), "", "| # | tempo na montagem | ouvido | veredito |", "|---|---|---|---|"]
    pos, prob = 0.0, 0
    for i, (A, B) in enumerate(zip(edl, edl[1:]), 1):
        pos += A["ate"] - A["de"]
        fa = os.path.join(tmp, "a.wav"); fb = os.path.join(tmp, "b.wav"); fj = os.path.join(tmp, "j%02d.wav" % i)
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", str(max(A["de"], A["ate"] - n)), "-to", str(A["ate"]), "-i",
                        os.path.join(pa, A["clip"] + ".wav"), fa], check=True)
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", str(B["de"]), "-to", str(min(B["ate"], B["de"] + n)), "-i",
                        os.path.join(pa, B["clip"] + ".wav"), fb], check=True)
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", fa, "-i", fb, "-filter_complex", "[0:a][1:a]concat=n=2:v=0:a=1", fj], check=True)
        r = m.transcribe(fj, language="pt", fp16=False, word_timestamps=True,
                         initial_prompt="Ãh, é, é… a a estrutura, no, no seu caso. iGreen, licenciado.")
        ws = [w["word"].strip() for s in r["segments"] for w in s["words"]]
        t = " ".join(ws)
        nw = [norm(w) for w in ws if norm(w)]
        rep = [x for x, y in zip(nw, nw[1:]) if x == y and len(x) > 1]
        # a janela termina N s depois da emenda, no meio da fala: "…" na ÚLTIMA palavra é o fim da janela, não corte (falso
        # alarme em 35 de 43 emendas na AULA-M1, 20/10/2026). Só conta palavra truncada antes da última.
        trunc = any(("…" in w or w.endswith("...") or re.search(r"\w-$", w)) for w in ws[:-1])
        v = "REPETIÇÃO: %s" % ", ".join(rep) if rep else ("PALAVRA CORTADA?" if trunc else "ok")
        prob += v != "ok"
        md.append("| %d | %d:%05.2f | %s | %s |" % (i, pos // 60, pos % 60, t, v))
        print("%2d %6.2f  %-8s %s" % (i, pos, v if v != "ok" else "ok", t), flush=True)
    md += ["", "Problemas: %d (ouvir cada um antes de decidir; o whisper também alucina em trecho curto)" % prob]
    open(saida, "w", encoding="utf-8").write("\n".join(md) + "\n")
    print("→ %s · problemas: %d" % (saida, prob))


if __name__ == "__main__":
    main()
