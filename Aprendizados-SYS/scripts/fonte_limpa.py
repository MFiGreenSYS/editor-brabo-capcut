"""fonte_limpa.py — cópia da Inter da marca SEM contornos sobrepostos, para o texto do CapCut.

Por quê (22/10/2026): a Inter estática (`07_Marca-Assets\\Marketing\\Inter\\static`) vem com contornos sobrepostos (flag OVERLAP_SIMPLE
em todo glifo, acentos como componentes). O CapCut desenha a sobreposição como emenda: risco vertical na haste do D, riscos no A,
"texto recortado". A fonte da marca não é alterada; a cópia limpa fica em Aprendizados-SYS/fontes/Inter-limpa/ e o motor usa ela.

Uso (uma vez; precisa do skia-pathops, instalado na pasta do usuário, por isso SEM -I):
    python Aprendizados-SYS/scripts/fonte_limpa.py
"""
import glob, os, sys
from fontTools.ttLib import TTFont
from fontTools.ttLib.removeOverlaps import removeOverlaps

AQUI = os.path.dirname(os.path.abspath(__file__))
# a Inter estática da marca (iGreen.SYS\07_Marca-Assets\Marketing\Inter\static); em outra máquina passe os .ttf na linha de comando.
# A Inter limpa já vai pronta no repositório: só precisa rodar isto se a fonte da marca mudar.
ORIGEM = os.path.abspath(os.path.join(AQUI, "..", "..", "..", "..", "07_Marca-Assets", "Marketing", "Inter", "static"))
DESTINO = os.path.abspath(os.path.join(AQUI, "..", "fontes", "Inter-limpa"))


def limpar(arq, destino):
    f = TTFont(arq)
    removeOverlaps(f)                      # une os contornos e desmonta os compostos (Ó, Ã, Ç…)
    for g in f["glyf"].glyphs.values():
        if hasattr(g, "flags") and len(g.flags):
            g.flags[0] &= ~0x40            # tira a marca OVERLAP_SIMPLE: não há mais sobreposição
    f.save(destino)


def main():
    os.makedirs(DESTINO, exist_ok=True)
    arqs = sys.argv[1:] or sorted(glob.glob(os.path.join(ORIGEM, "Inter_18pt-*.ttf")))
    for arq in arqs:
        limpar(arq, os.path.join(DESTINO, os.path.basename(arq)))
        print("limpa:", os.path.basename(arq))


if __name__ == "__main__":
    main()
