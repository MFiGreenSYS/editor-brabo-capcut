#!/usr/bin/env python3
"""capcut_estado.py — fotografa o estado do CapCut (processos, títulos de janela, arquivos do rascunho com data) para descobrir
como saber se um projeto está ABERTO no editor ou se o CapCut está só na tela inicial (modo ao vivo).

  python capcut_estado.py <projeto> [--rotulo home|editor|fechado]   → imprime e guarda em _backups/_estado/<rotulo>.json
"""
import json, os, subprocess, sys, time

sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import capcut_brabo as M


def janelas():
    ps = ("Get-Process | Where-Object { $_.ProcessName -like '*CapCut*' } | "
          "Select-Object ProcessName,Id,MainWindowTitle,@{n='h';e={$_.MainWindowHandle}} | ConvertTo-Json -Compress")
    out = subprocess.run(["powershell", "-NoProfile", "-Command", ps], capture_output=True, text=True, encoding="utf-8").stdout.strip()
    if not out:
        return []
    j = json.loads(out)
    return j if isinstance(j, list) else [j]


def arquivos(pasta):
    r = {}
    for raiz, _, fs in os.walk(pasta):
        for f in fs:
            p = os.path.join(raiz, f)
            st = os.stat(p)
            r[os.path.relpath(p, pasta)] = [st.st_size, time.strftime("%H:%M:%S", time.localtime(st.st_mtime))]
    return r


def main():
    pasta = M.pasta_projeto(sys.argv[1])
    rot = sys.argv[sys.argv.index("--rotulo") + 1] if "--rotulo" in sys.argv else time.strftime("%H%M%S")
    est = {"quando": time.strftime("%H:%M:%S"), "janelas": janelas(), "arquivos": arquivos(pasta)}
    d = os.path.join(M.BACKUPS, "_estado")
    os.makedirs(d, exist_ok=True)
    json.dump(est, open(os.path.join(d, rot + ".json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    for w in est["janelas"]:
        print("processo %-22s pid %-6s janela «%s»" % (w["ProcessName"], w["Id"], w["MainWindowTitle"]))
    print("%d arquivos no rascunho; mais recentes:" % len(est["arquivos"]))
    for k, v in sorted(est["arquivos"].items(), key=lambda x: x[1][1], reverse=True)[:12]:
        print("  %s  %8d  %s" % (v[1], v[0], k))


if __name__ == "__main__":
    main()
