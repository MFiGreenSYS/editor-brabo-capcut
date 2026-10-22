---
name: capcut-igreen-app-ui-demo
description: Demonstração de app no CapCut para o MKT iGreen (iGreen Connect, iGreen Club, iGreen OS, telas do licenciado e do cliente) nas medidas do Editor Brabo - telas entrando com push e paralaxe, toque com cursor e ripple, digitação, contador com punch, pop de badge, saída quádrupla, zoom no detalhe da tela. Use quando pedirem "mostra o app", "demo do iGreen Connect/Club", "tela do aplicativo no vídeo", "tour pelo app", "print do app animado".
---

# Editor Brabo CapCut · Demo de app

Números: `Aprendizados-SYS/05-herdado-do-after/TRANSICOES-RAMP-TRACKER-UI.md` (App / UI demo). Grafias: iGreen Connect, iGreen Club.

## Montagem
- Material: gravação de tela do app (melhor) ou prints. Gravação de tela entra como clipe; print como imagem com movimento.
- Tela nova entra da direita (posição + escala 0,94 → 1 em 10–12 q `cam65_100`); a anterior sai com paralaxe 30 % para a esquerda
  [MOTOR keys de posição/escala]; fade só se a opacidade por keyframe estiver confirmada.
- Toque: cursor 100 → 82 → 100 % em 4 + 4 q; o alvo afunda a 90–93 %; o estado muda no pico; ripple 100 → 300 % em 12 q
  (cursor e ripple = PNG com alfa [ASSAR] posicionados pelo motor); som de clique no pico.
- Digitação na tela: 1–1,7 q por caractere (frase de valor 2,6 q) + teclado a cada 2 letras.
- Contador (economia, ganhos): conta em 35 q outCubic → punch de 8 % em 10 q; unidade à direita, `R$` menor, sem ",00".
- Pop de badge/notificação: escala 40 → 100 em 5 q com leve overshoot.
- Zoom no detalhe da tela: `zoom` com `rosto_x/rosto_y` = ponto da tela que importa (o motor mantém o ponto parado).
- Leitura: 2–4 palavras pedem 45–60 q; overlap entre telas 5–12 q; saída quádrupla (posição + escala 0,94 + opacidade; blur capturado).
- Rota que se desenha, Dynamic Island, morph de card: [ASSAR] no After/Remotion (Editor Brabo do After) e importar como clipe.
- Dados sensíveis na tela (CPF, telefone, valores reais de cliente): borrar ou usar conta de demonstração — perguntar ao Matheus.
