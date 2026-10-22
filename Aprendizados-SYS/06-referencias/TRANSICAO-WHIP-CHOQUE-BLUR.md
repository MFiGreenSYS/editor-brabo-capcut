# Ficha · Transições com movimento de câmera: whip (chicote com motion blur), choque, punch + flash, blur, ramp

Estudo de 20/10/2026. Método, fontes, evidência e conversão q24→q30: ver `CAMERA-DERIVA-PUSH-LENTO.md`.
Medição de transição: `estudo_camera\scripts\medir_transicao.py` (nitidez = variância do Laplaciano em 540×960; razão gx/gy < 1 =
borrão horizontal). Folhas: `estudo_camera\saidas\whip_A188.jpg`, `whip_D240.jpg`, `ramp_AR4_160.jpg` (scratchpad).

## 1. Whip (Reels de construtora, aprovado ANTARES/D HAUSS)
**Lógica:** chicote horizontal na entrada de B-ROLL/drone; direção alterna a cada transição (dir = +1, −1, +1…). NUNCA na entrada de
plano de fala ("whip speed ramp blur na entrada de plano de fala = feio", SANTORINI rev3; ANTARES rev3 "entrada da garagem sem whip
(blur feio)"). Nas entradas de fala vai corte com peças douradas do logo. ANTARES: 7 whips em 59,6 s (q188, 606, 702, 969, 1089, 1185,
1361); sem whip em q236, 858, 1231 (entradas de fala) (`ANTARES\_trabalho\montagem.json` → `trans`, E3).
**Código** (`ANTARES\scripts\08_build.jsx` l. 318–327, E3): camada de ajuste de tc−5 a tc+5 q24 com Motion Tile (largura 300 %, bordas
espelhadas) + Transform (obturador próprio 360°): posição 0 → −450 px de tc−5 a tc−0,5 (cam100_10, acelera) e +450 → 0 px de tc a
tc+5 (cam40_100, freia). Em 30 fps: 6 q30 saindo + 6 q30 entrando.
**Medido** (nitidez por quadro, q24):
| Corte tc | antes (tc−6…tc−1) | tc | depois (tc+1…tc+5) |
|---|---|---|---|
| ANTARES 188 (fala → drone) | 117 · 65 · 48 · 45 · 43 · 45 | 127 | 36 · 42 · 62 · 234 · 771 |
| ANTARES 606 (zoom do número → b-roll) | 86 · 47 · 27 · 22 · 22 · 21 | 16 | 10 · 10 · 18 · 43 · 78 |
| D HAUSS 240 (fala → drone) | 121 · 71 · 23 · 8 · 4 · 4 · 5 (tc−7…tc−1) | 125 | 70 · 131 · 220 · 420 · 749 |
Borrão horizontal confirmado (gx/gy cai de 1,04 para 0,62 em q186, E1). Quadro inteiramente nítido de novo em tc+4/tc+5 (E1).
**CapCut:** posição por keys [MOTOR] ±450 px com as curvas acima + espelho/preenchimento da borda [CAPTURAR: recurso de espelho ou
escala ≥ 184 % (1080 + 2×450 = 1980 px de largura) no trecho para não mostrar borda — E4] + desfoque de movimento horizontal [CAPTURAR] nos 5 q30 antes e 4 q30 depois do
corte, mais forte em tc−2…tc+2. Alternativa: transição nativa de deslize com desfoque, 12 q30 centrada no corte [CAPTURAR] (E4: não
medida). Whoosh com pico no corte (−12/−14 dB, LEIS §15, E3).

## 2. Choque (CASA, regra 18/10 "toda troca de cena leva transição de impacto") — só código, CASA sem render
`Aprendizados-SYS\scripts\replica_loira.jsx` l. 152–169 (E3), keys LINEARES a cada quadro q24, camada de ajuste com Motion Tile 300×300
espelhado + Transform obturador 360°:
- sai (tc−5…tc−1): deslocamento 0, −15, −60, −170, −420 px; escala 100, 101,5, 104, 107, 111 %;
- entra (tc…tc+4): +420, +160, +55, +15, 0 px; escala 111, 106, 103, 101, 100 %;
- shake (tc+5…tc+10): (22, −16) (−17, 12) (12, −9) (−7, 5) (3, −2) (0, 0) px;
- junto: speed ramp curto (CASA rev8: 1× → pico 1,6× no corte, curva 100/50; rev9: 65/65) — ramp NUNCA em fala.
CapCut: posição/escala/shake [MOTOR] (um key por quadro, 16 keys; a 30 fps repetir os valores dá 20 % mais rápido — reamostrar por
tempo), desfoque [CAPTURAR], ramp [CAPTURAR curva de velocidade].

## 3. Punch + flash no corte (CASA build 1, 84,04 s) — só código
`replica_loira.jsx` l. 171–177 (E3): escala 100→135 % nos 4 últimos q24 antes do corte (cam100_10, acelera até o corte) com obturador
360°; Exposição +1,5 no quadro do corte, volta a 0 em 3 q24 no plano seguinte. Medido na referência da loira (12,0–12,2 s).

## 4. Blur transition e whip de ramp (MADALENA, aprovada 12/10) — só código, render no HD
`Aprendizados-SYS\10-acervo-projetos\004-DIGITAL-PRO-CLUB\MADALENA\scripts\03_build.jsx` l. 105–124 (E3): blur = Gaussian 0 → 45 → 0 de tc−6 a tc+6 q24 (cam65); whip = Directional Blur
(ângulo 90°) comprimento 0 → 120 → 0 de tc−4 a tc+4 q24 (cam65), só no pico de um speed ramp.
Reprovado antes: "muita transição com efeito" (13 blur + 4 whips → corte seco na batida, efeito só em 2–3 viradas, C14) e "esse zoom e
essa sacudida" (whip + afastamento digital na tomada seguinte, C10) (`AUDITORIA-PROJETOS.md`, E3).

## 5. Ramp com borrão (ARANTES rev2, coberturas com câmera andando)
Código `ARANTES\scripts\04_build.jsx` l. 70–92 (E3): Time Remap 1× → até 4,5× no corte (ease 45 %), CC Force Motion Blur com obturador
ligado à velocidade (1× = 0°, máx. = 360°). Medido Story 4 q157–159 (corte em q160): nitidez 162 → 108 → 72 → 56 (E1): o borrão só
aparece nos 3 últimos quadros. Só em tomada SEM fala.

## Quando usar qual (regras do Matheus)
- Cinematográfico/institucional: corte seco na batida; efeito em 2–3 viradas; ≤ 5 cortes com efeito em 60 s (C14).
- Reels de construtora com apresentador: whip na entrada de b-roll; corte + peças douradas na entrada de fala.
- Reels de imóvel com apresentadora (CASA): choque em toda troca de cena.
- Sempre: um efeito por tomada (C10); nada de whip/ramp em fala; blur só durante o movimento, nunca residual (C9).
