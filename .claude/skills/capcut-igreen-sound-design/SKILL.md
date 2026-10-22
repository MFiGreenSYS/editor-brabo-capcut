---
name: capcut-igreen-sound-design
description: Sound design e mixagem no CapCut para vídeos do MKT iGreen - SFX no pico de cada troca (whoosh, pop, click, typing, riser), trilha baixa com fade, voz tratada e no loudness certo, e finalização no CapCut de um render vindo do After (o fluxo já usado no iGreen OS Capa). Volumes medidos no projeto real do Matheus. Use quando pedirem "põe os efeitos sonoros", "sound design", "coloca uma trilha", "a voz está baixa", "normaliza o áudio", "finaliza o render do After no CapCut".
---

# Editor Brabo CapCut · Sound design

Números medidos no projeto "1001" (iGreen OS Capa finalizado no CapCut, 01–02/10/2026): `00-CEREBRO.md` §4.
Densidade de referência: ~35 SFX por minuto em vídeo de produto/UI; ~20 por minuto em Reels de fala.

## Mapa de som (volume no CapCut → dB)
| Evento na tela | Som | Volume |
|---|---|---|
| troca de tela / entrada de bloco | Woosh 01 | 0,55 (−5 dB) |
| troca grande / virada | Woosh 02 · Whizzing | 1,0 · 0,43 |
| item aparecendo (lista, card, número) | Pop-up | 0,28–0,38, um por item (~0,9 s entre eles) |
| clique em UI | Click mouse | 2,85 (+9 dB, o arquivo é baixo) |
| texto digitando | Keyboard typing | 1,0–2,3 |
| ok / check | "Correct answer" | 0,20–0,28 |
| conquista / resultado | Game Win | 1,0 |
| antes do fecho | Riser (acelerado até caber) | 1,0 |
| trilha (cama) | música | 0,07 (−23 dB), fade in ~1,2 s, fade out ~2–7 s |
Som cai no PICO do movimento (não no início do clipe). Mesmo som repetido: trocar a variação ou o volume a cada 3–4 usos.

## Click na câmera (Matheus, 22/10/2026)
"Click quando mudar a posição da câmera com zoom… não em todos, alternando": `cliques-camera <proj> camera.json sons.json` (padrão:
1 a cada 2 momentos — salto/volta à base no corte, ênfase, zoom out —, volume 0,35, pula o que cai a < 0,35 s de outro som) e depois
`audio --lote sons.json`. Sons em rodízio ("tem que ser dinâmicos"): `click_a/b/c` (timbre, altura e lado diferentes) com volume
×1 / ×0,85 / ×1,15, e todo `whoosh.wav` repetido vira `whoosh_a/b/c`. No 1020: 51 momentos → 20 clicks.
**Régua de volume (22/10/2026, "ainda não tá saindo, só os whoosh")**: som curto (click, pop) tem que ficar **+5 dB acima da voz** no
instante em que toca — a 35 % os clicks ficavam −5,5 dB e sumiam. `nivelar-sons <proj> sons.json --so click,pop --acima 5` mede a voz do
trecho no bruto e acerta o volume de cada um (teto 1,0). Click com corpo na faixa da fala (estalo + "tic" 1,9 kHz + batida grave).
Ordem: `cliques-camera` → `nivelar-sons` → `audio --lote`.
**Conferir ouvindo**: trilha de som muda (attribute 1) não toca nada — `validar` acusa; `ouvir_saida.py` grava o CapCut tocando.

## Inserir pelo motor (CapCut fechado)
`python -I Aprendizados-SYS/scripts/capcut_brabo.py audio "<projeto>" "<arquivo.wav>" --em 3.20 --volume 0.55`
Sobreposto → o motor abre outra trilha "Brabo · SFX N" sozinho. Biblioteca de som do CapCut (baixada pelo app) não se escreve
do zero: o Matheus põe um no MODELO e capturamos (`capturar --segmento … --como sfx-woosh`) para clonar.
Arquivos de som próprios: guardar em `Aprendizados-SYS/sons/` (pedir ok antes de baixar qualquer pack; só licença livre).

## Voz
- Medir: `ffmpeg -i export.mp4 -af ebur128=peak=true -f null -` (ou `revisar_export.py`). Alvo voz −19,5…−16 LUFS, pico ≤ −1 dBTP.
- No CapCut: "Aprimorar voz"/"Reduzir ruído" só se houver ruído audível (comparar antes/depois; artefato metálico = desligar);
  "Normalizar volume" na voz. Voz ≥ 12 dB acima da trilha; trilha desce ~12 dB 0,4 s antes da fala quando ela começa depois de música.
- Voz picotada pelo cortador: sem fade (o corte já respeita o decaimento); só crossfade se ouvir clique.

## Finalizar no CapCut um render do After
1. O Editor Brabo do After renderiza (quando o Matheus pede) → importar o MP4 como trilha principal (CapCut 16:9 ou 9:16 igual ao render).
2. Narração (se separada) em trilha própria, picotada nas pausas para o visual respirar.
3. Mapa de som acima por evento visual (ler o roteiro/TEMPOS do projeto do After para achar os tempos de cada animação).
4. Trilha a 0,07, fades; filtro de grão leve (no 1001: "Granulação vinho" a 30 %) só se o Matheus pedir o look.
5. Revisar e registrar no projeto de lá (`PROJETOS/NNN/NOTAS.md` do After) e aqui no `00-CEREBRO.md` se aprender algo.
