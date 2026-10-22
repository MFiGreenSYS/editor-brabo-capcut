# Ficha · Legenda dinâmica "Apple" do Editor Brabo do After (16:9 e 9:16)

Estudo de 20/10/2026 nos renders e no código reais (`Desktop\Pessoal.SYS\AFTER-EDITORBRABO`). Tempos em quadros (q).
Evidência: E1 medido no render · E2 visto no quadro · E3 lido no código (não medido) · E4 desconhecido.
Quadros-prova e scripts de medição: scratchpad da sessão 58ed7cbb (`estudo_legenda\capa\`, `\arantes\`, `\scripts\`).

## Fontes
- 16:9 iGreen: `PROJETOS\002-GreenOS-Capa\render\▶ iGreen OS — Capa.mp4` (1920×1080, 30 fps, 146,17 s), legenda da Sol em
  q3648–4330. Código: `PROJETOS\002-GreenOS-Capa\scripts\edicoes\2026-09-25_legenda_sol.jsx` (v2 depois do "suba mais um pouco").
  Status no INDICE: "em edição desde 30/09 (confirmar se aprovado)".
- 9:16 fórmula: `PROJETOS\004-DIGITAL-PRO-CLUB\ARANTES\render\▶ Story 2-7 · O poder mudou de mão.mp4` (1080×1920, **23,976 fps**),
  página "eu tenho UM MILHÃO para comprar." q195–235. Código: `Aprendizados-SYS\scripts\formula_reels.jsx` `FR.legenda` (l. 223–330),
  overrides em `ARANTES\scripts\04_build.jsx` l. 39–43 e `PACHECO\ANTARES\scripts\08_build.jsx` l. 41–42.

## Lógica
- Página = frase/oração falada (whisper por palavra). A página inteira é **diagramada no layout final** e cada palavra **aparece no
  lugar dela, no quadro em que é falada** (±1 q, E1). A linha nunca se recentraliza enquanto as palavras chegam (E1/E2).
- Quem anima é a PALAVRA (entrada própria). A página não tem entrada de bloco; só tem saída de bloco.
- Quando NÃO usar: manchete grande atrás da cabeça, letreiro de dado (outra técnica); b-roll sem a pessoa leva só legenda pequena
  (diretiva 18/10). Nunca véu/placa preta atrás (12/10, 17/10).

## Receita 16:9 (Capa, legenda da Sol)
| Item | Valor | Prova |
|---|---|---|
| Fonte | Inter Medium, 32 px, tracking −8, branco #FFFFFF, centralizada | E3 l. 24/30; E1 altura do "O" 24 px (y 904–927) |
| Posição | centro x 960, centro y 918 | E3 l. 24/32; E1 linha y 902–933, cx 959,5 (q3712) |
| Largura | só a frase (pág. 1 = 496 px, x 712–1207) | E1 q3712 |
| Palavras/página | 3–8 (frase) | E3 l. 13–23; E1 pág. 1 = 7, pág. 2 = 8 |
| Entrada por palavra | 6 q, cubicOut p=1−(1−u)³ em tudo: opacidade 0→100, blur 9→0, y +7→0, sem escala | E3 l. 40/49; E1 tinta 35/61/84/89/94 % em q3655–3659 |
| Tempo | quadro da fala (whisper) | E1: iGreen q3655 vs fala q3656; "que" q3727 = q3727 |
| Saída da página | junto, 6 q depois do fim: opacidade 100→0 e blur 0→8, lineares, sem movimento | E3 l. 50–51; E1 q3727–3733 |
| Sobreposição | a página nova nasce no 1º q da saída da anterior (6 q de mistura no mesmo lugar) | E1/E2 q3728–3731 ("quO") |
| Pílula | vidro: blur do fundo 26 na máscara, véu #050F0A 46 %, fio branco 1 px 16 %, H 62, raio 31, padding 34/lado, sombra 35 % dist 6 suave 24 | E3 l. 54–78 |
| Pílula anima | nasce a0−4 q (larg. 80 %→100 % até a0+6 q, escala 94→100 até a0+10 q, opac. 0→100 em 8 q); muda de largura por frase de a0−3 q a a0+7 q (65/65); some 10 q no fim | E3 l. 58–80 |
| Borda de luz | `B.chaseBorder`: #7CF5AE em Add, traço 1,4 px + halo 7 px 55 % blur 10 + 2º cometa 35 %, trecho 24 %, 1 volta/3 s | E3 l. 84; E2 traço verde y 947–950 |
| Leitura da pílula | no fundo verde-escuro o véu quase não aparece: dentro × fora ≈ −8 % de luminância | E1 q3715 (55 vs 60) |
| Destaque | nenhum (tudo branco) | E1/E2 |
| Sombra no texto | nenhuma | E3 |

## Receita 9:16 (FR.legenda)
| Item | Valor | Prova |
|---|---|---|
| Fonte | sans Medium (Manrope; Urbane na Arantes; Poppins na Antares), 52 px, #F3F3F3, passo de linha 66 | E3 Arantes l. 43; E1 branco 243,243,243 |
| Destaque | 1 palavra/expressão por página, fonte pesada (Georgia BoldItalic 108 Pedro · Manrope XB 86 Arantes · Poppins SemiBold 100 Antares), cor da marca, passo 96–112 | E3 formula l. 15, Arantes l. 40–43 |
| Destaque anima | letra a letra (seletor Ramp Up): opacidade 0, y +22, blur 26 → 0; dur = mín(1,2 s, máx(8 q, nº letras × 1,4 q)) | E3 l. 306–309; E1 "um milhão" q204–212 |
| Brilho do destaque | 2 sombras da cor da marca, distância 0 (op 56 %/suave 13 e op 36 %/suave 36) + sombra preta 45 % dist 2 suave 16 | E3 l. 103–106, 312 |
| Largura | máx. 760 px centrada em 540 (era 880) | E3; E1 "um milhão" 430 px, linha 700 px |
| Quebra | 1 linha se couber; senão 2 linhas equilibradas, penalidades: palavra sozinha embaixo +900, em cima +600, linha terminando em o/de/em/a… +700, pontuação −120; com destaque: empilhada antes / DESTAQUE / depois | E3 l. 235–270; E2 |
| Posição | bloco termina em y 1400 (stories) · 1110 acima da pílula de UI · 1470 "base" · topo 470; baseline = topo da linha + 0,8 × passo | E3 l. 274–281; E1 bases 1224/1315/1387 |
| Entrada por palavra (sans) | 8 q cam65_100: y +16→0, escala 106→100 (âncora no centro da palavra), blur 24→0 (cam65_100); opacidade linear 0→100 em 5 q | E3 l. 319–322; E1 "eu" y +12,5/+9,3/+2,6/+1,1/+0,3 em q197–201 |
| Sombra (sans) | preta 45 %, 180°, dist 2, suave 14 | E3 l. 323 |
| Saída | página inteira, nos 6 q ANTES do fim: opacidade 100→0 e blur 0→18 lineares, sem movimento | E3 l. 326–327; E1 q229–235 |
| Pílula atrás da legenda | não existe | E3/E2 |

Os "q" do `FR.legenda` são quadros da comp: na Arantes (23,976 fps) 8 q = 0,334 s = 10 q a 30 fps. Em comp de 30 fps (Pedro) = 8 q.

## Etiqueta CapCut
- Palavra = segmento de texto próprio no x final da página [MOTOR] (ou um texto com estilo por trecho e alfa 0, já testado, mas
  sem movimento por palavra).
- Posição, escala, opacidade por palavra em keyframes [MOTOR] (`KFTypeAlpha` em texto ainda não conferido).
- Blur da palavra: [CAPTURAR: animação de entrada "desfoque" do texto] — ajustar a duração para 6 q (16:9) / 8 q (9:16); valor de
  blur do CapCut ↔ px do After = E4.
- Letra a letra do destaque: [CAPTURAR: animação de texto por caractere com desfoque].
- Pílula de vidro com blur do fundo: [ASSAR] PNG/MOV com alfa por largura de frase, ou [SEM EQ.] para o blur real do fundo.
- Borda de luz correndo: [ASSAR] MOV com alfa em Add (ou dispensar).
- Saída de página: opacidade [MOTOR] + blur [CAPTURAR: animação de saída "desfoque"].

## Gatilhos
"legenda dinâmica", "legenda estilo Apple", "aquelas legendas", "palavra saindo do blur", "lower third moderno", "legende a fala".

## Ouro × clichê
Ouro: palavra no quadro da fala, no lugar final (zero dança de layout); saída curta só com blur; destaque único por página.
Não copiar: a mistura de 6 q de duas páginas no mesmo lugar (Capa q3728–3731); o degradê preto 62 % da Arantes (`04_build.jsx`
l. 131–134), contrário à diretiva de 12/10 e 17/10.
