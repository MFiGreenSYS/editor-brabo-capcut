#!/usr/bin/env python3
"""zona_segura.py — desenha a ZONA SEGURA do Instagram Reels (grade que o Matheus mandou, 2026-10-11) por cima dos quadros do
ae_preview e monta uma folha para revisão: faixa vermelha no topo (0–420) e na base (1500–1920), margens laterais de 32,5 px e a
coluna de ícones à direita (x > 1000, y 1020–1500). Rosto ou texto dentro do vermelho = reprovado.

  python zona_segura.py <pasta_com_fN.png> [--colunas 3]   → <pasta>/zona.jpg
"""
import glob, os, re, sys
import cv2
import numpy as np

def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    d = sys.argv[1]; col = int(sys.argv[sys.argv.index("--colunas") + 1]) if "--colunas" in sys.argv else 3
    fs = sorted(glob.glob(os.path.join(d, "f*.png")), key=lambda p: int(re.findall(r"f(\d+)", os.path.basename(p))[0]))
    out = []
    for p in fs:
        im = cv2.imdecode(np.fromfile(p, np.uint8), cv2.IMREAD_COLOR)
        h, w = im.shape[:2]; k = w / 1080.0
        ov = im.copy()
        cv2.rectangle(ov, (0, 0), (w, int(420 * k)), (0, 0, 230), -1)
        cv2.rectangle(ov, (0, int(1500 * k)), (w, h), (0, 0, 230), -1)
        cv2.rectangle(ov, (int(1000 * k), int(1020 * k)), (w, int(1500 * k)), (0, 0, 230), -1)
        cv2.rectangle(ov, (0, 0), (int(32.5 * k), h), (0, 0, 230), -1); cv2.rectangle(ov, (w - int(32.5 * k), 0), (w, h), (0, 0, 230), -1)
        im = cv2.addWeighted(ov, 0.35, im, 0.65, 0)
        cv2.putText(im, os.path.basename(p)[:-4], (int(40 * k), int(80 * k)), cv2.FONT_HERSHEY_SIMPLEX, 2 * k, (255, 255, 255), max(1, int(4 * k)))
        out.append(cv2.resize(im, (360, 640)))
    while len(out) % col:
        out.append(np.zeros_like(out[0]))
    folha = np.vstack([np.hstack(out[i:i + col]) for i in range(0, len(out), col)])
    ok, b = cv2.imencode(".jpg", folha, [cv2.IMWRITE_JPEG_QUALITY, 85]); b.tofile(os.path.join(d, "zona.jpg"))
    print(os.path.join(d, "zona.jpg"))

if __name__ == "__main__":
    main()
