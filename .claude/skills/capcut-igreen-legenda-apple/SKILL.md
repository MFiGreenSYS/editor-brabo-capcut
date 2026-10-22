---
name: capcut-igreen-legenda-apple
description: Legenda dinâmica do Editor Brabo no CapCut para o MKT iGreen, MEDIDA nos renders aprovados do After - a página nasce diagramada inteira e cada PALAVRA acende no lugar no quadro em que é falada (16:9 Capa iGreen: Inter Medium 32 px, y 918, entrada de 6 q opacidade/subida 7 px/blur 9; 9:16 fórmula: 52 px, 8 q cam65_100 +16 px 106→100 % blur 24, destaque letra a letra), saída da página em 6 q com blur, pílula de vidro no 16:9. Use quando pedirem "legenda dinâmica", "legenda estilo Apple", "palavra por palavra", "legenda igual a do After", "texto Apple".
---

# Editor Brabo CapCut · Legenda dinâmica (o jeito do After)

Spec medida (render + código): `Aprendizados-SYS/06-referencias/LEGENDA-APPLE-DO-AFTER.md` — Capa iGreen 16:9
(`AFTER-EDITORBRABO/PROJETOS/002-GreenOS-Capa/scripts/edicoes/2026-09-25_legenda_sol.jsx`, render q3655–3733) e fórmula 9:16
(`formula_reels.jsx` FR.legenda, ARANTES q195–235). **A animação é POR PALAVRA** — a página não tem entrada (erro de 20/10).

## Gerar (CapCut fechado)
1. `paginar` (página = frase de 3–8 palavras, com `palavras` e tempos da MONTAGEM; nunca termina em o/de/em/a; nada sozinho).
2. `python -I Aprendizados-SYS/scripts/capcut_brabo.py legenda-palavras "<projeto>" paginas.json [--px 32] [--sem-pilula]`
   - mede cada palavra com a Inter Medium (PIL) e diagrama a página inteira centrada (2 linhas equilibradas se passar de 1200 px no
     16:9 / 760 px no 9:16); **um segmento de texto por palavra** no x/y final, começando no quadro em que ela é falada;
   - 16:9: 32 px (tamanho CapCut 3,53), branco, centro do bloco em y 918; entrada 6 q (opacidade 0/42/70/88/96/100 % + sobe 7 px);
   - 9:16: 52 px #F3F3F3, bloco termina em y 1400; entrada 8 q cam65_100 (+16 px, 106→100 %);
   - saída: a página inteira nos 6 q antes da próxima;
   - destaque da página em #18FF00;
   - 16:9: **pílula de vidro** da Capa atrás (PNG por largura: véu #050F0A 46 %, raio = altura/2, fio branco 1 px 16 %, largura = frase +
     2×34 px), entra 4 q antes da 1ª palavra (opacidade 8 q, escala 0,94→1 em 10 q cam65), escala = largura do PNG ÷ largura da tela.
   Trilhas «Brabo · Pílula» e «Brabo · Legenda 1…N» (uma por posição de palavra). Recria tudo.

## O que o CapCut não deixa o motor fazer (capturar no MODELO iGreen)
- **Opacidade por keyframe em TEXTO não funciona** (medido 20/10): a palavra aparece cheia no seu quadro + sobe 7 px. O fade e o
  **blur 9→0 (16:9) / 24→0 (9:16)** da palavra e a saída da página com blur (8 / 18) vêm da animação nativa de texto com desfoque:
  aplicar 1× num texto do MODELO (entrada ~6–8 q, saída 6 q) e capturar → o motor clona em cada palavra.
- Sombra 45 %/dist 2/suav 14 (9:16) e brilho do destaque: capturar a sombra do texto.
- Destaque 9:16 letra a letra (86–108 px, blur 26): animação por caractere nativa — capturar.

## Regras (crivo)
Texto = fala; grafia; página = frase; nunca no rosto; grade do Instagram no 9:16 (y 420–1500, linha ≤ 760); 9:16 sem pílula e sem véu
preto; 16:9 com pílula. Texto que termina junto com o corte sai seco. A antiga `legenda-apple` (página com palavras reveladas e
entrada da página) está superada.
