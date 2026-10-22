#!/usr/bin/env python3
"""auditar_cortes.py — confere cada corte de uma EDL no ÁUDIO do bruto com a régua do corte do Matheus (CRT-01/02, medida em
447 cortes: MR-Editor.SYS/00_sistema/auditoria-edicao/corte-de-respiro/resumo.md). Usa a detecção de voz do cortador_fala.py
(S = fala mediana; voz ≥ S−15 dB com periodicidade).
  python auditar_cortes.py <pasta_wav> <edl.json> [--fps 23.976]
Problemas (proibidos pela CRT-02):
  - INÍCIO AMPUTADO: há fala nos 60 ms ANTES da entrada (a frase começa antes do corte);
  - FIM AMPUTADO: há fala nos 60 ms DEPOIS da saída (a palavra continua depois do corte);
  - cauda < 40 ms (sai em cima do fim da voz) · clipe com voz < 0,30 s · pausa interna > 0,50 s mantida.
Entrar no ataque da voz (cabeça ~0) NÃO é problema: é o estilo medido (77% dos cortes até 1 quadro antes da voz).
"""
import json, os, sys
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from cortador_fala import ler_wav, Voz, QS

def main():
    a = sys.argv
    if len(a) < 3:
        sys.exit(__doc__)
    pa, edl_p = a[1], a[2]
    fps = float(a[a.index("--fps") + 1]) if "--fps" in a else 24000 / 1001
    edl = [e for e in json.load(open(edl_p, encoding="utf-8")) if e.get("clip")]
    V, prob = {}, 0
    print("%-3s %-10s %8s %8s  %6s %6s  %s" % ("#", "clip", "de", "ate", "cab_ms", "cau_ms", "veredito"))
    for k, e in enumerate(edl):
        if e["clip"] not in V:
            V[e["clip"]] = Voz(ler_wav(os.path.join(pa, e["clip"] + ".wav")))
        v = V[e["clip"]]
        de = round(e["de"] * fps) / fps; ate = round(e["ate"] * fps) / fps
        ag = [(s, t) for s, t, tp in v.aglomerados(de - 0.6, ate + 0.6) if tp == "fala"]
        dentro = [(max(s, de), min(t, ate)) for s, t in ag if t > de and s < ate]
        r = []
        if any(s < de - 0.06 < t or (de - 0.06 <= s < de and t > de) for s, t in ag):
            r.append("INÍCIO AMPUTADO")
        if any(s < ate + 0.06 and t > ate + 0.0 and s <= ate for s, t in ag):
            r.append("FIM AMPUTADO")
        cab = (dentro[0][0] - de) * 1000 if dentro else 0
        cau = (ate - dentro[-1][1]) * 1000 if dentro else 0
        if dentro and cau < 40 and "FIM AMPUTADO" not in r:
            r.append("cauda curta")
        if sum(t - s for s, t in dentro) < 0.30:
            r.append("voz < 0,30 s")
        pz = [dentro[i + 1][0] - dentro[i][1] for i in range(len(dentro) - 1)]
        if pz and max(pz) > 0.50:
            r.append("pausa interna %.2f s" % max(pz))
        prob += bool(r)
        print("%-3d %-10s %8.2f %8.2f  %6.0f %6.0f  %s  «%s»" % (k + 1, e["clip"], de, ate, cab, cau, "; ".join(r) or "ok", e.get("texto", "")[:50]))
    print("\nPROBLEMAS: %d" % prob)

if __name__ == "__main__":
    main()
