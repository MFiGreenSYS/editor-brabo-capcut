---
name: capcut-igreen-revisao-entrega
description: Revisar e entregar vídeo do MKT iGreen editado no CapCut - checklist erro zero (marca, fala, grade do Instagram, movimento, projeto), validação do rascunho, export com as configurações certas quando o Matheus pedir, revisão automática do MP4 (quadros com a zona segura, loudness, tela preta/congelada), nome e pasta do arquivo, e registro. Use antes de dizer que um vídeo está pronto, quando pedirem "revisa", "confere", "exporta", "manda o vídeo", "está pronto?".
---

# Editor Brabo CapCut · Revisão e entrega

Checklist: `Aprendizados-SYS/04-auditoria/CHECKLIST-ERRO-ZERO-CAPCUT.md` (5 portões). Nada é "pronto" sem os 5.

## Antes de mostrar (sem export)
1. `python -I Aprendizados-SYS/scripts/capcut_brabo.py validar "<projeto>"` = **VALIDAÇÃO OK** (avisos de zona segura e palavra
   sozinha resolvidos ou justificados).
2. `raio-x` conferido contra o `PLANO.md`: cada cena no tempo, legenda = fala, destaque certo, assinatura no fim.
3. Portões 1–4 do checklist marcados um por um. Emendas ouvidas.
4. Dizer ao Matheus o que conferir no CapCut (lista curta com tempos) e o que ficou pendente.

## Export (só quando o Matheus pedir)
CapCut > Exportar: resolução **1080p** (Reels 1080×1920), **30 fps**, codec **H.264**, formato **MP4**, taxa de bits "Recomendada"
ou maior; áudio AAC. Nome `DD-MM-AAAA_Projeto_vN.mp4`, salvar em `PROJETOS/<projeto>/export/`. Feed 4:5 → projeto separado 1080×1350.
Depois:
```
python -I Aprendizados-SYS/scripts/revisar_export.py "PROJETOS/<projeto>/export/<arquivo>.mp4" --cada 1.5
```
→ `revisao.md` (formato, fps, loudness, pico, preto/congelado) + `zona.jpg` (quadros com a grade em vermelho). **Olhar a zona.jpg**:
texto ou rosto no vermelho = reprovado. Quadros de momentos específicos: `--tempos 0.5,3.2,7.9`.

## Registrar
- `PROJETOS/<projeto>/EDICOES.md`: versão, o que mudou, backups do motor usados.
- `PROJETOS/INDICE.md`: status (em edição → revisão → aprovado → publicado).
- Erro que o Matheus pegou → linha em "Erros já cometidos" do checklist + regra na skill da área.
- Aprendizado de ritmo/estilo → `00-CEREBRO.md`.
