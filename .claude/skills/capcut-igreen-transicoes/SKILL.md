---
name: capcut-igreen-transicoes
description: Transições de impacto no CapCut para vídeos do MKT iGreen, nas medidas do Editor Brabo do After - corte escondido no pico, tremida (shake) no corte, flash de 2-3 quadros, choque (push + shake), travessia, speed ramp em b-roll, máscara em degraus, whip; uma ou duas assinaturas por vídeo e som no pico. Use quando pedirem "transição", "transição de impacto", "tremida no corte", "shake", "flash", "speed ramp", "acelera e corta", "whip", "chicote".
---

# Editor Brabo CapCut · Transições de impacto

Números e ranking: `Aprendizados-SYS/05-herdado-do-after/TRANSICOES-RAMP-TRACKER-UI.md` e `LEIS-E-METODO.md` §A (ranking de transições).
Princípio: **corte escondido no quadro de pico** (borrão, flash, energia). 1 q fora do pico = salto visível. Som no pico, sempre.
Padrão da casa: corte seco; efeito só nas viradas de bloco (1–2 assinaturas por vídeo, ≤ 5 cortes com efeito em 60 s). Reels de
apresentador em estilo "CASA" (impacto em toda troca) só se o Matheus pedir esse formato.

## O que o motor faz (CapCut fechado)
| Transição | Comando | Receita |
|---|---|---|
| **Tremida no corte** | `tremida "<proj>" --em 57.6[,110.0] [--amount 43] [--sobe 16] [--desce 14]` | 0 → pico no quadro do corte (subida 16 q acelerando) → 0 em 14 q; posição ±a·1,5 px x (10 Hz) / ±a·0,6 px y; escala +8 % no pico (sem borda preta); somada ao enquadramento/zoom do corte |
| **Flash** | `flash "<proj>" --em 57.6 [--pico 0.5] [--cor white] [--curva …]` | sólido com opacidade quadro a quadro: sobe 1 q antes, pico 3 q, cai 5 q. Alto padrão pico 0,10–0,15; marca forte 0,35–0,6. Flash creme: `--cor #E4D080 --pico 1 --curva 0.85,0.81,0.77,0.71,0.64,0.55,0.40,0.21,0.05,0` |
| **Choque** | `zoom` (fator 1,11 em 6 q) + `tremida --amount 22 --sobe 2 --desce 6` + whoosh | push 100→111 + shake 22→0 px em 6 q |
| **Travessia/zoom-through** | `zoom` cam100_10 no fim de A + `flash` + B chegando de 1,22 com cam40_100 | |
| **Jump cut = zoom IN que fica** | `zoom` fator 1,22 em 0,13 s cam40_100 no início do corte (teto 1,6) | nunca volta |
Som: whoosh 0,12 s antes do pico; impacto no pico; riser antes de virada (skill `capcut-igreen-sound-design`).

## O que falta capturar da interface (lista de captura)
- **Speed ramp** (Velocidade > Curva) — só em b-roll com câmera andando, nunca em fala: rápido 100→500→100 % (subida ≈ 40 % da descida),
  corte 2–4 q depois do pico, B entra em 400–500. Até capturar: fatiar em degraus 100/200/350/500 ou remap com ffmpeg [ASSAR].
- **Máscara em degraus / fatias** (Máscara > Retângulo com keyframe): degraus de 1 q a cada 4–5 q; fatias 3 cópias em 6 q cam40_100.
- **Blur/whip** (efeito de desfoque de movimento) e **modo de mistura** (Diferença) para o flash Difference.
- Transições da biblioteca: escolher UMA para o vídeo (ex.: "Feixe aberto" usada no iGreen OS com o clipe a 1,73×).

## Regras
- Pico exatamente no quadro do corte; conferir quadro a quadro no CapCut (esperar 2–4 s o player renderizar).
- Alto padrão: flash 10–15 %, tremida curta, glow contido; azul elétrico + tremida forte = estética viral (fora da marca iGreen).
- Corte dentro da mesma tomada nunca seco: zoom in que fica. Chicote na entrada de fala é feio.
