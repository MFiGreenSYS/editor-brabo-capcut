---
name: capcut-igreen-legendas
description: Legenda de marca iGreen no CapCut - página por frase (3-7 palavras) sincronizada à fala, destaque da palavra de valor em verde #18FF00, Inter, dentro da zona segura do Instagram e nunca no rosto, gerada direto no rascunho pelo motor a partir da transcrição. Use quando pedirem "legenda", "legenda dinâmica", "legenda com destaque verde", "corrige a legenda", "legenda está em cima do rosto", "palavra sozinha na legenda" em vídeos do MKT iGreen no CapCut.
---

# Editor Brabo CapCut · Legendas iGreen

Regras medidas na fórmula viral do Editor Brabo + marca iGreen. Estilo visual vem do esqueleto `legenda` capturado do MODELO iGreen
(skill `capcut-igreen-marca`); o motor só troca texto, tempo e o trecho em destaque.

## Gerar
1. Palavras com tempo: JSON do whisper (`--word_timestamps True`) dos brutos.
2. `python -I Aprendizados-SYS/scripts/capcut_brabo.py paginar <palavras.json> --edl <edl.json> --destaques "20%,economia,app" -o paginas.json`
   - página por programação dinâmica: 3–7 palavras, fecha em pontuação/pausa > 0,35 s, nunca termina em o/de/em/a/que/pra/com…
   - a página fica na tela até a próxima (sem buraco < 0,6 s).
3. **Ler o `paginas.json` como editor**: texto = fala; grafia (iGreen, produtos, nomes); no máximo 1 destaque por página e poucos
   no vídeo (destaque é número, economia, produto, CTA — "uma frase em verde por peça" é a lei da marca nos estáticos; no vídeo,
   1 palavra por página em ~1/3 das páginas). Corrigir à mão no JSON quando precisar.
4. CapCut fechado → `capcut_brabo.py legendas "<projeto>" paginas.json --esqueleto legenda` (fundo claro: `--esqueleto legenda-claro`).
   Sem MODELO capturado: `--esqueleto basico` (branco + destaque verde, fonte padrão) e avisar.
5. `capcut_brabo.py validar` → avisos de zona segura e palavra sozinha.

## Regras (nunca violar)
- Texto em y 420–1500 px, x 32,5–1047,5, fora da coluna de ícones (x > 1000 em y 1020–1500). Linha ≤ 760 px centrada.
- Nunca no rosto: plano normal (olho em y ~700–780) → legenda abaixo do queixo (centro ~1250–1350). Close em que o queixo passa
  de ~1150 → legenda sobe para acima da cabeça (y 450–600) naquele trecho; avisar no plano.
- Nunca uma palavra sozinha numa linha. Destaque no meio da frase pode empilhar: [antes] / DESTAQUE / [depois].
- Verde `#18FF00` só na palavra de destaque; fundo claro usa `#0B7A00`. Corpo `#F2FFF0`, sombra suave (não contorno grosso).
- Inter (800 corpo / 900 destaque). Nada de outra fonte.
- Legenda até o último quadro da fala; não invade a assinatura.

## Legenda automática do CapCut
Pode servir só como transcrição de conferência. A legenda final é a do motor (página certa, destaque, grafia); se o Matheus quiser a
automática, aplicar o mesmo crivo e corrigir página por página.
