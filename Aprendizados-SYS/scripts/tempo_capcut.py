#!/usr/bin/env python3
"""tempo_capcut.py — lê o tempo atual do player do CapCut (OCR do Windows sobre o contador capturado em resolução real).
  python tempo_capcut.py --ret 548,1035,95,40      → "57.600 1728 00:00:57:18" (ou "?")
--ret = retângulo do contador "hh:mm:ss:qq" em pixels de tela (achar pela captura do editor maximizado).
"""
import os, subprocess, sys, tempfile
import cv2
import numpy as np

AQUI = os.path.dirname(os.path.abspath(__file__))


def ler(ret):
    tmp = tempfile.mkdtemp(prefix="tc_")
    cru, pb = os.path.join(tmp, "cru.png"), os.path.join(tmp, "pb.png")
    subprocess.run(["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", os.path.join(AQUI, "tela.ps1"),
                    "-Retangulo", ret, "-Largura", "4000", "-Saida", cru], capture_output=True)
    im = cv2.imdecode(np.fromfile(cru, np.uint8), 1)
    g = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
    g = cv2.resize(g, None, fx=4, fy=4, interpolation=cv2.INTER_CUBIC)
    _, b = cv2.threshold(g, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    b = cv2.copyMakeBorder(b, 40, 40, 40, 40, cv2.BORDER_CONSTANT, value=255)
    cv2.imencode(".png", b)[1].tofile(pb)
    out = subprocess.run(["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", os.path.join(AQUI, "ler_tempo.ps1"),
                          "-Imagem", pb], capture_output=True, text=True).stdout.strip()
    return out


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    print(ler(sys.argv[sys.argv.index("--ret") + 1]))
