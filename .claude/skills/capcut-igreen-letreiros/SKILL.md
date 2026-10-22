---
name: capcut-igreen-letreiros
description: Letreiros animados (lettering) no estilo Editor Brabo para vídeos do MKT iGreen no CapCut - bloco de texto com tipografia mista (linha pequena branca + palavra de valor grande em verde #18FF00), fonte Inter da marca, entrada pop/sobe/zoom com as curvas do After amostradas em keyframe, lados alternados, som no pico, gerados direto no rascunho pelo motor. Use quando pedirem "letreiro", "lettering", "texto grande na tela", "palavra-chave animada", "texto dinâmico", "edição dinâmica", "tipografia animada" em vídeo do MKT iGreen.
---

# Editor Brabo CapCut · Letreiros animados

Comando: `python -I Aprendizados-SYS/scripts/capcut_brabo.py letreiros "<projeto>" letreiros.json` (CapCut fechado).
Rodar de novo SUBSTITUI as trilhas "Brabo · Letreiros…" (o JSON é a lista completa). Itens sobrepostos vão sozinhos para outra trilha.

## Item do JSON
```json
{"t0": 56.95, "t1": 60.2, "x": -0.60, "y": 0.28, "alinhar": "esquerda", "anim": "zoom", "saida": true,
 "partes": [{"texto": "COMISSÕES\n", "tamanho": 10, "cor": "branco", "peso": "titulo"},
            {"texto": "EM DÓLAR",    "tamanho": 20, "cor": "verde",  "peso": "impacto"}]}
```
- `partes` viram UM texto com vários estilos (linha nova = `\n` no fim da parte). Cores: `branco` #F2FFF0, `verde` #18FF00,
  `verde_fundo_claro` #0B7A00, `tinta`, `cinza`, ou `[r,g,b]`. Pesos (Inter da marca, lida direto de
  `Aprendizados-SYS/fontes/Inter-limpa/`, sem instalar; ver "Fonte: Inter LIMPA"): `medio` SemiBold, `bold`, `titulo` ExtraBold, `impacto` Black.
- `x`/`y` = centro do bloco em meia tela (0 = centro, ±1 = borda; y + = para cima).
- `anim`: `pop` (0 → 108 % em 8 q cam65_100 → 100 % em 6 q: o pop de 3 keys do After) · `sobe` (sobe 0,06 + 0,94 → 1 em 10 q) ·
  `zoom` (1,6 → 1 em 12 q cam40_100). Saída: some em 7 q no fim (`saida: false` no último letreiro do vídeo).

## Efeito de texto nativo (preferido desde 22/10/2026)
Item com `"efeito": {"entrada": "desfoque", "saida": "desfoque", "dur_entrada": 0.45, "dur_saida": 0.35}` usa a animação da biblioteca
do CapCut no lugar das keys (o CapCut não aceita opacidade por keyframe em texto; a animação nativa faz fade + blur de verdade).
Entradas: `desfoque` (sai do blur — o "Apple"), `ampliar` (cresce aparecendo), `surgir` (fade), `pular`, `brilho`, `varredura`.
Saídas: `desfoque`, `sumir`, `encolher`, `brilho`. Vistos na tela: desfoque e ampliar. Uma família por vídeo (padrão: desfoque).

## Fonte: Inter LIMPA (22/10/2026)
O motor usa `Aprendizados-SYS/fontes/Inter-limpa/` (a Inter da marca com os contornos unidos por `fonte_limpa.py`). A estática original
tem contornos sobrepostos e o CapCut desenhava emendas ("linhas nos A", D com risco). Continua texto editável no CapCut. Fonte nova
da marca → rodar `fonte_limpa.py` nela antes de usar.

## Regras (Editor Brabo + marca)
- **Texto = palavra falada** (grafia conferida: iGreen com i minúsculo, nunca "IGREEN"). Tempo `t0` = início da palavra − 0,05…0,1 s
  (procurar na transcrição da MONTAGEM).
- Tipografia mista: linha de apoio pequena branca (8–10) + **palavra de valor** grande em verde (16–22). Proporção ~1 : 2.
  Um verde por letreiro.
- **Lados alternados** (direções opostas): esquerda `x −0,60` alinhado à esquerda, direita `x +0,60` alinhado à direita, `y +0,28`,
  longe do rosto e da legenda (a legenda fica em y −0,62).
- Ritmo: um letreiro a cada ~10–15 s em aula; em Reels a cada 3,5 s. Duração 2,5–3,5 s. Nada parado > 7 s sem troca.
- Som no pico: `whoosh` (sobe/zoom, 0,12 s antes) ou `pop` (pop, +0,2 s), volume 0,45–0,5 (skill `capcut-igreen-sound-design`).
- Destaque forte (número, dinheiro, garantia, atenção) = letreiro `zoom` + **zoom de impacto** no vídeo (skill `capcut-igreen-movimento`).

## Verificado no CapCut 9.5 (1020, 20/10/2026)
Fonte Inter por caminho de arquivo funciona; vários estilos num texto funcionam; o pop por keyframe de escala (`KFTypeScaleX`)
aparece certo (pequeno → passa de 100 % → assenta). A conferir: `KFTypeAlpha` (fade) e `KFTypePositionY` (sobe) em texto.

## Próximos passos de estilo (pedidos que vão chegar)
- Texto ATRÁS da pessoa (máscara/recorte): no CapCut = duplicar o clipe por cima com "Remover plano de fundo" e o letreiro entre os
  dois. O motor ainda não escreve o recorte (capturar de um clipe feito no CapCut → esqueleto).
- Legenda estilo Apple (palavra saindo do blur): animação de entrada da biblioteca do CapCut → capturar do MODELO.
