---
name: capcut-igreen-movimento
description: Movimento no CapCut para vídeos do MKT iGreen - zoom de corte (punch/jump zoom) alternado mantendo o olho no lugar, zoom por keyframe com a curva 65/65 aprovada, pop de elemento, transição-assinatura (tremida + flash, corte no pico), velocidade e speed ramp por curva. Tradução das leis de movimento do Editor Brabo do After para os controles do CapCut. Use quando pedirem "zoom", "punch in", "dá um zoom na fala", "transição mais forte", "tremida no corte", "flash", "acelera", "speed ramp", "keyframe" no CapCut.
---

# Editor Brabo CapCut · Movimento

Leis do After (`00-CEREBRO.md` §3) traduzidas. O CapCut não tem câmera 3D: zoom = escala do clipe. Curva = a curva personalizada
capturada (`esqueletos/curva.json`); sem ela o motor faz key linear e AVISA — linear em movimento visível é reprovado.

> **22/10/2026:** antes desta data a câmera do motor NÃO andava no CapCut (key de vídeo conta o tempo no arquivo, não no segmento; o vídeo
> ficava no último valor). Corrigido no motor; rascunho antigo → `migrar-keys`. Conferir sempre 2 quadros do mesmo corte.

## CÂMERA DO AFTER — o padrão (medido nos renders aprovados, 20/10/2026)
Fichas: `Aprendizados-SYS/06-referencias/CAMERA-*.md` e `TRANSICAO-WHIP-CHOQUE-BLUR.md` (ANTARES, D HAUSS, SANTORINI, ARANTES).
`python -I Aprendizados-SYS/scripts/capcut_brabo.py camera "<projeto>" camera.json` — escreve a trilha principal inteira:
- **Deriva:** toda fala anda +5 % no corte (cam65). "A fala nunca fica parada."
- **Corte na mesma tomada = zoom IN que FICA** ×1,22 em 5 q30 cam40_100, partindo de onde o corte anterior terminou; nunca volta.
  Teto 1,6: ao bater, o corte seguinte vira "tomada nova" (volta à base).
- **Blocos** (assunto novo) = tomada nova: volta à base (100 %).
- **Ênfase** (tese, alerta, número dito): ×1,16 em 17,5 q30 cam65_100 começando 5 q30 ANTES da palavra; segura.
- **Zoom OUT só com motivo** ("eu quero mostrar", muda de assunto, resumo): ×0,85 em 12,5 q30 cam40_100 (o bloco nasce em 1/0,85).
- **Gancho:** começa ampliado (1,5–1,67) e abre para 100 % em 27,5 q30 cam40_100.
- Curvas em 1/escala (a câmera 3D do After anda em distância). Posição = rosto × (1 − escala). Rodar ANTES de `tremida` e `atras`.
- Número atrás da pessoa (construtora, fonte 4K): ×1,77–1,90 em 17,5 q30 cam40_100 — ainda não usado na aula.
- **Blur** só nos quadros rápidos (salto: q1 ~15 % de nitidez, q2 ~45 %; número q4–q8 forte): efeito de desfoque nativo — capturar.
- Whip só na entrada de b-roll, nunca em fala; um efeito por tomada (nada de zoom + sacudida juntos).
O `punch` estático alternado abaixo é a regra antiga do ADV (11/10), superada pela de 17/10.

## Punch (zoom de corte) — antigo (degrau estático alternado)
`python -I Aprendizados-SYS/scripts/capcut_brabo.py punch "<projeto>" --escala 1.10 --a-cada 2 --rosto-y 0.59 --rosto-x -0.045`
- cortes alternados 100 % / 110 %; `--rosto-x/-y` = olho em meia tela (y_px de 1080 → (540 − y)/540): o corte ampliado
  desloca para o olho ficar no mesmo lugar. Rodar o `punch` ANTES do `zoom --lote` (o zoom parte da escala do corte).
- Ênfase forte (número, CTA): 1,20–1,25 só naquele corte. Nunca dois cortes seguidos na mesma escala se há troca de ideia.
- Plano aberto com elemento sobreposto: não dar punch (o elemento sai da grade).

## Zoom de impacto por keyframe (medido e conferido no CapCut 9.5, 20/10/2026)
`capcut_brabo.py zoom "<projeto>" --lote zooms.json` com itens
`{"em": 57.6, "dur": 0.35, "fator": 1.18, "curva": "cam65_100", "rosto_x": -0.045, "rosto_y": 0.59}`.
- O lote é a lista COMPLETA: limpa os zooms antigos da trilha e reaplica (rodar de novo não acumula).
- `fator` multiplica a escala do corte (com punch 1,10 → 1,30); `para` = escala absoluta. Segura até o fim do corte; `volta` (s) volta.
- **Curvas da casa amostradas** a cada 2 quadros (o CapCut só interpola linear entre keys): `cam65` (65/65), `cam65_100`,
  `cam40_100`, `cam100_10`. Não depende de capturar curva.
- **Rosto fixo**: posição = rosto × (1 − escala), em **meia tela** (conferido medindo o quadro: Y −0,09 desceu 50 px em 1080).
  Medir o rosto antes: Haar/YuNet em quadros do bruto → olho em x, y de meia tela (aula ACADEMY M1: x −0,045, y +0,59).
- No JSON: escala uniforme = `KFTypeScaleX` (+ `uniform_scale` ligado); `UNIFORM_SCALE` NÃO anima. Posição = `KFTypePositionX/Y`.
- Push lento de fala: `fator` 1,06 com `dur` = corte inteiro e `curva` linear. Impacto: 1,12–1,20 em 0,3–0,5 s no início da palavra.
- **Conferir no CapCut esperando renderizar**: o player demora 2–4 s para mostrar o quadro novo; captura antes disso mostra o quadro velho
  (foi o que fez parecer que o zoom não funcionava).

## Pop de elemento (número, ícone, logo, print)
3 keys de escala: 0 → 1,08 → 1,00 em ~8 + 6 quadros, curva 65/65; entrada junto com a palavra falada (tempo do whisper).
Saída: escala 1,0 → 0,9 + opacidade 0 em 6 quadros. Fazer no CapCut (guiado com tempos exatos) ou capturar como esqueleto do MODELO.

## Transição-assinatura (uma por vídeo)
| Transição | Receita no CapCut | Quando |
|---|---|---|
| Corte seco na fala | sem efeito | padrão de 90 % dos cortes |
| Tremida + flash | efeito de tremida curto (≤ 0,4 s, pico no quadro do corte) + texto/forma branca 2 quadros a ~15 % + whoosh | troca de bloco (fala → tela cheia) |
| Corte no pico do ramp | Velocidade > Curva: o clipe A acelera até ~3× nos últimos 0,3 s e corta 2–4 quadros depois do pico; B começa no pico | B-roll em movimento |
| Biblioteca do CapCut | só uma escolhida para o vídeo inteiro (ex.: "Feixe aberto", usada no iGreen OS com o clipe a 1,73×) | abertura/fecho |
Pico do efeito exatamente no quadro do corte (1 quadro fora = salto visível). Som no pico, sempre.

## Velocidade
Fala nunca acelerada acima de 1,10× (voz fica artificial); B-roll livre. Câmera lenta só em B-roll gravado em 60 fps.
