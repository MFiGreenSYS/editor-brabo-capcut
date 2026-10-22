# Herdado do After — transições de impacto, speed ramp, tracker, imobiliário/construtora, app/UI

Estudo de 20/10/2026 das skills brabo-transicoes-impacto, brabo-speed-ramp, brabo-tracker-destaque, brabo-imobiliario,
brabo-replica-construtora, brabo-app-ui-demo e fichas (011-imobiliario 07/09/10, 00-CEREBRO §6, MODELO-REELS-CONSTRUTORA,
SINTESE-REPLICA-CONSTRUTORAS) em `Desktop\Pessoal.SYS\AFTER-EDITORBRABO\`. 30 fps.

## Transições de impacto
Princípio: toda transição forte é um **corte escondido no quadro de pico**; 1–2 transições-assinatura por vídeo; som no pico; 1 q fora do
pico = salto visível.
| Transição | Números (After) | CapCut |
|---|---|---|
| Shake + flash | Amount 0→43 em 16 q, pico 1 q no corte, volta em 14 q (KV 90/90); tremida = posição ±a·1,5 (x) / ±a·0,6 (y), escala 100→104→100, bordas espelhadas, saída 120–150 %; flash branco em Difference 2 q | tremida [MOTOR] (`tremida`: keys de posição/escala quadro a quadro) ou [CAPTURAR Efeitos > Tremer]; flash [MOTOR] (`flash`: sólido branco com opacidade) |
| Choque (CASA) | ramp + chicote (obturador 360°) + push 100→111 + shake 22→0 px em 6 q | push/shake [MOTOR], ramp [CAPTURAR], borrão [ASSAR] |
| Máscara em degraus / fatias | degraus a 1 q a cada 4–5 q, feather 0; fatias: 3 cópias, faixa em 6 q cam40_100 | [CAPTURAR Máscara > Retângulo com keyframe] |
| Pessoa desaparecendo | sumiço em ~6 q; Turbulent Displace −103/98/10; Deep Glow; tint 0→23 % | [SEM EQ.] (versão: recorte + glow + tremida + flash + corte para placa vazia) |
| Travessia pelo logo | câmera cam100_10 + flash da cor; próxima cena chega de 22 % cam40_100 | zoom [MOTOR] + flash [MOTOR] |
| Flash creme (construtora) | #E4D080 opacidade 85,81,77,71,64,55,40,21,5,0 % (9 q) a partir do corte | [MOTOR] `flash --cor` com a curva |
Alto padrão: flash 10–15 %, tremida curta, glow contido (Radius 250–400, Exposure 0,2–0,4). "Muita transição com efeito" = ruim: whip
em metade dos ramps. **Conflito a decidir por formato:** CASA (impacto em toda troca) × réplicas de construtora (quase tudo corte seco).

## Speed ramp
Só em câmera andando (nunca câmera parada, take tremido, pessoas andando, direções opostas, nunca em fala). Rápido 100→500→500→100 %
com keys lineares (tutorial: subida 10 q, patamar 17, descida 13); regra da casa: subida ≈ 40 % da descida. Lento 100→30→30→100 só com
fonte ≥ 60 fps. Transição: A acelera e corta 2–4 q depois do pico; B entra em 400–500 e volta a 100. Borrão 0° a 100 % → 326° a 500 %.
Fonte consumida = ∫v dt (rampa linear 100→V em r s consome r·(100+V)/200 s). Nunca Pixel Motion Blur/Echo. Estabilizar tremido (vidstab).
CapCut: [CAPTURAR Velocidade > Curva] · aproximação [MOTOR] fatiando em degraus 100/200/350/500 · remap exato [ASSAR ffmpeg] ·
borrão [ASSAR tmix] · lenta suave [CAPTURAR fluxo óptico].

## Tracker / destaque preso
Um destaque por plano; precisa de paralaxe e textura. Rastreio planar em Python (Lucas-Kanade + homografia RANSAC) → 4 cantos por quadro.
Número ancorado entra em 12 q com blur 12→0; caixa de linhas ~35 q stagger 3; contorno ~40 q com o fora escurecendo 0→50 %.
Rótulo pregado na superfície real; sem superfície boa = centrado e fixo; letreiro pequeno no canto é "feio"; placa preta atrás proibida.
CapCut: texto seguindo ponto 2D [ASSAR rastreio → keys de posição/escala/rotação, que o MOTOR escreve] ou [CAPTURAR Rastreamento];
perspectiva/corner pin, contorno que se desenha, holograma [ASSAR] (queimar no clipe); 3D Camera Tracker [SEM EQ.].

## Imobiliário / construtora (estrutura útil para anúncio iGreen)
Arco: gancho → apresentador → transição de impacto → tour/prova → número no lugar → CTA. Técnica pelo material.
D1 contador na frente sobre o peito · D2 nome gigante atrás e acima da cabeça (fundo 20–25 % só no cenário, apoio ≥ 50 px Medium) ·
D3 número com ênfase = número grande atrás + zoom 1,0→2,7 em 14 q cam40_100 fora da cabeça · D9 jump cut = clique + zoom IN que fica ×1,22
em 4 q, teto 1,6 · D10 letreiro digitando 1 letra/q + teclado · D12 rosto em y 700–780 · D13 duas pessoas: centrar quem fala ·
D16 textos empilhados conferidos em todas as keys · D17 letreiro no canto vira centrado.
Construtora: um dono do corte (batida OU palavra); corte 1–2 q depois do ataque da batida; letreiro herói 45–72 % da largura entrando por
caractere em 8 q, sai seco; nenhum plano começa parado; tudo estabilizado; fechamento: escurece 23 q + logo em 14 q; música duck ~6 dB,
−14 LUFS; nada de piscar 1 q (pulso 100→40→100 em 3 q).

## App / UI demo (iGreen Connect, iGreen Club, iGreen OS)
Tela nova entra da direita; a anterior sai com paralaxe 30 % + fade; toque = cursor 100→82→100 em 4+4 q, alvo a 90–93 %, estado muda no pico,
ripple 100→300 % em 12 q; digitação 1–1,7 q/caractere (frase de valor 2,6); contador 35 q outCubic → punch 8 % em 10 q; pop de badge
40→100 em 5 q; 2–4 palavras pedem 45–60 q; overlap 5–12 q; saída quádrupla.
CapCut: push de telas, pop, clique, zoom [MOTOR] (prints/vídeos de tela como mídia + keys); fade [MOTOR se opacidade confirmar]; blur de
saída [CAPTURAR]; rota que se desenha, Dynamic Island, morph de card [ASSAR no After/Remotion e importar].

## Ranking para o MKT iGreen (aula, reels de licenciado, anúncio)
1 jump cut = zoom IN que fica [MOTOR] · 2 palavra de valor atrás da pessoa [MOTOR `atras`] · 3 shake + flash no corte de bloco (1–2 por
vídeo) [MOTOR `tremida`/`flash`] · 4 número dito com ênfase = zoom rápido + contador [MOTOR] · 5 letreiro digitando + teclado
[CAPTURAR máquina de escrever ou MOTOR letra a letra] · 6 speed ramp só em b-roll andando [CAPTURAR curva].
