#!/usr/bin/env python3
"""sfx_brabo.py — gera os sons da casa (sem licença de terceiro, sem download) em Aprendizados-SYS/sons/:
  whoosh.wav   ruído rosa com filtro varrendo 250 → 5500 → 400 Hz, 0,55 s, abre no estéreo (entrada de letreiro / troca de bloco)
  whoosh_longo.wav  idem, 0,9 s (transição grande)
  pop.wav      tom 1100 → 380 Hz em 70 ms + estalo (item que aparece, pop de texto)
  impacto.wav  grave 70 Hz decaindo em 0,45 s + transiente de ruído (zoom de impacto)
  riser.wav    ruído + tom subindo 1,6 s (antes do fecho)
Picos em −3 dBFS; o volume final se acerta no CapCut (mapa de som do 00-CEREBRO §4).

  python sfx_brabo.py [--saida pasta]
"""
import os, sys, wave
import numpy as np

SR = 48000
AQUI = os.path.dirname(os.path.abspath(__file__))


def grava(nome, est, pasta):
    est = est / (np.abs(est).max() + 1e-9) * 10 ** (-3 / 20)
    pcm = (np.clip(est, -1, 1) * 32767).astype(np.int16)
    with wave.open(os.path.join(pasta, nome), "wb") as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(pcm.tobytes())
    print(os.path.join(pasta, nome), "%.2f s" % (len(pcm) / SR))


def rosa(n, semente):
    r = np.random.default_rng(semente)
    b = np.fft.rfft(r.standard_normal(n))
    f = np.arange(len(b)); f[0] = 1
    return np.fft.irfft(b / np.sqrt(f), n)


def varre(x, f_ini, f_meio, f_fim):
    """passa-baixa de 1 polo com corte variando no tempo (subida até o meio, descida até o fim)."""
    n = len(x); t = np.linspace(0, 1, n)
    fc = np.where(t < 0.5, f_ini * (f_meio / f_ini) ** (t / 0.5), f_meio * (f_fim / f_meio) ** ((t - 0.5) / 0.5))
    a = np.exp(-2 * np.pi * fc / SR)
    y = np.zeros(n); acc = 0.0
    for i in range(n):
        acc = a[i] * acc + (1 - a[i]) * x[i]; y[i] = acc
    return y - varre_hp(y)


def varre_hp(y, fc=120.0):
    a = np.exp(-2 * np.pi * fc / SR); z = np.zeros_like(y); acc = 0.0
    for i in range(len(y)):
        acc = a * acc + (1 - a) * y[i]; z[i] = acc
    return z


def whoosh(dur, semente):
    n = int(SR * dur); t = np.linspace(0, 1, n)
    x = varre(rosa(n, semente), 250, 5500, 400)
    env = np.sin(np.pi * np.clip(t, 0, 1)) ** 1.6
    pan = np.clip(t * 1.4 - 0.2, 0, 1)
    m = x * env
    return np.stack([m * np.sqrt(1 - pan * 0.7), m * np.sqrt(0.3 + pan * 0.7)], 1)


def pop():
    n = int(SR * 0.16); t = np.arange(n) / SR
    f = 380 + (1100 - 380) * np.exp(-t / 0.018)
    tom = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / 0.035)
    clk = rosa(n, 7) * np.exp(-t / 0.002) * 0.6
    m = tom + clk
    return np.stack([m, m], 1)


def impacto():
    n = int(SR * 0.6); t = np.arange(n) / SR
    f = 70 + 60 * np.exp(-t / 0.04)
    grave = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / 0.16)
    trans = varre(rosa(n, 3), 3000, 1200, 200) * np.exp(-t / 0.03) * 0.8
    m = grave + trans
    return np.stack([m, m], 1)


def riser():
    n = int(SR * 1.6); t = np.linspace(0, 1, n)
    x = varre(rosa(n, 11), 200, 2500, 9000) * t ** 2
    tom = np.sin(2 * np.pi * np.cumsum(220 * 2 ** (2 * t)) / SR) * t ** 3 * 0.35
    m = x + tom
    return np.stack([m * (0.6 + 0.4 * t), m * (0.6 + 0.4 * t)], 1)


def click(semente=21, agudo=1.0, toc_hz=180, lado=0.0):
    """click de câmera (movimento de câmera, 22/10/2026). 1ª versão (só estalo agudo de 9 ms) ficou 5,5 dB ABAIXO da voz e sumia
    ("só os whoosh"): agora tem corpo na faixa da fala que corta por cima dela — estalo + "tic" tonal 1,6–2,4 kHz + batida grave.
    Variações (semente/agudo/toc/lado) para o rodízio ("tem que ser dinâmicos")."""
    n = int(SR * 0.13); t = np.arange(n) / SR
    est = rosa(n, semente) * np.exp(-t / 0.002)
    tic = np.sin(2 * np.pi * 1900 * agudo * t) * np.exp(-t / 0.014) * 0.9
    ruido = varre(rosa(n, semente + 1), 5000 * agudo, 3000 * agudo, 1500) * np.exp(-t / 0.02) * 1.2
    toc = np.sin(2 * np.pi * toc_hz * t) * np.exp(-t / 0.03) * 0.8
    m = np.tanh(1.6 * (est + tic + ruido + toc))      # satura de leve: mais densidade (mais alto com o mesmo pico)
    return np.stack([m * np.sqrt(1 - max(lado, 0) * 0.6), m * np.sqrt(1 + min(lado, 0) * 0.6)], 1)


def main():
    pasta = sys.argv[sys.argv.index("--saida") + 1] if "--saida" in sys.argv else os.path.join(AQUI, "..", "sons")
    pasta = os.path.abspath(pasta)
    os.makedirs(pasta, exist_ok=True)
    grava("whoosh.wav", whoosh(0.55, 1), pasta)
    grava("whoosh_longo.wav", whoosh(0.9, 2), pasta)
    grava("pop.wav", pop(), pasta)
    grava("impacto.wav", impacto(), pasta)
    grava("riser.wav", riser(), pasta)
    grava("click.wav", click(), pasta)
    for nome, kw in (("a", dict(semente=21, agudo=1.0, toc_hz=180, lado=-0.3)), ("b", dict(semente=31, agudo=1.25, toc_hz=220, lado=0.3)),
                     ("c", dict(semente=41, agudo=0.85, toc_hz=150, lado=0.0))):
        grava("click_%s.wav" % nome, click(**kw), pasta)
    for nome, (dur, sem) in (("a", (0.5, 5)), ("b", (0.6, 6)), ("c", (0.45, 7))):
        grava("whoosh_%s.wav" % nome, whoosh(dur, sem), pasta)


if __name__ == "__main__":
    main()
