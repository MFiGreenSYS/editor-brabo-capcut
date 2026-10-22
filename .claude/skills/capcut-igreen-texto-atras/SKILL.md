---
name: capcut-igreen-texto-atras
description: Texto ATRÁS da pessoa no CapCut para vídeos do MKT iGreen - palavra de valor gigante entre o cenário e a pessoa recortada (a cabeça cobre só o pé das letras), com recorte MODNet em vídeo com alfa ou "Remover plano de fundo" nativo, mesmo zoom do corte nas camadas, som de impacto, nas medidas do Editor Brabo do After. Use quando pedirem "texto atrás da pessoa", "letra por trás", "mask das letras por trás", "palavra atrás da cabeça", "dá profundidade", "ela aparece por trás", "manchete atrás".
---

# Editor Brabo CapCut · Texto atrás da pessoa

Receita medida (camadas, posição, tipografia, tempos): `Aprendizados-SYS/05-herdado-do-after/TEXTO-ATRAS-E-LEGENDA-APPLE.md` §1.

## Como o motor monta (CapCut fechado)
```
python -I Aprendizados-SYS/scripts/capcut_brabo.py atras "<projeto>" atras.json --midia <pasta_dos_brutos>
```
Para cada item: letreiro na trilha «Brabo · Atrás texto» + **pessoa recortada** (MODNet → ProRes 4444 com alfa,
`recorte_pessoa.py`, cache em `<pasta do json>/recortes/`) na trilha «Brabo · Atrás pessoa», no mesmo tempo, com a escala, posição e
keyframes do corte de baixo (o zoom de impacto move a pessoa e o fundo juntos; o texto fica parado = profundidade) e **volume 0**.
Camadas: vídeo → texto atrás → pessoa → flash → legenda e letreiros (estes continuam na frente). Rodar de novo recria as duas trilhas.
O item usa o formato dos letreiros (`partes`, `x`, `y`, `alinhar`, `anim`, `largura`).

## Recorte colado no vídeo (22/10/2026, "a máscara mexe")
O recorte só casa se as DUAS camadas tiverem a mesma escala no mesmo quadro: início no quadro da timeline, recorte saindo do mesmo instante
do bruto, keys copiadas do corte de baixo — e keys de vídeo gravadas no tempo do arquivo (o motor faz). Conferir com braço/notebook:
contorno duplicado = camadas desencontradas.

## Efeito de texto nativo (22/10/2026)
Item do `atras.json` com `"efeito": {"entrada": "ampliar", "saida": "desfoque", "dur_entrada": 0.5, "dur_saida": 0.35}`: a palavra
cresce aparecendo atrás da cabeça (animação da biblioteca do CapCut, vista na tela no CARTEIRA ATIVA do 1020) e sai no blur.
Nomes iguais aos dos letreiros (skill `capcut-igreen-letreiros`).

## Regras (do After, valem aqui)
- É MOMENTO forte (3–5 por minuto no máximo), não a base do vídeo. Só com a pessoa em quadro. Um por virada de ideia.
- Atrás da **cabeça**, nunca do tronco: a cabeça cobre só o pé das letras (base da palavra ≈ topo da cabeça + 30–75 px), cobertura ≤ 30 %.
  Se a cabeça esconde uma letra inteira, subir. Sem espaço acima (16:9, cabeça perto do topo): a palavra atravessa o terço de cima e a cabeça
  esconde ~15 % do meio — ou abrir o bloco dos dois lados da cabeça.
- Palavra = palavra falada (o herói), Inter 900 caixa alta, branco #F2FFF0 (verde #18FF00 só se o fundo não for verde — no cenário
  neon verde da iGreen o branco lê melhor). Apoio pequeno Inter 800 acima. Largura × zoom de pico ≤ ~0,9 da tela.
- Entrada: `zoom` (1,6 → 1 em 12 q, "aparece por trás dando profundidade") ou `pop`; som: riser/impacto na entrada.
- Recorte apertado, sem aura: o `recorte_pessoa.py` já fecha 1 px e suaviza 2 px; fundo claro atrás da cabeça falha (o matte come a borda).
- Nunca placa ou sombra preta atrás do texto. Véu de leitura, se precisar, é escurecer o cenário inteiro 20–25 %.
- Conferir no CapCut esperando renderizar (2–4 s) e olhar a borda do cabelo em 1:1.

## Conferido no CapCut 9.5 (1020, 20/10/2026)
O vídeo com alfa entra como camada e a pessoa fica na frente do texto; com o zoom de impacto o corpo cresce e cobre parte da palavra
(profundidade real). Em 16:9 com a cabeça no topo, o bloco aberto dos dois lados (vão de 300 px atrás da cabeça) foi o que funcionou:
CARTEIRA ‹cabeça› ATIVA, EM ‹cabeça› DÓLAR, 100% ‹cabeça› DIGITAL, SEM ‹cabeça› FRONTEIRAS. Tamanho calculado com 9,07 px/unidade.
O texto atrás dura só até o fim do corte de baixo: escolher o momento num corte com ≥ 1,5 s depois da palavra.

## Medir a cabeça antes
Rosto por Haar/YuNet em quadros do bruto (ver `capcut-igreen-movimento`): olho em y de meia tela; topo da cabeça ≈ olho + 0,8 × altura
do rosto. Aula ACADEMY M1 (16:9): olho y +0,59, cabeça de y_px ~110 a ~330 → herói com centro em y ≈ +0,62…+0,70.

## Alternativa nativa (melhor borda, editável no CapCut)
Duplicar o clipe na trilha de cima + "Remover plano de fundo" (bloco `matting` do material). Falta CAPTURAR uma vez: aplicar na interface
num clipe do MODELO e `capturar --segmento <id> --como recorte` para o motor clonar o `matting`. Até lá, o MODNet.
