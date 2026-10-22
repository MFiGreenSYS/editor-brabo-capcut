# Herdado do After — texto atrás da pessoa, legenda/texto estilo Apple, fórmula viral e dinamismo

Estudo de 20/10/2026. Fontes (em `Desktop\Pessoal.SYS\AFTER-EDITORBRABO\`): skills apresentador-reels, formula-viral-reels,
reels-talking-head, narracao-sync; `03-analise-videos\011-imobiliario\10-reels-virais-imobiliario.md` (F10), `SINTESE-IMOBILIARIO.md`
(SIM), `014-yt-reels-imobiliario\01/02` (E01/E02), `013-viral-reels-ai\` (SVR, DISSECACAO, FICHA-JOSEPH), `00-CEREBRO.md`,
`09-auditoria-projetos\` (CHECKLIST, AUDITORIA, CRIVO-LETREIROS), `scripts\formula_reels.jsx` (FR). 30 fps; px em 1080×1920.

## 1. TEXTO ATRÁS DA PESSOA (receita medida)
**Camadas (de cima para baixo):** textos da frente (legenda, CTA) → **pessoa recortada** (cópia do take) → **textos de trás** →
sólido preto 20–25 % só no cenário (entra em 8 q, sai com a palavra; 45 % ficou "muito opaco"; nunca placa) → take original.
**Recorte:** Object Matte Feather 5, Contrast 80 % · MODNet suavizado no tempo · matte apertado com erosão de 3 px, **sem desfoque no
cenário** (camisa clara vaza em aura) · funciona com fundo de luminância mediana (~99) atrás da cabeça; céu claro (~226) falha.
**Posição:** atrás da **cabeça** (rosto esconde ~15 %, tronco ~45 %; cobertura ≤ 30 %). Base da palavra ≈ topo da cabeça + 30–75 px
("a cabeça cobre só o pé das letras"); se a cabeça esconde uma letra inteira, suba. Sem espaço: desça a pessoa com zoom preso no topo, ou
abra o bloco à esquerda e à direita da cabeça (vão do tamanho da cabeça). Rosto > ~35 % da largura → a palavra de trás vira contador NA
FRENTE, sobre o peito. Largura × zoom de pico ≤ ~980 px (com zoom 118 %, palavra ≤ 700–720 px).
**Tipografia:** modelo Shadow 3 linhas **1 : 1,8 : 1,17** (138/248/160 px): sans bold · sans bold gigante · serif itálica. Casa: Inter
700–800 + serif itálica. Modelo Videotrix: herói ≈ 213 px, tracking −24, 61–70 % da largura, topo em y 418–464; apoio serif ≈ 93 px
(2,3 : 1). **iGreen:** Inter (a marca proíbe outra fonte) — apoio Inter 800 + herói Inter 900; verde #18FF00 só no herói.
**Cor/halo:** Shadow = branco em Difference + sombra preta 100 %, distância 0, suavidade 671 (halo gigante); Difference some em
luminância 45–55 % e vira ciano em fundo claro (vetado) → branco normal + halo. Halo da casa: distância 0, suavidade 50, 35–40 % em fundo
liso; 81 % com suavidade ~94–107 px em fundo cheio de detalhe.
**Tempos:** bloco de 44 q, linhas em +0/+8/+23 q (padronizar +0/+8/+16), palavras com stagger 2 q (~15 q cada), troca seca entre blocos;
upgrade da casa: blur 12→0 em 55 % da entrada; "aparece por trás dando profundidade" = escala 150→100 + desfoque.
**Zoom de impacto junto:** 1,66× → 1× em ~58 q (cam40_100), segura até q80, push-in de 6 % até q125. Som: riser + impacto na entrada,
swoosh na saída.
**Regras de uso:** é MOMENTO, 3–5 por minuto no máximo; não é base do vídeo (fórmula Joseph); manchete grande só com a pessoa em quadro;
nome/empreendimento no alto, centrado; nunca placa preta atrás do texto.
**No CapCut:**
- [MOTOR] `capcut_brabo.py atras <proj> atras.json --midia <brutos>`: letreiro na trilha «Brabo · Atrás texto» + pessoa recortada
  (MODNet → ProRes 4444 com alfa, `recorte_pessoa.py`) na trilha «Brabo · Atrás pessoa», com a escala/posição/keys do corte e volume 0.
  Camadas: vídeo → texto atrás → pessoa → legenda/letreiros.
- [CAPTURAR] alternativa nativa: duplicar o clipe + "Remover plano de fundo" (bloco `matting` do material: `flag`, `path`,
  `mask_video_path`) — capturar 1× para o motor clonar (melhor borda, editável no CapCut).
- [CAPTURAR] halo (sombra do texto distância 0, desfoque alto) e modo de mistura "Diferença" (se existir na versão).
- [ASSAR] plano B exato: compor o trecho inteiro em Python (fundo + texto com halo/Difference + pessoa) e importar como clipe.

## 2. TEXTO / LEGENDA ESTILO APPLE (receita medida, FR)
**Legenda da fórmula:** sans 50 px #F3F3F3 + serif 108 px (2,2×) na cor de destaque; passo 64/112; linha ≤ 760 px (fonte larga).
Joseph: sans 44–52, serif 100–110; nunca abaixo de y ~1460; o texto inteiro nunca leva > 1,5 s para entrar.
Topo do bloco por modo: UI/gancho 1110 − altura · meia tela 1000 · topo 470 · base 1470 − altura · abaixo da pílula 1312 · stories até 1400.
**Entrada de cada palavra ("sai do blur"), 8 q a partir do início da palavra** (ou até 6 q antes do fim da página; no WTC 3 q antes):
âncora no centro da palavra · posição y +16 → 0 cam65_100 · escala **106 → 100 %** cam65_100 · opacidade 0 → 100 em **5 q** linear ·
Gaussian **24 → 0** cam65_100 · sombra 45 %, distância 2, suavidade 14.
**Serif letra a letra:** por caractere opacidade 0, y +22, blur 26, Ramp Up; duração min(1,2 s, max(8 q, letras × 1,4 q)) cam65_100;
glow = 2 sombras coloridas distância 0 (70 %×0,8 suav. 13 e 45 %×0,8 suav. 36).
**Saída da página:** últimos **6 q**, opacidade 100 → 0 e blur 0 → 18, linear. Texto que termina junto com o corte fica nítido até a
última sílaba (sai seco).
**Pílula de vidro (UI):** 494×140, x 293–787, y 1150–1290; #141518 a 90 %; contorno branco 1,5 px 12 %; raio min(32, h/2); fio de brilho
no topo 1,5 px 14 %; sombra 45 %, dist 14, suav 40. Fundo que escurece e desfoca embaixo: Gaussian 28 + Exposure −1,1 com máscara de
y 1040 para baixo, feather 300, fade 4 q. Lower third Apple 16:9 (Capa): vidro + véu ~45 % + fio ~15 %, largura muda por frase
(65/65), frases 3–7 palavras, y ≈ 986 em 1080.
**No CapCut:**
- [MOTOR] página por frase (`paginar`), escala 106→100 e y +16→0 em 8 q cam65_100 na página (`legendas --anim apple`); revelação
  palavra a palavra no lugar (cada palavra aparece no seu tempo sem mexer o layout) — ver skill `capcut-igreen-legenda-apple`.
- [CAPTURAR] o blur 24→0 e o fade (animação de entrada de texto com desfoque, ~0,27 s) e a saída com desfoque (0,2 s); sombra 45 %/dist 2.
- [ASSAR] pílula de vidro como PNG por frase; luz correndo na borda como vídeo com alfa.

## 3. FÓRMULA VIRAL (base de todo Reels de pessoa falando)
Plano antes (linha × tipo: Captions · Captions+UI · Halfscreen · Full screen), mistura ~35/30/30, troca a cada ~3,5 s, nada > 7 s, A-roll
nunca "pelado". Gancho (UI que mostra a promessa) → ponte → capítulos (stepper) → fecho. A-roll: olhos a 25–30 % da altura, rosto 18–25 %
da altura, push lento +8–18 % em 2–3 s, punch seco ×1,2–1,3 na palavra-chave. Meia tela: A-roll desce ~800–840 px em 6 q cam65_100,
corte em y 960, degradê de 960 a ~1300. Tela cheia: fundo #F4F2EE + grade 120 px + sombra de janela, revelação por círculo (2–3 q) ou
retângulo (6 q), zoom-out 108→100 cam65, volta ao A-roll em corte seco. Pop: 0 → 108 % em 4 q (cam65_100) → 100 % em 5 q (cam65).
Crivo: texto = fala; nunca no rosto; grade; página = frase 3–7 sem terminar em o/de/em/a/que/pra/com e sem palavra sozinha; destaque
empilhado [antes] / DESTAQUE / [depois]; plaquinha de nome 56/34 centrada pelo rosto; objeto real na mão não é coberto.
Talking head (pipeline): 1 frase = 1 plano (0,6–1,2 s); degraus de escala 100/106/100/110/100/104/108 (dois cortes seguidos nunca na
mesma escala); gancho 167 → 100 % em 22 q cam40_100; push de tese +16 % em 14 q; deriva +4,5 % em planos ≥ 2 s; som: whoosh −17,
textura −13, riser −11, hit −12 dBFS; 22–28 sons diferentes por reel; punch seco não leva som; nicho sóbrio sem glitch/neon.
Narração: bordas na pausa real medida (RMS 5 ms; silêncio < −50 dB ≥ 50 ms; início/fim de fala a −42 dB); troca de voz casada palavra a
palavra (desvio > 0,3 s divide na pausa); animação dispara no início da palavra; brilho pulsando com a voz = envelope RMS → keys [ASSAR+MOTOR].

## 4. DINAMISMO (truques por frase forte, 3–5 por minuto, cada um diferente do anterior)
IM-43 caixa por direção: cada linha entra por um lado, mesma largura (≤ 600–740 px), 10 q cam40_100, 1º quadro invisível ·
IM-44 letra a letra subindo 107 px, 1 letra/q, assenta em 8–14 q · IM-45 bloco torto: palavras giradas +11, −10, +6, −2, +3, +8, −9°,
sobem 232 px, 12 q por palavra · IM-39 herói que troca no lugar: entra 88 px em 6 q cam40_100, sai em 6 q cam100_10 para o lado oposto,
1 herói a cada 0,7–1,4 s, nunca junto da legenda · IM-46 saída para um ponto (escala 100 → 0 até dentro da cabeça, 6–8 q cam100_10) ·
IM-41 saída sugada 7 q terminando 3 q antes do corte · IM-31 texto atrás da cabeça.
Vetados: piscar, clarão radial, Difference em fundo claro. Um efeito por tomada; corte seco é o padrão.
No CapCut: rotação/posição/escala por palavra [MOTOR] (um segmento por palavra); 1º quadro invisível depende de opacidade (a confirmar)
ou de animação [CAPTURAR]; motion blur [CAPTURAR/ASSAR].
