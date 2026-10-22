# Ficha · Câmera: corte na mesma tomada = zoom IN que fica ("clique de câmera")

Estudo de 20/10/2026. Método, fontes, evidência e conversão q24→q30: ver `CAMERA-DERIVA-PUSH-LENTO.md`.

## Lógica
- Corte DENTRO da mesma tomada (jump cut, mesmo enquadramento) nunca é seco: o pedaço novo nasce no zoom em que o anterior terminou e
  entra ×1,22 em 4 q24 (5 q30), curva cam40_100, e FICA. Depois deriva +3 % (cam65) até o fim do pedaço. Cada clique aumenta mais;
  nunca volta ao tamanho anterior. Teto 1,6 (câmera): "ele anda até a câmera e a cabeça cortaria".
- Diretivas: SANTORINI rev3 17/10 "corte dentro da mesma tomada nunca seco"; rev5 "no clique ele dá um zoom e volta… preciso que no
  clique ele dê um zoom IN… clica de novo e volta no tamanho que era… deve aumentar mais" (`SANTORINI\scripts\07_textos.py` l. 118–124, E3).
  `CHECKLIST-ERRO-ZERO.md` l. 108: "Jump cut = zoom IN que fica (nunca vai e volta)".
- Quando NÃO: corte entre tomadas diferentes (nasce na base 115 % e só deriva); câmera de mão andando ("não aplique o zoom-in do corte
  se a câmera de mão estiver andando", README do modelo, E3); um efeito por tomada (nada de whip/ramp junto, C10).
- Substitui o degrau seco alternado do ADV de 11/10 (`plano_reel.py` l. 147: 100/106/100/110/100/104/108/100/112/100/105) — regra
  mais nova (17/10) e listada como geral em `LEIS-E-METODO.md` §D (E3).

## Receita medida
| Prova | Escala por quadro (q24) | × | Nitidez por quadro | Âncora |
|---|---|---|---|---|
| ANTARES q364–368 | 121,0 · 135,4 · 144,1 · 146,8 · 147,3 % | 1,217 | 132 · 20 · 58 · 134 · 172 | (752, 674) fixa |
| SANTORINI q186–190 | 144,3 · 161,1 · 171,8 · 175,0 · 175,6 % | 1,217 | 87 · 14 · 37 · 88 · 120 | (602, 1325)→(512, 1242) |
| SANTORINI q271–275 (2º clique, bateu no teto 1,6) | 148,9→158,3 % | 1,064 | 40 · 36 · 51 · 41 · 43 | (845, 1207)→(718, 1148) |
| D HAUSS q545–549 | 136,2→150,0 % | 1,102 | 52 · 22 · 55 · 74 | (1080, 450)→(1080, 540) |
Curva: cam40_100 casa melhor (RMSE 2,2 % contra 5,6 % da cam65_100 no ANTARES; 2,5 contra 6,5 no SANTORINI). Progresso medido
0 · 0,55 · 0,88 · 0,98 · 1,00 (E1; o borrão adianta ~0,1 no 1º quadro, use a tabela do modelo).
Código: `ANTARES\scripts\07_textos.py` l. 120–122: `z0 = min(1.6, zp*1.22); fases [[0,zp],[4,z0],[nq,z0*1.03]]; ["cam40_100","cam65"]` (E3).
Montagem real ANTARES: 1,2075 → 1,47315 → 1,5173 (E3) = medido (E1, k = 0,9999).

## Tabela CapCut (30 fps, relativo ao zoom do pedaço anterior, modelo 1/escala)
q0 100,0 · q1 103,8 · q2 115,9 · q3 120,0 · q4 121,6 · q5 122,0 %; depois cam65 até ×1,03 no fim do pedaço. Teto: câmera 1,6 sobre a
base do take (no ANTARES 160 %; o próximo clique só sobe até lá).

## Blur [CAPTURAR: desfoque de movimento/zoom do CapCut]
No After vem do motion blur da comp (obturador 180°, fase −90, `brabo_lib.jsx` l. 167, E3). Medido: nitidez cai a 15 % do quadro
anterior no 1º quadro do movimento e a 44 % no 2º; 3º quadro já nítido (E1). No CapCut: efeito de desfoque só nos quadros q1–q2 do
movimento (2 q30), intensidade alta em q1 e metade em q2 (dois segmentos de efeito de 1 q30 se não houver key de intensidade, E3/proposta).

## Som
Clique de mouse −11 dB no corte (`SANTORINI\scripts\07_textos.py` l. 190–191, E3); no modelo, clique de mouse/câmera alternado (D9).

## Gatilhos
"jump cut", "corte na mesma tomada", "clique", "zoom in que fica", "mudou a posição da câmera".
