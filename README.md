# Editor Brabo CapCut · MKT iGreen

Sistema de edição de vídeo do marketing da iGreen no **CapCut desktop**, operado pelo **Claude Code**. O Claude lê as skills deste
repositório e monta a edição direto no rascunho do CapCut: cortes da fala, letreiros com a Inter da marca, texto atrás da pessoa,
câmera com zoom in/out nas curvas da casa, transições, sound design nivelado pela voz, marca e revisão.

É o mesmo sistema para todos os editores: as mesmas 14 skills, os mesmos 3 agentes, o mesmo motor, as mesmas regras. O que um
editor (ou o Claude dele) aprende vira commit, e os outros recebem com `git pull`.

## O que precisa no PC
- Windows 11
- **CapCut desktop 9.5** (o formato do rascunho foi medido nessa versão), aberto ao menos uma vez
- **Claude Code** (aba Code do app do Claude)
- Python 3.12 e ffmpeg (o instalador diz como instalar se faltar)

## Instalar
```powershell
git clone https://github.com/MFiGreenSYS/editor-brabo-capcut.git
cd editor-brabo-capcut
powershell -NoProfile -ExecutionPolicy Bypass -File .\instalar.ps1
```
O instalador confere Python, ffmpeg e CapCut, instala as bibliotecas (`requirements.txt`) e roda o teste do motor. Tem que terminar
em **MOTOR OK**. Coloque a pasta onde quiser (ex.: `D:\iGreen.SYS\MKT\Editor-Brabo`); nada depende do caminho.

## Usar
1. No app do Claude, aba **Code**, abra uma sessão **nesta pasta**.
2. Peça o que precisa, por exemplo:
   - "novo projeto: Reels do licenciado João, 9:16" → cria `PROJETOS/DD-MM-AAAA_Nome/` com briefing e plano
   - "decupa e corta os respiros desse vídeo" · "legenda dinâmica estilo Apple" · "texto atrás da pessoa"
   - "põe letreiros e zoom estilo Editor Brabo" · "sound design com click na câmera" · "revisa antes de entregar"
3. O Claude pergunta o que faltar, mostra o plano cena a cena, e só monta depois do ok.
4. **O CapCut tem que estar fechado quando o motor grava** (ele recusa sozinho se estiver aberto). Depois o Claude abre o projeto
   e confere na tela e ouvindo a saída de som.

As regras completas, as skills e o motor estão no `CLAUDE.md` (é o que o Claude lê primeiro).

## Regras de ouro (resumo)
- Nada inventado na tela: texto = palavra falada ou copy aprovada. Na dúvida, o Claude pergunta.
- Logo e ícone só de `marca/` (cópia exata dos oficiais). Nunca recortar, redesenhar ou gerar.
- A voz do apresentador nunca sai. Efeito sonoro curto fica ~5 dB acima da voz.
- O motor só mexe nas trilhas `Brabo · …`; o que você editou à mão é intocável. Toda gravação tem backup em `_backups/`.
- Não exporta sem você pedir. Recurso pago do CapCut (Pro), fonte paga ou plugin: o Claude avisa, não assina nem instala.

## Atualizar
```powershell
git pull
```
Rode `instalar.ps1` de novo se o `requirements.txt` mudou.

## Contribuir (melhoria no sistema)
Correção de regra, skill nova, ajuste no motor:
1. Branch própria (`git switch -c ajuste-legenda-x`).
2. Mudou o `capcut_brabo.py`? `python -I Aprendizados-SYS/scripts/test_motor.py` tem que dar **MOTOR OK** (e o teste novo entra junto).
3. Registre: diretiva nova em `Aprendizados-SYS/01-diretivas/REGISTRO-DIRETIVAS.md` (data e quem pediu), aprendizado no arquivo certo
   e no `00-CEREBRO.md`, incidente no checklist.
4. Pull request. O Matheus aprova. Nada de `reset`, `rebase` ou `push --force`.

## O que tem aqui
| Pasta | O quê |
|---|---|
| `CLAUDE.md` | instruções do Editor Brabo (o Claude lê primeiro) |
| `.claude/skills/` | as 14 skills (reels, decupagem, legendas, legenda Apple, letreiros, texto atrás, marca, movimento, transições, sound design, app UI, referências, motor, revisão) |
| `.claude/agents/` | analista, diretor e revisor |
| `Aprendizados-SYS/` | cérebro, diretivas, marca, formato do rascunho, checklist erro zero, estudos herdados do After, referências |
| `Aprendizados-SYS/scripts/` | o motor (`capcut_brabo.py`) e as ferramentas: recorte da pessoa, sons, tela, conferência, teste |
| `Aprendizados-SYS/sons/` · `fontes/` · `modelos/` | sons da casa (sintetizados), Inter limpa, MODNet (recorte) |
| `marca/` | logo, ícone, assinaturas e sub-marcas oficiais (cópia exata de `iGreen.SYS\07_Marca-Assets`) |
| `PROJETOS/` | seus projetos (ficam só no seu PC; não vão para o Git) |

## Licenças de terceiros
- MODNet (`Aprendizados-SYS/modelos/modnet.onnx`, versão ONNX do Xenova): Apache-2.0.
- Inter (`Aprendizados-SYS/fontes/Inter-limpa/`): SIL Open Font License 1.1 — cópia com os contornos unidos, mesmo desenho.
- Sons de `Aprendizados-SYS/sons/`: sintetizados pelo `sfx_brabo.py`, sem licença de terceiro.
- `marca/`: arquivos da iGreen, uso interno.
