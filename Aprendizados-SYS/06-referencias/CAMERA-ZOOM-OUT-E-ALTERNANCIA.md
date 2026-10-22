# Ficha · Câmera: zoom OUT (afastar, abrir nos dois, gancho) e alternância in/out

Estudo de 20/10/2026. Método, fontes, evidência e conversão q24→q30: ver `CAMERA-DERIVA-PUSH-LENTO.md`.

## Lógica
- O zoom OUT existe nos aprovados, sempre com motivo na fala: (1) afastar para "respirar" depois de um IN; (2) abrir para mostrar a 2ª
  pessoa quando ela é citada e voltar quando a fala volta (D HAUSS, D11/D13); (3) gancho do talking head que abre de 167 % para o
  enquadramento (ADV); (4) "zoom in e out dinâmico": IN quando a palavra grande entra, OUT antes do corte (CASA).
- Rápido (10–12 q24, cam40_100 no build) quando muda de assunto/pessoa; lento (plano inteiro, cam65) em cobertura e tela cheia.
- Quando NÃO: jump cut na mesma tomada (lá é IN que fica; "vai e volta" foi reprovado, SANTORINI rev5); pessoa colada na borda que
  não centraliza (compensar com mais zoom, README); não abrir até aparecer borda preta (âncora presa ao quadro).

## Receita medida (D HAUSS aprovado; palavras pelas páginas de legenda de `DHAUSS\_trabalho\montagem.json`)
| Quadros q24 | Escala | × | Duração | Melhor curva medida (RMSE) | Gatilho na fala | Nitidez mín. |
|---|---|---|---|---|---|---|
| q63–70 | 253,1→233,9 % | 0,924 | 7 q24 | linear 1,4 / cam65 1,7 | "afasta no D HAUSS" (EDICOES rev1) | 10 |
| q130–141 | 235,2→289,9 % | 1,233 (IN) | 11 q24 | cam65_100 2,2 | "zoom IN no 43" | 11 |
| q188–198 | 294,3→249,3 % | 0,847 | 10 q24 | cam65_100 2,9 / cam40_100 4,6 | "OUT no eu quero mostrar" ("eu" = q193) | 8 |
| q318–330 | 226,0→138,0 % + pan (356, 646)→(867, 721) | 0,610 | 12 q24 | cam65_100 6,1 / cam40_100 8,1 | abre nos dois em "com o Willer" ("com" = q317) | 21 |
| q371–383 | 140,1→219,7 % + pan de volta | 1,568 (IN) | 12 q24 | cam65_100 1,8 | "que vai apresentar" | 82 |
| q1044–1055 | 138,0→115,6 % + pan | 0,837 | 11 q24 | cam65_100 1,6 | abre nos dois em "uma boa qualidade" ("uma" = q1050) | 8 |
| q1126–1135 / q1169–1177 | ×1,113 IN / ×0,891 OUT | — | 9 / 8 q24 | cam65_100 | IN em "área de lazer" (q1129) | 174 / 62 |
Entre movimentos: deriva +0,3 a +1,9 %/s (cam65). Build: curva cam40_100 em fase ≤ 14 q, cam65 nas outras (`DHAUSS\scripts\17a_cams.py`
l. 20, E3). O render casa um pouco melhor com cam65_100 (E1, diferença de 1–2 pontos de RMSE; o pan junto e o borrão pesam). Para o
CapCut use cam40_100 (regra do build) e confira na prova.
Quadro-prova do "abre nos dois": `estudo_camera\saidas\D318.jpg` (scratchpad): borrão forte q321–326, nítido em q328.

## Receitas lidas no código (sem render local)
- Gancho talking head: 167 % → 100 % em 22 q24 (27,5 q30), cam40_100, a partir do quadro 0 (`plano_reel.py` l. 30, 251–253, E3);
  referência medida "50 % do trajeto em 23 % do tempo + motion blur nos 4 primeiros quadros" (`SINTESE-REELS-TALKING-HEAD.md` l. 48, E3).
- CASA (pedido "câmera 3D zoom in e out dinâmico", 18/10): IN 100→122 % em 10 q24 (cam65) quando o número entra; OUT para 104 % nos
  12 q24 antes do corte (cam65) (`CASA\scripts\17_metragem_atras.jsx` l. 52–53; EDICOES Rev11, E3). Rev12: IN 118 % (q2050–2058) /
  OUT 104 % (q2063–2070); IN 116 % / OUT 104 %. Rev13: IN 124 % / OUT 114 %; CTA IN 130 %, 138 % em "paz" e "privacidade", OUT 100 %.
- Tela cheia da fórmula Joseph: 108→100 % na cena inteira, cam65 (`formula_reels.jsx` `FR.cheia`, E3).
- Pull-out de reset (referência): −15 a −25 % em 14–27 q, ou seco no corte (`SINTESE-REELS-TALKING-HEAD.md` l. 47, E3).

## Tabelas CapCut (30 fps, modelo 1/escala)
- OUT ×0,61 (abre nos dois), cam40_100, 15 q30: 100,0 · 99,3 · 96,3 · 88,5 · 76,8 · 70,6 · 67,3 · 65,2 · 63,9 · 62,9 · 62,2 · 61,7 · 61,4 ·
  61,2 · 61,0 · 61,0 %. IN de volta ×1,57 (15 q30, a cada 2 q): 100,0 · 102,3 · 120,6 · 138,2 · 147,4 · 152,7 · 155,6 · 156,9 · 157,0 %.
- Gancho 167→100, cam40_100, 28 q30 (a cada 2 q): 167,0 · 165,5 · 159,2 · 142,5 · 123,0 · 113,8 · 108,9 · 105,9 · 103,8 · 102,4 · 101,4 ·
  100,7 · 100,3 · 100,1 · 100,0 %.
- CASA IN 100→122 cam65 12 q30: 100,0 · 100,5 · 102,8 · 109,9 · 118,1 · 121,3 · 122,0; OUT 122→104 cam65 15 q30: 122,0 · 121,6 · 120,3 ·
  116,9 · 110,6 · 106,3 · 104,6 · 104,1 · 104,0 % (a cada 2 q).
- Pan junto: a âncora r anda com a mesma curva; posição `T = (r − C)(1 − s)` a cada key.

## Blur [CAPTURAR]
Medido: nitidez cai a 10–40 % no meio do movimento rápido (q24: 3º–6º quadro) e volta no fim (E1). Mesma regra do zoom rápido.

## Som
Whoosh leve −17 dB em cada passagem rápida (`DHAUSS\EDICOES.md` rev1, E3).

## Gatilhos
"zoom in e zoom out", "afasta", "abre nos dois", "alternância de câmera", "vai até ele e volta", "respira".
