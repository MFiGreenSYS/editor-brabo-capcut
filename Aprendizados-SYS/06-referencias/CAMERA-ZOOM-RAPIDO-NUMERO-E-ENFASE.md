# Ficha · Câmera: zoom rápido de impacto (número atrás) e push de ênfase (palavra-chave)

Estudo de 20/10/2026. Método, fontes, evidência e conversão q24→q30: ver `CAMERA-DERIVA-PUSH-LENTO.md`.

## Lógica
- **Número da fala com o número gigante atrás da pessoa** ("referência aprovada de dinâmica: a garagem do Santorini", 17/10): zoom
  rápido e alto (×1,77–1,90) que começa 4 q24 (5 q30) ANTES da palavra do número e assenta 10 q24 (12,5 q30) depois; antes e depois,
  deriva cam65. Não volta: o plano termina no zoom alto. Só com fonte 4K (teto 2,4; fonte 1080 ≤ 1,5 — README do modelo, E3).
- **Push de ênfase** (talking head ADV/PEDRO, palavra-destaque marcada `push`): ×1,16 em 14 q24, cam65_100, começa 4 q24 antes da
  palavra e segura até o fim da peça (`plano_reel.py` l. 30, 257–260, E3). Render no HD (não medido, E4 no render).
- **"Câmera 3D zoom in e out dinâmico"** (CASA, pedido do Matheus 18/10): IN rápido quando o número/palavra grande entra, OUT antes do
  corte (ver `CAMERA-ZOOM-OUT-E-ALTERNANCIA.md`).
- Quando NÃO: frase sem dado/tese; dois zooms rápidos colados; com whip/ramp na mesma tomada (C10); fonte 1080 acima de 1,5.

## Receita medida (número atrás)
| Prova | Escala | Duração | Curva (RMSE) | Nitidez | Âncora |
|---|---|---|---|---|---|
| ANTARES q569–583 ("2" vagas) | 130,0→229,9 % (×1,77) | 14 q24 = 17,5 q30 | cam40_100 2,7 % (cam65_100 8,9) | 177 → 17 no q573 (10 %); só volta a 65 (37 %) | (596, 904) fixa |
| D HAUSS q814–828 | 125,0→229,9 % (×1,84) | 14 q24 | cam40_100 5,8 (cam65_100 6,6) | 303 → 35 (12 %) | (252, 768) fixa |
| SANTORINI q1067–1081 | 130,5→248,6 % (×1,90) | 14 q24 | cam65_100 2,9 (cam40_100 5,8) | 73 → 16 | (642, 882)→(617, 899) |
Progresso ANTARES por quadro (q24): 0 · 0,03 · 0,11 · 0,33 · 0,52 · 0,66 · 0,75 · 0,83 · 0,89 · 0,93 · 0,96 · 0,98 · 0,99 · 1 (E1).
Antes: deriva 125→130 % (cam65, 31 q24). Depois: 230→240 % (cam65). Build ANTARES: fases `[[-10,1.25],[fz-4,1.3],[fz+10,2.3],[nq,2.4]]`,
curvas cam65 · cam40_100 · cam65, alvo = (rosto x, rosto y + 150) (`ANTARES\scripts\07_textos.py` l. 111–114, E3); SANTORINI começa em
1,35 ("rev3: começa maior, aparecia pequeno e baixo", `SANTORINI\scripts\07_textos.py` l. 110, E3).
Quadro-prova: `estudo_camera\saidas\prova_A_numero_566_583.jpg` (scratchpad).

## Tabelas CapCut (30 fps, relativo ao início do movimento, modelo 1/escala)
- Número ×1,77, cam40_100, 18 q30 (q a q): 100,0 · 100,3 · 101,7 · 105,2 · 114,4 · 128,5 · 139,6 · 148,0 · 154,6 · 159,9 · 164,2 ·
  167,7 · 170,5 · 172,7 · 174,4 · 175,6 · 176,4 · 176,9 · 177,0 %.
- Push de ênfase ×1,16, cam65_100, 18 q30: 100,0 · 100,0 · 100,2 · 100,4 · 100,9 · 101,9 · 104,2 · 109,0 · 111,5 · 112,9 · 113,9 ·
  114,5 · 115,0 · 115,4 · 115,6 · 115,8 · 115,9 · 116,0 · 116,0 %.
- Em zoom grande (×1,77) a interpolação em 1/escala (After) difere da escala direta: RMSE 1,0 % contra 2,4 % (E1) → amostre a tabela.

## Blur [CAPTURAR: desfoque de zoom/movimento do CapCut]
Medido (ANTARES): nitidez 177 · 144 · 67 · 25 · 17 · 20 · 24 · 27 · 32 · 37 · 42 · 48 · 56 · 60 · 65 de q569 a q583 (E1): borrão máximo
no 4º–5º quadro (o mais rápido), cai devagar até o fim. Depois do zoom o quadro fica em ~37 % da nitidez anterior (fundo desfocado +
ampliação 2,3× do 4K; causa exata E4). No CapCut: desfoque forte em q4–q8 do movimento (30 fps), médio em q9–q13, nada depois.

## Som
Whoosh −12 dB no MEIO do movimento (média de fases[1] e fases[2]; comentário "pico no quadro mais rápido"; ANTARES `07_textos.py` l. 194, E3); push ADV: whoosh em 37 % do movimento
(`plano_reel.py` l. 463–464, E3). "Punch seco não leva som" (SINTESE 012, E3).

## Frequência
ANTARES (59,6 s): 1 zoom de número + 1 zoom IN que fica; o resto é deriva (E1). D HAUSS (90 s): ~12 movimentos rápidos ≈ 1 a cada
7,5 s, contando in/out de alternância (E1). Talking head: "1 push a cada 2–3 frases" (SINTESE 012, E3).

## Gatilhos
"número atrás", "zoom rápido e alto", "dá um zoom quando falar isso", "ênfase", "punch-in", "câmera 3D zoom in e out dinâmico".
