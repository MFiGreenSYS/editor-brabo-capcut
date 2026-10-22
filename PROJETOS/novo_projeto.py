#!/usr/bin/env python3
"""novo_projeto.py — cria um projeto de vídeo do Editor Brabo CapCut (MKT iGreen) a partir do _TEMPLATE.

  python -I PROJETOS/novo_projeto.py "Nome do Projeto" [--formato Reels|Feed|Wide]

Pasta = PROJETOS/DD-MM-AAAA_Nome-do-Projeto (Regra 1 do iGreen.SYS) com BRIEFING/PLANO/EDICOES/NOTAS e brutos/, _trabalho/, export/.
Registra a linha em PROJETOS/INDICE.md.
"""
import os, re, shutil, sys, time, unicodedata

sys.stdout.reconfigure(encoding="utf-8")
AQUI = os.path.dirname(os.path.abspath(__file__))


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    nome = sys.argv[1].strip()
    formato = sys.argv[sys.argv.index("--formato") + 1] if "--formato" in sys.argv else "Reels"
    slug = "-".join(w[:1].upper() + w[1:] for w in re.sub(r"[^\w\s-]", "", nome).split())
    data = time.strftime("%d-%m-%Y")
    pasta = os.path.join(AQUI, "%s_%s" % (data, slug))
    if os.path.exists(pasta):
        sys.exit("Já existe: %s" % pasta)
    shutil.copytree(os.path.join(AQUI, "_TEMPLATE"), pasta)
    for sub in ("brutos", "_trabalho", "export"):
        os.makedirs(os.path.join(pasta, sub), exist_ok=True)
    for f in os.listdir(pasta):
        p = os.path.join(pasta, f)
        if f.endswith(".md"):
            t = open(p, encoding="utf-8").read().replace("{{NOME}}", nome).replace("{{DATA}}", data.replace("-", "/")).replace("{{FORMATO}}", formato)
            open(p, "w", encoding="utf-8").write(t)
    idx = os.path.join(AQUI, "INDICE.md")
    if not os.path.exists(idx):          # clone novo do repositório: os projetos não vão no Git, o índice nasce aqui
        with open(idx, "w", encoding="utf-8") as h:
            h.write("# Projetos · Editor Brabo CapCut (MKT iGreen)\n\nStatus: em briefing → plano → em edição → revisão → aprovado → publicado.\n\n"
                    "| Criado | Projeto | Formato | Status | Pasta |\n|---|---|---|---|---|\n")
    with open(idx, "a", encoding="utf-8") as h:
        h.write("| %s | %s | %s | em briefing | `%s` |\n" % (data.replace("-", "/"), nome, formato, os.path.basename(pasta)))
    print(pasta)
    print("Próximo: preencher BRIEFING.md (perguntar o que faltar) e criar no CapCut o projeto vazio chamado \"%s\"." % nome)


if __name__ == "__main__":
    main()
