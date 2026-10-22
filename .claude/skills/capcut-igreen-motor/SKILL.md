---
name: capcut-igreen-motor
description: Ler e escrever rascunhos do CapCut desktop pelo motor capcut_brabo.py (MKT iGreen) - listar projetos, raio-x da timeline (trilhas, cortes, textos, keyframes, marcadores), capturar moldes de estilo de um rascunho real, inserir cortes/legendas/sons/zoom, validar, voltar backup, e evoluir o motor com teste. Use quando pedirem "olha o que eu fiz no CapCut", "lê o projeto", "o que tem na timeline", "edita o trecho que marquei", "volta a versão anterior", ou quando for mexer no código do motor ou o CapCut mudar de versão.
---

# Editor Brabo CapCut · Motor do rascunho

Formato: `Aprendizados-SYS/03-capcut/FORMATO-DRAFT.md`. Código: `Aprendizados-SYS/scripts/capcut_brabo.py` (ajuda: rodar sem argumentos).

## Comandos
| Comando | Faz |
|---|---|
| `listar` | projetos da tela inicial (nome, duração, data) e se o CapCut está aberto |
| `raio-x <proj> [--json f]` | trilhas e segmentos com tempo, texto, mídia, escala/posição, velocidade, volume, keyframes, animações, marcadores |
| `capturar <proj> --texto "X" \| --segmento ID --como nome [--curva]` | salva molde em `esqueletos/` |
| `cortes <proj> edl.json --midia pasta` | trilha principal "Brabo · Cortes" a partir da EDL do cortador |
| `paginar palavras.json [--edl] [--destaques] -o paginas.json` | páginas de legenda por frase |
| `legendas <proj> paginas.json --esqueleto legenda\|basico` | trilha "Brabo · Legenda" |
| `audio <proj> arquivo --em s --volume v` | SFX/trilha em "Brabo · SFX" |
| `punch <proj> [--escala] [--a-cada] [--rosto-y]` | zoom de corte alternado |
| `zoom <proj> --em s --dur s --de --para` | keyframe de escala com a curva capturada |
| `validar <proj>` | referências, sobreposição, mídia offline, zona segura, palavra sozinha → VALIDAÇÃO OK |

## Regras de segurança
- **CapCut fechado** para escrever (o motor checa `CapCut.exe` e recusa). Ler (`listar`, `raio-x`, `validar`) pode com ele aberto,
  mas o arquivo só reflete o que o CapCut já salvou.
- Toda escrita faz backup em `_backups/<proj>/<data>_<comando>/` (arquivos `draft_content.json`, `Timelines__<id>__draft_content.json`,
  `draft_meta_info.json`). **Voltar versão**: CapCut fechado, copiar de volta para os mesmos lugares (raiz e `Timelines\<id>\`),
  incluindo os `.bak`. Conferir com `raio-x`.
- O motor só substitui trilhas com nome `Brabo · …`. Trilha do Matheus nunca. Antes de editar algo que ele fez: `raio-x`, mostrar o
  que entendeu, editar o mínimo.
- Mídia da biblioteca do CapCut (efeito, SFX, transição, animação) → só por esqueleto capturado, nunca JSON inventado.

## Ver no CapCut (o Matheus quer ver sempre o resultado no CapCut, 20/10/2026)
O Claude opera e enxerga o CapCut sozinho (acesso livre dado pelo Matheus):
- `tela.ps1 -Janela CapCut -Saida x.png` → captura a janela (coordenadas da imagem + `tela x/y` = ponto na tela).
- `clique.ps1 -X … -Y … [-Duplo]` → clique (os dois scripts usam DPI por monitor: o monitor de cima está a 125 %).
- Abrir o CapCut: `Start-Process "$env:LOCALAPPDATA\CapCut\Apps\CapCut.exe"`; fechar: `CloseMainWindow()` duas vezes
  (1ª volta à tela inicial, 2ª sai). Confirmar com `listar` ("CapCut aberto agora: não").
Ciclo: fechar CapCut → motor grava (com `vigiar_rascunhos.py` ligado) → abrir CapCut → duplo clique no card →
`clique.ps1 -SemClique -Maximizar` → `ver_quadros.ps1 -Quadros "…"` (só teclado: HOME, Shift+→ = 10 q, → = 1 q) → folha de contato →
`validar` no fim. **Nunca clicar na timeline** (20/10: o 1º corte encurtou 4,7 s com o CapCut aberto). Detalhes e armadilhas
(pop-up como janela principal, minimizado, tela cheia, Claude vindo para a frente): `03-capcut/FORMATO-DRAFT.md`.
Nunca clicar em Excluir, Exportar, comprar/assinar, nem em janelas que não sejam do CapCut.

## Edição guiada (equivalente à seleção/pinça do After)
O Matheus marca no CapCut (marcador na timeline com comentário, ou diz o tempo mm:ss:qq) → `raio-x` mostra `MARCADORES` e os
segmentos naquele tempo (pelo `#id`) → editar só aqueles → `validar` → registrar no `EDICOES.md` (pedido, segmentos, backup).

## Evoluir o motor
1. Mudou o código → `python -I Aprendizados-SYS/scripts/test_motor.py` = **MOTOR OK** (testa num rascunho temporário).
2. Bug novo corrigido → teste novo no `test_motor.py`.
3. CapCut atualizou de versão → `raio-x` num projeto real, `validar`, recapturar os esqueletos `video`/`audio` de um projeto novo
   (`capturar <proj> --segmento <id> --como video`) e anotar a versão em `FORMATO-DRAFT.md`.
4. Item novo confirmado abrindo no CapCut → marcar em "Pendências de verificação" do `FORMATO-DRAFT.md`.
