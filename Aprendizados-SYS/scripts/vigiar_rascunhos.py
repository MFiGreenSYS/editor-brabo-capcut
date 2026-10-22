#!/usr/bin/env python3
"""vigiar_rascunhos.py — vigia a pasta de rascunhos do CapCut e registra, segundo a segundo, o que é criado, alterado ou apagado,
e quando o CapCut abre/fecha. Criado em 20/10/2026 para descobrir o que apagou os projetos 1001 e 1019.

  python vigiar_rascunhos.py [--minutos 40] [--log _backups/_vigia/AAAAMMDD-HHMMSS.log]

"""
import os, shutil, subprocess, sys, time

sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import capcut_brabo as M


def foto():
    r = {}
    for raiz, ds, fs in os.walk(M.DRAFTS):
        for f in fs:
            p = os.path.join(raiz, f)
            try:
                st = os.stat(p)
                r[os.path.relpath(p, M.DRAFTS)] = (st.st_size, int(st.st_mtime))
            except OSError:
                pass
    return r


def pids():
    out = subprocess.run(["tasklist", "/FI", "IMAGENAME eq CapCut.exe", "/NH", "/FO", "CSV"], capture_output=True, text=True).stdout
    return sorted(l.split(",")[1].strip('"') for l in out.splitlines() if l.lower().startswith('"capcut.exe"'))


def main():
    a = sys.argv
    mins = float(a[a.index("--minutos") + 1]) if "--minutos" in a else 40
    os.makedirs(os.path.join(M.BACKUPS, "_vigia"), exist_ok=True)
    log = a[a.index("--log") + 1] if "--log" in a else os.path.join(M.BACKUPS, "_vigia", time.strftime("%Y%m%d-%H%M%S") + ".log")
    h = open(log, "a", encoding="utf-8")

    def reg(msg):
        linha = "%s  %s" % (time.strftime("%H:%M:%S"), msg)
        h.write(linha + "\n"); h.flush(); print(linha, flush=True)

    antes, pa = foto(), pids()
    reg("vigia ligado · %d arquivos · CapCut %s" % (len(antes), pa or "fechado"))
    fim = time.time() + mins * 60
    while time.time() < fim:
        time.sleep(0.5)
        agora, pn = foto(), pids()
        if pn != pa:
            reg("CapCut processos: %s → %s" % (pa or "nenhum", pn or "nenhum"))
            pa = pn
        novos = sorted(set(agora) - set(antes))
        sumiram = sorted(set(antes) - set(agora))
        mudou = sorted(k for k in set(agora) & set(antes) if agora[k] != antes[k])
        for k in novos:
            reg("NOVO    %s (%d B)" % (k, agora[k][0]))
        for k in mudou:
            reg("MUDOU   %s (%d → %d B)" % (k, antes[k][0], agora[k][0]))
        for k in sumiram:
            reg("SUMIU   %s" % k)
        pastas = {k.split(os.sep)[0] for k in sumiram} - {k.split(os.sep)[0] for k in agora}
        for p in pastas:
            reg("!!! PASTA DE PROJETO SUMIU: %s" % p)
        antes = agora
    reg("vigia desligado")


if __name__ == "__main__":
    main()
