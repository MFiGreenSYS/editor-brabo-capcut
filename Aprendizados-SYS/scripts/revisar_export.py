#!/usr/bin/env python3
"""revisar_export.py — auto-revisão do vídeo EXPORTADO do CapCut (o equivalente do ae_preview + ae_validar do After).
Tira quadros, desenha a zona segura do Reels por cima (zona_segura.py), mede o loudness e acusa quadro preto/congelado.

  python revisar_export.py <export.mp4> [--cada 1.5 | --tempos 0.5,3.2,7.9] [--saida pasta]

Saída: <pasta>/fN.png (N = quadro), <pasta>/zona.jpg (folha com a grade), <pasta>/revisao.md (números + veredito).
Portões (CHECKLIST-ERRO-ZERO-CAPCUT.md): 1080×1920 · 30 fps · voz/mix −16…−19,5 LUFS integrado · pico ≤ −1 dBTP ·
nenhum trecho preto/congelado > 0,5 s fora do fim.
"""
import json, os, re, subprocess, sys

sys.stdout.reconfigure(encoding="utf-8")
AQUI = os.path.dirname(os.path.abspath(__file__))


def ff(args):
    return subprocess.run(["ffmpeg", "-hide_banner", "-nostats"] + args, capture_output=True, text=True, encoding="utf-8",
                          errors="replace").stderr


def main():
    a = sys.argv
    if len(a) < 2:
        sys.exit(__doc__)
    vid = a[1]
    out = a[a.index("--saida") + 1] if "--saida" in a else os.path.splitext(vid)[0] + "_revisao"
    os.makedirs(out, exist_ok=True)
    p = json.loads(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration:stream=codec_type,width,height,r_frame_rate",
                                   "-of", "json", vid], capture_output=True, text=True, encoding="utf-8").stdout)
    v = next(s for s in p["streams"] if s["codec_type"] == "video")
    num, den = (int(x) for x in v["r_frame_rate"].split("/"))
    fps, dur = num / den, float(p["format"]["duration"])
    if "--tempos" in a:
        ts = [float(x) for x in a[a.index("--tempos") + 1].split(",")]
    else:
        passo = float(a[a.index("--cada") + 1]) if "--cada" in a else 1.5
        ts = [round(i * passo + 0.2, 3) for i in range(int((dur - 0.2) / passo) + 1)]
    for f in os.listdir(out):
        if re.match(r"f\d+\.png$", f):
            os.remove(os.path.join(out, f))
    for t in ts:
        ff(["-y", "-ss", str(t), "-i", vid, "-frames:v", "1", os.path.join(out, "f%d.png" % round(t * fps))])
    subprocess.run([sys.executable, "-I", os.path.join(AQUI, "zona_segura.py"), out], capture_output=True)
    lo = ff(["-i", vid, "-af", "ebur128=peak=true", "-f", "null", "-"])
    I = re.findall(r"I:\s+(-?[\d.]+) LUFS", lo)
    TP = re.findall(r"Peak:\s+(-?[\d.]+) dBFS", lo)
    I = float(I[-1]) if I else None
    TP = float(TP[-1]) if TP else None
    bl = ff(["-i", vid, "-vf", "blackdetect=d=0.5:pix_th=0.08,freezedetect=n=0.002:d=0.5", "-an", "-f", "null", "-"])
    pretos = re.findall(r"black_start:([\d.]+) black_end:([\d.]+)", bl)
    cong = re.findall(r"freeze_start: ([\d.]+)", bl)
    prob = []
    if (v["width"], v["height"]) != (1080, 1920):
        prob.append("formato %dx%d (Reels = 1080×1920)" % (v["width"], v["height"]))
    if abs(fps - 30) > 0.01:
        prob.append("%.3f fps (padrão 30)" % fps)
    if I is None or not -19.5 <= I <= -14.0:
        prob.append("loudness integrado %s LUFS (alvo −16…−19,5 para voz; mix final até −14)" % I)
    if TP is not None and TP > -1.0:
        prob.append("pico %.1f dBTP (máx −1)" % TP)
    pretos = [x for x in pretos if float(x[1]) < dur - 0.3]
    if pretos:
        prob.append("tela preta em %s" % ", ".join("%s–%s s" % x for x in pretos))
    if cong:
        prob.append("quadro congelado ≥ 0,5 s em %s s (confira se é intencional)" % ", ".join(cong[:8]))
    md = ["# Revisão do export — %s" % os.path.basename(vid), "",
          "- formato: %dx%d · %.3f fps · %.2f s" % (v["width"], v["height"], fps, dur),
          "- loudness integrado: %s LUFS · pico: %s dBTP" % (I, TP),
          "- quadros: %d (folha com a zona segura: zona.jpg)" % len(ts), ""]
    md += ["## Problemas"] + ["- " + x for x in prob] if prob else ["## Sem problema automático. Agora olhar a zona.jpg: texto/rosto no vermelho = reprovado."]
    open(os.path.join(out, "revisao.md"), "w", encoding="utf-8").write("\n".join(md) + "\n")
    print("\n".join(md))
    print("\nREVISÃO AUTOMÁTICA OK" if not prob else "\nREVISÃO COM %d PROBLEMA(S)" % len(prob))


if __name__ == "__main__":
    main()
