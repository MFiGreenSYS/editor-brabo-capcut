---
name: capcut-igreen-reels
description: Fluxo completo do Editor Brabo CapCut para o MKT iGreen - Reels, Shorts, Stories e anúncios verticais de pessoa falando (licenciado, consultor, cliente, porta-voz, depoimento, Royal/Embaixador) montados no CapCut desktop - briefing, decupagem da fala, plano cena a cena aprovado, cortes e legendas gerados no rascunho pelo motor, marca iGreen, zoom de corte, sound design, revisão pela grade do Instagram e entrega. Use quando pedirem "edita esse reels no CapCut", "monta o vídeo do licenciado", "anúncio da iGreen", "corta e legenda", "faz no CapCut", ou ao continuar qualquer projeto em PROJETOS/.
---

# Editor Brabo CapCut · Reels iGreen (skill viva — lapidar a cada vídeo)

Padrão: o editor mais caro do mercado, com a marca iGreen. Toda correção do Matheus vira regra na seção "Crivo" desta skill
(ou na skill da área) e, se for de código, teste no `test_motor.py`. Exclusivo MKT iGreen.

Ler antes: `Aprendizados-SYS/00-CEREBRO.md`, `02-marca/MARCA-IGREEN-VIDEO.md`, `04-auditoria/CHECKLIST-ERRO-ZERO-CAPCUT.md`.
Motor: `python -I Aprendizados-SYS/scripts/capcut_brabo.py …` (abaixo só "motor").

## O processo (nesta ordem, sempre)
1. **Projeto e briefing** — `python -I PROJETOS/novo_projeto.py "Nome"`; preencher `BRIEFING.md`: público (cliente que economiza
   OU licenciado/consultor — nunca os dois), produto, CTA único, duração, formato (Reels 9:16 / Feed 4:5), quem fala, prazo.
   Faltou algo → perguntar. Brutos vão para `brutos/` (o Matheus copia; não mover arquivo dele de outro lugar sem ele pedir).
2. **Decupagem** — skill `capcut-igreen-decupagem` → `_trabalho/<ID>.edl.json` + transcrição da montagem conferida.
   Grafia de marca corrigida na transcrição (iGreen, nomes de pessoas: perguntar).
3. **PLANO (obrigatório)** — `PLANO.md`: tabela linha a linha da fala × tipo de cena × o que aparece × som.
   Tipos: **Fala** (A-roll + legenda) · **Fala+Punch** · **Fala+Elemento** (número/ícone/print sobreposto) · **Tela cheia**
   (B-roll, print do app, vídeo de produto da pasta `WORKSPACE-MF\assets\video`) · **Assinatura**.
   Gancho (0–2 s: número ou dor) → ponte → 2–4 blocos → CTA → assinatura vertical. Troca a cada ~3,5 s; nada > 7 s parado.
   Mandar ao Matheus e esperar ok (ou "pode seguir" → montar e entregar o plano junto).
4. **Rascunho no CapCut** — o Matheus cria o projeto vazio no CapCut com o nome do projeto (ou duplica o "MODELO iGreen"),
   proporção 9:16, e **fecha o CapCut**. Depois:
   - `motor cortes "<projeto>" _trabalho/<ID>.edl.json --midia brutos/`
   - `motor paginar _trabalho/<ID>.palavras.json --edl _trabalho/<ID>.edl.json --destaques "20%,economia" -o _trabalho/<ID>.paginas.json`
     → conferir as páginas (texto = fala, grafia, destaque ≤ 1 por página) → `motor legendas "<projeto>" … --esqueleto legenda`
     (sem MODELO capturado ainda: `--esqueleto basico` e avisar que o estilo final vem do MODELO).
   - `motor punch "<projeto>" --escala 1.12 --rosto-y <altura do olho>` (skill `capcut-igreen-movimento`).
   - SFX/trilha: skill `capcut-igreen-sound-design`. Assinatura/CTA: skill `capcut-igreen-marca`.
   - `motor validar "<projeto>"` = **VALIDAÇÃO OK**.
5. **Acabamento no CapCut (Matheus ou guiado)** — o que o motor ainda não escreve do zero: elementos sobrepostos, transição-assinatura,
   animações da biblioteca. Dar a lista exata (tempo, elemento, efeito, valor) em `EDICOES.md`.
6. **Revisão** — skill `capcut-igreen-revisao-entrega`. Export só se o Matheus pedir.
7. **Registrar** — `EDICOES.md` (o que foi feito, backups), `NOTAS.md` (aprendizado), `00-CEREBRO.md` / Crivo se mudou regra,
   `PROJETOS/INDICE.md` (status).

## Crivo do Matheus (regras herdadas e medidas — nunca violar)
- Texto = palavra falada. Nada no rosto. Grade do Instagram (y 420–1500, x 32,5–1047,5, fora da coluna de ícones).
- Legenda = frase de 3–7 palavras, nunca termina em o/de/em/a/que/pra/com, nunca uma palavra sozinha, linha ≤ 760 px.
- Emenda de fala é o erro nº 1 (7× no After): ouvir CADA corte antes de entregar.
- Edição manual do Matheus é sagrada: o motor só regrava trilhas "Brabo · …".
- Verde só no destaque; um CTA; logo oficial.

## Quando o projeto já foi mexido pelo Matheus no CapCut
`motor raio-x "<projeto>"` → comparar com o plano → mudar só o pedido. Se ele pôs **marcadores** na timeline com comentário,
o raio-x mostra (`MARCADORES`): tratar cada marcador como um pedido localizado (equivalente à "pinça" do After).
