# Herdado do Editor Brabo do After — leis de movimento, estilos, linguajar, diretivas e método

Estudo de 20/10/2026 (CLAUDE.md, 00-CEREBRO, REFERENCIA-BASE/Skill-motion-brabo, REGISTRO-DIRETIVAS, LINGUAJAR-MATHEUS, skills
pinça/estudar/replicar/decupagem, agentes analista/diretor/revisor, after-effects-replication-engine), em
`Desktop\Pessoal.SYS\AFTER-EDITORBRABO\`. Tempos em quadros (q) a 30 fps.
Etiqueta CapCut: [MOTOR] o motor escreve · [CAPTURAR] recurso nativo, capturar 1× de projeto feito na interface ·
[ASSAR] gerar em Python/ffmpeg e importar · [SEM EQ.] não existe no CapCut.

## A. As 15 leis de movimento
1. **Analisar antes de animar** (o que existe, principal/secundário, entrada por tipo, quebra do texto, saída que prepara a próxima).
   Texto: de baixo para cima, palavra a palavra, com blur. Forma: scaleX 0→1. Ícone: escala + "back". Fundo: corte seco/opacidade,
   nunca posição. — processo/plano.
2. **Palavra a palavra, nunca a linha.** Stagger 1–4 q (padrão 3; 2 em frase longa; 4–5 em tagline). Entrada "up": sobe 40 px em
   22 q outCubic, opacidade em 60 %, blur 12→0 em 55 %. **Apple (12/10):** blur 24→0, sobe 16 px, escala 106→100 em 8 q; página
   sai com blur em 6 q; serif letra a letra com blur 26 em onda. Digitando (17/10): 1 letra/q, tecla a cada 2 letras.
   — posição/escala/stagger por palavra [MOTOR] (um segmento por palavra); blur [CAPTURAR animação de texto]; letra a letra [CAPTURAR].
3. **Curvas:** toda posição/escala em keyframe velocity, velocidade 0: `cam65` 65/65, `cam100_10`, `cam65_100`, `cam40_100`
   (esta posta à mão por ele). **Nunca 33 %.** Ajuste manual dele é intocável. "velocity 100/50" = sai 100, chega 50. — [MOTOR]
   (curvas amostradas a cada 2 q). `whipIn/whipOut` (spike) só liberado para efeito (tremida, flash, blur).
4. **Blur = velocidade.** Entrada 10–14→0 linear, mais curta que a posição; saída 0→15–20 (explosiva 25–30); parado = 0, nunca residual.
   — blur de texto [CAPTURAR]; blur de vídeo [ASSAR] (ou efeito capturado).
5. **Stagger é lei.** Palavras 1–4 q, saída 2 q, elementos grandes 2–6 q; ordem de saída = ordem de entrada. — [MOTOR].
6. **Direções opostas** (← ↑ → ↓; nunca repetir a direção em trocas seguidas). — [MOTOR] + plano.
7. **Zero quadros vazios:** overlap 5–12 q; início = início anterior + duração − overlap; quem sai fica acima. — [MOTOR].
8. **Fundo em corte seco**, 3 camadas (base + radial 3–5 % respirando + ruído 3–6 %), deriva −3 a −5 %/s nos holds. — fundo [ASSAR], deriva [MOTOR].
9. **Saída quádrupla:** posição inExp 1200 px em 15–20 q + blur 0→15–25 + opacidade a partir de 35–50 % + escala 1→0,94.
   "Fade puro = amadorismo." — posição/escala/opacidade [MOTOR]; blur [CAPTURAR/ASSAR].
10. **Layouts diferentes** entre cenas seguidas; no vertical o split vira pilha e a tipografia cresce 20–33 %.
11. **Tempo de leitura:** 2–4 palavras = 45–60 q; 5–8 = 60–75 q; 9–12 = 75–105 q. Entrada q0–22, dentro anima 5–8 q depois, saída nos
    últimos 15–20 q. CTA hold ≥ 2–3 s. Máx. 3 níveis de texto. Respiro vertical ≥ 80 px em cima/baixo, ≥ 40 px dos lados.
12. **Overshoot só no estilo que pede** (a: nenhum, ≤ 5 % em ícone). — [MOTOR] com mola amostrada.
13. **Zoom:** peça gráfica = câmera 3D com DOF [SEM EQ.]; vídeo = escala com o olho parado [MOTOR]. Fala parada > 2–3 s = zoom.
    IN cam65 ~10 q até ~122 %, OUT até ~104 % antes do corte. Fala: 1,10–1,26. Número com ênfase 1,0→2,7 em 14 q cam40_100.
    **Jump cut = zoom IN que fica** ×1,22 em 4 q cam40_100, teto 1,6 (nunca volta). Joseph: push lento sempre + punch seco ×1,2–1,3.
    Enquadramento aprovado (18/10): rosto em y 700–780 de 1920.
14. **Choque** (transição de impacto): speed ramp + chicote + push 100→111 + shake 22→0 px em 6 q. Ramp nunca em fala. — push/shake [MOTOR],
    ramp [CAPTURAR curva de velocidade], borrão [ASSAR].
15. **Som acompanha o movimento:** whoosh −12/−14 dB com pico no quadro mais rápido; textura −9/−11 no evento; teclado −14; riser −10 +
    sub −13 nas viradas; whoosh de jump cut −24. 20+ sons diferentes em 40–60 s. Pico ≤ −1 dBFS, voz ≥ 12 dB acima. — [MOTOR].

**Ranking de transições** (referências): 1 morph de container [ASSAR] · 2 objeto-ponte [ASSAR] · 3 corte seco com fundo contínuo [MOTOR] ·
4 câmera virtual/plano-sequência [MOTOR] · 5 match-cut/zoom-through (novo plano começa em 300 %) [MOTOR] · 6 wipe por forma
[CAPTURAR/ASSAR] · 7 whip/push 900–1200 px (entra 8 q, sai 20–25 q) posição [MOTOR] + blur [ASSAR] · 8 blur-cut/rack focus
(escala 115→100 + blur 30→0 em 8 q) [CAPTURAR] · 9 flash (sobe 4 q, pico 3, cai 5; corta no 1º q do pico) [MOTOR com sólido + opacidade] ·
10 flip 3D [SEM EQ.] · 11 blob [ASSAR] · 12 fade só no fechamento [MOTOR].
**Decidir com o Matheus por formato:** cinematográfico = corte seco na batida, efeito em 2–3 viradas, ≤ 5 cortes com efeito em 60 s;
reels de imóvel com apresentadora (CASA 18/10) = transição de impacto em toda troca.

## B. Estilos (escolher por cena; UMA família por vídeo, ≤ 2 transições-assinatura)
- **(a) Brabo:** ease-out forte + blur, sem overshoot (outCubic 22 q, blur 12–14→0 em 13–14 q, stagger 3, saída inExp 14–20 q; versão
  comercial: entradas 6–10 q ease-out 80–90 %, saídas 3–7 q). Marca, explainer, narrativa — **padrão iGreen**.
- **(b) UI premium (mola):** ataque 7–8 q, overshoot +7–9 % (card até 16 %), undershoot −2 a −3,5 %, assenta em 22–29 q.
- **(c) Viral clean SaaS:** keys lineares 3–5 q + overshoot (3 q 32 %, 4 q 24 %, 5 q 19 %), câmera bezier 73–76 %.
- **(d) Easy ease alta:** ~69 % dos dois lados; move 10 q, segura 5 q; listas e toggles.

## C. Linguajar do Matheus (termo → o que ele quer)
pinça = agulha (ou pino indicador em "mask e pinça apresentando X") · esquilo = skill · "zoom in que fica" = aproxima no corte e não
volta · "câmera baixa demais / sobrando em cima" = rosto para y 700–780 · "câmera torta" = centralizar · "grade de segurança" =
y 420–1500, x 32,5–1047,5 · "atrás da cabeça" = texto entre o fundo e o recorte · "pregado" = rastreado na superfície ·
"fundo opaco" = escurecer o cenário inteiro por igual, nunca placa · "ficou top/excelente" = aprovado, vira modelo ·
"ficou uma bosta / nada a ver com a dinâmica" = refazer, não remendar · "isso deve ser regra" = registrar e aplicar já ·
"a dinâmica" = manchete viva só com a pessoa em quadro · "transição" (sem nome) = impacto (ramp + chicote + blur + push + shake) ·
"ela aparece por trás dando profundidade" = palavra grande atrás da cabeça, escala 150→100 + desfoque ·
"não fique em cima da cabeça, com profundidade atrás, mais acima" = abrir o texto em volta da cabeça, atrás do recorte ·
"palavras atrás dela… que dê leitura" = a cabeça cobre só o pé das letras · "abaixo do busto, centralizado" = legenda pequena x 540,
y ~1120 · "melhore a disposição das letras" = apoio centrado + palavra grande embaixo, uma manchete por plano ·
"camera 3d zoom in e out dinamic" = IN ~10 q até ~122 %, OUT até ~104 %, cam65 · "as letras da forma que está" = não mexer no texto ·
"ajustei lá, não mexa" = preservar · "quando não tiver ela falando, aumente o fundo musical" = música +10 dB nos silêncios ≥ 0,6 s,
rampas 8–10 q · "quando tiver falando… nunca muta" = música −19 dB sob voz, −7 dB nos respiros · "as cenas devem bater com os picos"
= entrada da música com os picos nos cortes · "faça um corte até aqui / comece no '…'" = ripple delete sem comer palavra ·
"Sony um / Sone um" = "põe um".

## D. Diretivas que valem em qualquer ferramenta (datas)
24/09 não alucinar; entender, estruturar, perguntar; blur só em movimento · 24/09 editar só o que ele apontou; tempos combinados antes ·
25/09 curvas da casa, nada de 33 %, manual dele intocável, não exportar sem pedir · 11/10 técnica pelo material; marca de corte dele
vale; rosto centralizado; zona segura; última repetição é a correta; texto nunca no rosto; texto = palavra falada; card cinza com letra
amarela reprovado; sons variados; Reels talking head = fórmula Joseph (sem letras gigantes atrás como BASE, sem cards de frase, sem filtro
azul) · 12/10 página = frase inteira; entrada Apple; linha ≤ 880 (760 com fonte larga); plano editável antes de todo projeto; voz −19,5 LUFS ·
12/10 corte seco na batida como padrão, efeito em 2–3 viradas; nunca repetir cena; marca = logo oficial · 12/10 fala parada > 2–3 s leva
zoom; **proibido véu preto esfumaçado** (fundo de leitura = desfoque em degradê + cinza, abaixo do texto); texto que termina no corte sai
seco · 13/10 comparar com o último estado antes de reconstruir; imagem de banco só gratuita com print antes · 15/10 entrada Apple já no 1º
build; pílulas em vidro "liquid glass"; usar o máximo do bruto · 17/10 voz nunca cortada; texto atrás dele, no alto; digitando com som de
teclado; **nunca placa ou sombra preta atrás de texto**; corte na mesma tomada nunca seco (= zoom in que fica); recorte nunca corta a
cabeça; chicote na entrada de fala é feio; SFX: whoosh = movimento, textura = evento, riser + hit = virada; CTA = botão + cursor ·
18/10 manchete grande só com a pessoa em quadro; edição pela pinça; música sobe nos silêncios · 19/10 picos da música nos cortes,
ducking −19/−7, instrumental.

## E. Método → CapCut
- **Pinça/edição guiada:** marcador ou timecode → `raio-x` dos segmentos no intervalo → backup → escrever só neles por id → novo raio-x
  provando que o resto não mudou → prova visual (quadros), export só com ok.
- **Estudar referência:** medir número, nunca adjetivo; ficha por técnica (lógica, quando NÃO usar, material, receita com números e
  quadro-prova, o que é script e o que é clique, upgrade pelas leis, gatilhos) **+ coluna de etiqueta CapCut**; curva da referência
  traduzida para as 4 aprovadas.
- **Replicar efeito:** medir quadros e fases → decompor (forma, textura, luz, câmera, revelação) → texturas/partículas [ASSAR] como MOV/PNG
  com alfa → motor posiciona e anima → amarrar à fala → versões quando houver dúvida de gosto.
- **Engine de replicação (8 etapas):** preparação → auditoria por vídeo (inventário, cortes por fluxo óptico, eventos) → síntese em 5
  classes (fixo/recorrente/contextual/exceção/desconhecido) → spec (campo indeterminado = null) e plano aprovado → construção → piloto →
  validação P0–P3 → entrega com limitações. Evidência E1 medido · E2 visto · E3 inferido · E4 desconhecido. Correlação ≠ causa.
  "2D simples que reproduz > 3D complexo." Tempo antes de cor; nunca aprovar por SSIM global; gancho e fecho pesam mais.
- **Agentes:** analista (mede, não anima) · diretor (plano cena a cena com quadros/curva/motivo, uma família, ≤ 2 assinaturas, marca
  [CAPTURAR] como lista de captura antes do build) · revisor (BLOQUEIA / DEVE CORRIGIR / PODE MELHORAR, sempre com prova).
  Versões CapCut em `.claude/agents/capcut-*.md`.

## F. O revisor reprova
curva fora das 4 ou 33 % · manual dele desfeito · edição fora do pedido · texto entrando por linha · stagger fora de 1–4 q · saída que não é
quádrupla · quadro vazio entre cenas · direção repetida · layout igual ao anterior · blur parado/residual · fala parada > 3 s sem zoom ·
texto fora da grade/linha > 760/no rosto · palavra não falada · página que quebra a frase ou termina em o/de/em/a · palavra sozinha ·
grafia errada · placa ou véu preto atrás de texto · cor fora da paleta · nome digitado no lugar da logo · emenda que come/repete palavra ·
voz da equipe · último corte sem 0,4–0,8 s de rabo · loudness fora · pico > −1 dBFS · voz < 12 dB acima · SFX repetido · mais de um efeito
na mesma tomada · ramp em fala · assinatura repetida de outro projeto. **Não entrega com BLOQUEIA aberto.**
