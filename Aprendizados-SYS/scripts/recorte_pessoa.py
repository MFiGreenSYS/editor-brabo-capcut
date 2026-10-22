#!/usr/bin/env python3
"""recorte_pessoa.py — a PESSOA recortada (fundo transparente) de um trecho do bruto, para o TEXTO ATRÁS DA PESSOA no CapCut:
fundo (vídeo normal) → letreiro → esta camada por cima.

Cor IDÊNTICA à do clipe de baixo (20/10/2026: a 1ª versão passava os quadros pelo OpenCV, que lê o HDR HLG do iPhone como vídeo comum,
e gravava sem marcação de cor → no CapCut a pessoa recortada ficava lavada, "pele branca"). Agora:
  1ª passada: ffmpeg decodifica o trecho em 672×384 (ou 384×672) RGB só para o MODNet calcular o matte
     (`Aprendizados-SYS/modelos/modnet.onnx`, Xenova/modnet, Apache-2.0; suavizado no tempo 0,25/0,5/0,25; borda fechada 1 px + feather);
  2ª passada: ffmpeg lê o MESMO trecho do bruto em 10 bits, sem conversão de cor, junta o matte como alfa (alphamerge) e grava ProRes 4444
     com as mesmas marcações de cor do bruto (ex.: BT.2020 + HLG). Mesmo -ss e mesmo número de quadros nas duas → alinhamento exato.

  python recorte_pessoa.py <bruto> <de_s> <ate_s> <saida.mov> [--largura 1920]
"""
import json, os, subprocess, sys
import cv2
import numpy as np

AQUI = os.path.dirname(os.path.abspath(__file__))
MODNET = os.path.join(AQUI, "..", "modelos", "modnet.onnx")


def sonda(src):
    j = json.loads(subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
                                   "stream=width,height,r_frame_rate,pix_fmt,color_space,color_transfer,color_primaries,color_range",
                                   "-of", "json", src], capture_output=True, text=True).stdout)["streams"][0]
    n, d = (int(x) for x in j["r_frame_rate"].split("/"))
    return j, n / d


def main():
    a = sys.argv
    if len(a) < 5:
        sys.exit(__doc__)
    src, de, ate, out = a[1], float(a[2]), float(a[3]), a[4]
    larg = int(a[a.index("--largura") + 1]) if "--largura" in a else 1920
    info, fps = sonda(src)
    W0, H0 = int(info["width"]), int(info["height"])
    W = min(larg, W0); H = int(round(H0 * W / W0 / 2) * 2)
    k0 = int(round(de * fps)); n = max(1, int(round(ate * fps)) - k0)
    ss = "%.6f" % (k0 / fps)
    mw, mh = (672, 384) if W >= H else (384, 672)

    # 1ª passada: quadros pequenos para o matte
    p1 = subprocess.run(["ffmpeg", "-v", "error", "-ss", ss, "-i", src, "-frames:v", str(n), "-vf", "scale=%d:%d:flags=area" % (mw, mh),
                         "-pix_fmt", "rgb24", "-f", "rawvideo", "-"], capture_output=True)
    quadros = np.frombuffer(p1.stdout, np.uint8)
    n = len(quadros) // (mw * mh * 3)
    quadros = quadros[: n * mw * mh * 3].reshape(n, mh, mw, 3)
    import onnxruntime as ort                                   # o cv2.dnn 4.14 não carrega este ONNX (Concat dinâmico)
    net = ort.InferenceSession(MODNET, providers=["CPUExecutionProvider"])
    nome = net.get_inputs()[0].name
    cru = []
    for q in quadros:
        x = q.astype(np.float32) / 255.0
        cru.append(net.run(None, {nome: ((x - 0.5) / 0.5).transpose(2, 0, 1)[None].astype(np.float32)})[0][0, 0])
    ker = np.ones((3, 3), np.uint8)
    mattes = []
    for i in range(n):
        m = 0.25 * cru[max(0, i - 1)] + 0.5 * cru[i] + 0.25 * cru[min(n - 1, i + 1)]
        m = cv2.resize(m, (W, H), interpolation=cv2.INTER_LINEAR)
        m = cv2.erode((np.clip(m, 0, 1) * 255).astype(np.uint8), ker, iterations=1)
        mattes.append(cv2.GaussianBlur(m, (5, 5), 0))

    # 2ª passada: o vídeo original (10 bits, sem conversão de cor) + matte como alfa
    tags = []
    for k, opt in (("color_primaries", "-color_primaries"), ("color_transfer", "-color_trc"), ("color_space", "-colorspace"),
                   ("color_range", "-color_range")):
        if info.get(k) and info[k] != "unknown":
            tags += [opt, info[k]]
    filtro = "[0:v]scale=%d:%d:flags=lanczos,format=yuv444p10le[v];[1:v]format=gray[m];[v][m]alphamerge,format=yuva444p10le" % (W, H)
    ff = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-ss", ss, "-i", src,
                           "-f", "rawvideo", "-pix_fmt", "gray", "-s", "%dx%d" % (W, H), "-r", "%.6f" % fps, "-i", "-",
                           "-filter_complex", filtro, "-frames:v", str(n), "-an",
                           "-c:v", "prores_ks", "-profile:v", "4444", "-alpha_bits", "16"] + tags + [out], stdin=subprocess.PIPE)
    for m in mattes:
        ff.stdin.write(m.tobytes())
    ff.stdin.close(); ff.wait()
    print("%s · %d quadros (%.3f–%.3f s) · %dx%d · ProRes 4444 com alfa · cor do bruto: %s" % (
        out, n, k0 / fps, (k0 + n) / fps, W, H, " ".join(tags) or "sem marcação"))


if __name__ == "__main__":
    main()
