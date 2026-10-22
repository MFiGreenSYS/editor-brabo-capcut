# CÉREBRO · Editor Brabo CapCut (MKT iGreen)

O destilado. Números medidos têm a fonte; "proposta" = ainda não aprovado pelo Matheus (confirmar no 1º projeto e promover).

> 22/10/2026 · Som curto (click/pop) some embaixo da voz se não ficar ~+5 dB acima dela no instante: nivelar pela voz (`nivelar-sons`).

## 1. Ritmo (herdado do Editor Brabo, medido em 447 cortes do Matheus e na fórmula viral aprovada)
- Corte de fala: pausa ≥ 0,40 s sai; saída = fim da voz + 80 ms; entrada até 1 quadro antes da voz, nunca depois; nenhuma pausa
  interna > 0,50 s; fica o ÚLTIMO take completo. Detalhes: skill `capcut-igreen-decupagem`.
- Troca de "cena" (corte, punch, B-roll, tela cheia) a cada ~3,5 s; nada parado > 7 s. Gancho nos 2 primeiros segundos.
- Último corte ganha 0,4–0,8 s de rabo neutro antes da assinatura.
- Um efeito-assinatura de transição por vídeo; o resto é corte seco na batida/na fala.

## 2. Legenda (proposta de marca sobre a regra medida da fórmula viral)
Regra medida (fórmula viral): página = frase de 3–7 palavras, nunca termina em o/de/em/a/que/pra/com…, nunca uma palavra
sozinha, linha ≤ 760 px centrada, texto em y 420–1500, nunca no rosto. Destaque = 1 palavra de valor por página, no máximo.
Proposta iGreen: Inter ExtraBold (800) `#F2FFF0`, ~50 px em 1080 de largura (no CapCut ≈ tamanho 8–9, conferir no MODELO),
destaque em `#18FF00` (fundo claro: `#0B7A00`), sombra preta suave (opacidade ~60 %, desfoque alto, distância 0) em vez de
contorno grosso; entrada curta com desfoque/subida (~0,25 s); posição: abaixo do queixo, centro em y ≈ 1250–1350.

## 3. Movimento no CapCut (tradução das leis do After)
| After (regra da casa) | CapCut |
|---|---|
| keyframe velocity 65/65, velocidade 0 | keyframe com **curva personalizada** equivalente; capturada do MODELO (`esqueletos/curva.json`) e reaplicada pelo motor |
| câmera 3D com DOF no zoom | não existe: escala por keyframe 65/65 no clipe + (proposta) desfoque no fundo quando o destaque é um elemento sobreposto |
| pop = 3 keys (0 → 108 % → 100 %) | 3 keys de escala no elemento (0 → 1,08 → 1,0) |
| palavra a palavra, nunca linha | legenda por frase com entrada curta; palavra-chave pode entrar 2–3 quadros depois |
| shake + flash no corte | efeito de tremida curto (≤ 0,4 s) + flash branco 2 quadros no ponto do corte; whoosh no pico |
| zoom de corte (jump) | `punch`: cortes alternados 100 % / 112 %, olho no mesmo lugar |

Câmera MEDIDA nos renders aprovados do After (20/10, fichas `06-referencias/CAMERA-*.md` e `TRANSICAO-WHIP-CHOQUE-BLUR.md`): fala sempre em deriva cam65 (+3 a +7,5 % no plano, começa antes do corte); corte na mesma tomada = zoom IN que FICA ×1,22 em 5 q30 cam40_100 (teto 1,6, nunca volta); número atrás ×1,77–1,90 em 17,5 q30 cam40_100 começando 5 q30 antes da palavra; zoom OUT só com motivo (abrir nos dois ×0,61 em 15 q30; afastar ×0,85–0,92); motion blur só nos quadros rápidos. **Conflita com a linha "zoom de corte (jump)" acima (alternado 100/112 seco): pendente de decisão do Matheus.**

## 4. Som — medido no projeto CapCut "1001" (finalização do iGreen OS Capa, 01–02/10/2026, 146 s)
16 trilhas de áudio, ~85 segmentos ≈ **35 SFX por minuto**. Narração (voz "Sol") picotada em frases com respiro para o visual.
| Som | Volume no CapCut | ≈ dB | Onde |
|---|---|---|---|
| Woosh 01 | 0,554 | −5 | toda troca/entrada de tela (recorrente) |
| Woosh 02 | 1,0 | 0 | trocas maiores |
| Whizzing | 0,431 (1,25 no clímax) | −7 | abertura e viradas |
| Click mouse | 2,853 | +9 | cliques de UI |
| Keyboard typing | 1,0–2,3 | 0 a +7 | texto sendo digitado |
| Pop-up | 0,28–0,38 | −11 a −8,5 | cada item que aparece, ~0,9 s entre eles |
| "Correct answer" | 0,20–0,28 | −14 a −11 | check/ok |
| Game Win | 1,0 | 0 | momento de conquista |
| Riser | 1,0 (vel. 1,72×) | 0 | antes do fecho |
| Trilha (Uplifting Electronica) | 0,069 | −23 | cama contínua, fade in 1,2 s / out 7,1 s |
Também: filtro "Granulação vinho" a 30 % no vídeo todo; transição "Feixe aberto" num corte com velocidade 1,73×; trecho em 0,58×.
Conversão: dB = 20·log10(volume). Alvo de mix: voz −19,5…−16 LUFS, pico ≤ −1 dBTP, voz ≥ 12 dB acima do fundo.

## 5. Formato e entrega
Reels/Stories 1080×1920, 30 fps, H.264, MP4, AAC. Feed 1080×1350. Wide 1920×1080. Nome do export: `DD-MM-AAAA_Projeto_vN.mp4`
em `PROJETOS/<projeto>/export/`.

## 6. O que o motor sabe do CapCut 9.5 (detalhes em `03-capcut/FORMATO-DRAFT.md`)
Rascunho = JSON aberto; duas cópias (raiz e `Timelines/<id>/`); tempo em microssegundos; posição normalizada (0 centro, ±1 borda,
y + para cima). Estilo de texto/animação/curva: capturar de um rascunho real (MODELO iGreen) em vez de inventar o JSON.
