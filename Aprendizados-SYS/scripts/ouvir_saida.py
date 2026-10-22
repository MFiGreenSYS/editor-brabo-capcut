"""ouvir_saida.py — grava o que sai na caixa de som padrão (loopback WASAPI) por N segundos → wav, para o Claude "ouvir" o CapCut tocando.
Uso (soundcard instalado na pasta do usuário, por isso SEM -I):  python Aprendizados-SYS/scripts/ouvir_saida.py saida.wav 5
Método (22/10/2026): posicionar com ver_quadros.ps1, iniciar a gravação, espaço (play) pelo clique.ps1, espaço de novo; depois
correlacionar a gravação com o .wav do SFX esperado (FFT) — o som presente dá correlação bem acima dos outros sons de controle."""
import sys, wave
import numpy as np
import soundcard as sc

arq, seg = sys.argv[1], float(sys.argv[2])
SR = 48000
alto = sc.default_speaker()
mic = sc.get_microphone(alto.name, include_loopback=True)
with mic.recorder(samplerate=SR, channels=2) as r:
    dados = r.record(numframes=int(SR * seg))
x = np.clip(dados, -1, 1)
with wave.open(arq, "wb") as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes((x * 32767).astype("<i2").tobytes())
print("gravado", arq, "pico %.3f" % np.abs(x).max(), "alto-falante:", alto.name)
