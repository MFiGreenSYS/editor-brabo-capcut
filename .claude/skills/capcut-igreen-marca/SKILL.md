---
name: capcut-igreen-marca
description: Aplicar a marca iGreen em vídeos no CapCut - assinatura/vinheta oficial no fim, logo e ícone só dos arquivos oficiais, CTA único com hold, plaquinha de nome, cores (#18FF00 raro, #030603), Inter, e montar/capturar o rascunho MODELO iGreen de onde saem os moldes de estilo (legenda, título, nome, CTA, curva). Use quando pedirem "coloca a assinatura", "põe o logo", "CTA no final", "lower third/plaquinha com o nome", "deixa com a cara da iGreen", "monta o modelo iGreen no CapCut" ou "captura o estilo".
---

# Editor Brabo CapCut · Marca iGreen

Tudo de marca: `Aprendizados-SYS/02-marca/MARCA-IGREEN-VIDEO.md` (fonte única: `Desktop\MKT.SYS\iGreen-Studio\brand\brand.json`).
Regra 4 do iGreen.SYS: ícone e logo SEMPRE de `marca/Aplicações logo iGreen/` (cópia exata de `iGreen.SYS\07_Marca-Assets\Aplicações logo iGreen\`).

## Peças padrão
| Peça | Como | Regra |
|---|---|---|
| Assinatura (fecho) | `Cópia de Assinatura vertical .mp4` (4,9 s, 1080×1920, com som) no fim da trilha principal | depois do CTA; a fala termina antes; trilha some com fade sob ela |
| Logo em cena | `iGreen - Verde.png` (fundo escuro) / `iGreen - Preto.png` (claro); `SEM ENERGY …` quando a peça é Grupo iGreen | sem distorcer, sem sombra colorida, nunca recortado nem digitado |
| Ícone | `G - Verde.png` / `Símbolo branco .png` | idem |
| CTA | "Quero economizar →" (cliente) ou "Seja um licenciado →"/"Quero ser consultor →" (negócio) — UM | botão pílula `#18FF00` com texto `#02220a`, hold ≥ 3 s |
| Plaquinha de nome | nome Inter 800 + função Inter 500 (`#B9C9B6`), proporção 56/34 | centralizada pelo rosto, nunca no canto nem no rosto; 2–3 s na 1ª fala |
| Número de prova | Inter 900 grande, número em `#18FF00` | é a manchete do trecho |
| Fundo de tela cheia | `#030603` + brilho radial verde 5–25 % ou os fundos 9:16 oficiais | nada de verde chapado |
Sub-marca (Telecom, Mobile, Club, Livre…): PNG de `marca/MARCAS IGREEN/`.

## O MODELO iGreen (fazer uma vez, com o Matheus)
Os estilos não são escritos "no braço": o Matheus monta no CapCut um projeto **"MODELO iGreen"** (9:16, 30 fps) com um exemplo de
cada molde, com o TEXTO exatamente assim:
- `LEGENDA destaque` — legenda de marca; selecionar só "destaque" e pintar de `#18FF00` (vira o 2º estilo = destaque); animação de entrada escolhida.
- `LEGENDA CLARO destaque` — versão para fundo claro (`#121317` + destaque `#0B7A00`).
- `TITULO` — número/manchete. `NOME` — plaquinha (nome; a função vai num 2º texto `FUNCAO`). `CTA` — texto do botão.
- Um clipe qualquer com 2 keyframes de escala usando a **curva personalizada 65/65** (a curva aprovada no After).
Fechar o CapCut e capturar:
```
python -I Aprendizados-SYS/scripts/capcut_brabo.py capturar "MODELO iGreen" --texto "LEGENDA destaque" --como legenda
python -I Aprendizados-SYS/scripts/capcut_brabo.py capturar "MODELO iGreen" --texto "LEGENDA CLARO destaque" --como legenda-claro
python -I Aprendizados-SYS/scripts/capcut_brabo.py capturar "MODELO iGreen" --texto "TITULO" --como titulo
python -I Aprendizados-SYS/scripts/capcut_brabo.py capturar "MODELO iGreen" --texto "NOME" --como nome
python -I Aprendizados-SYS/scripts/capcut_brabo.py capturar "MODELO iGreen" --segmento <id do clipe com key> --como curva --curva
```
Conferir com `raio-x` que o esqueleto tem 2 estilos (o motor avisa). Moldes mudaram → capturar de novo (versiona por data no nome
se o Matheus quiser manter o antigo). Registrar em `00-CEREBRO.md` §2 os valores finais (tamanho, posição, animação) e promover a
"Proposta" a regra.
