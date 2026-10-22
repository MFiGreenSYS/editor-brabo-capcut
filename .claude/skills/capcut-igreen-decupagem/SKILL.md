---
name: capcut-igreen-decupagem
description: Decupar e cortar fala gravada (talking head, depoimento de cliente ou licenciado iGreen, narração em takes) e montar os cortes direto no rascunho do CapCut - escolher o take bom, tirar respiros, pausas, erros, falsos inícios, voz da equipe, sem amputar palavra, com a régua medida nos cortes do Matheus. Use quando pedirem "corta os respiros", "tira os erros", "decupa", "escolhe os melhores takes", "monta os cortes no CapCut", "esse corte comeu a palavra" em projeto do MKT iGreen.
---

# Editor Brabo CapCut · Decupagem e corte de fala

Mesma régua do Editor Brabo do After (447 cortes reais do Matheus). Código copiado para cá: `Aprendizados-SYS/scripts/cortador_fala.py`
e `auditar_cortes.py` (origem: Editor Brabo do After, na máquina do Matheus; melhoria feita lá → entra aqui por commit, e vice-versa).
O "Remover pausas"/"palavras de preenchimento" automático do CapCut **não** substitui isto: ele não conhece a régua nem retake.

## Princípio
O tempo de palavra do whisper NÃO é régua de corte. A borda é decidida pela VOZ medida no áudio; o whisper serve para ler o conteúdo.

## Procedimento (pasta do projeto)
1. Áudio de cada bruto: `ffmpeg -i brutos/A01.MP4 -vn -ac 1 -ar 16000 _trabalho/audio/A01.wav` (nome do wav = nome do vídeo).
2. Transcrição por palavra: `whisper _trabalho/audio/A01.wav --model small --language pt --word_timestamps True --output_format json
   --output_dir _trabalho/whisper --fp16 False` → ler INTEIRO, como editor. (A pasta tem que ser `_trabalho/whisper/<clip>.json`:
   é onde o cortador procura a transcrição longa. Sem GPU nesta máquina: small leva ~1× a duração do áudio.)
3. Escolher takes em `_trabalho/selecao.json` = `{"ID": [["A01", t0, t1, "nota"], ...]}`: fica o **último take completo** de cada
   frase; take "aprovado" pela equipe mas que troca palavra do roteiro perde para o fiel. Frase sem take bom → avisar o Matheus.
   Fala fora do roteiro que não é retake → o Matheus decide.
4. Cortar: `python -I Aprendizados-SYS/scripts/cortador_fala.py _trabalho/audio _trabalho/selecao.json _trabalho --fps 30 --modelo medium`
   → `<ID>.edl.json` + `<ID>.cortes.md` (o que saiu e por quê).
5. Auditar: `python -I Aprendizados-SYS/scripts/auditar_cortes.py _trabalho/audio _trabalho/<ID>.edl.json --fps 30` → zero AMPUTADO
   não intencional.
6. Montar no CapCut (CapCut fechado): `python -I Aprendizados-SYS/scripts/capcut_brabo.py cortes "<projeto>" _trabalho/<ID>.edl.json --midia brutos`.
   Rodar de novo substitui só a trilha "Brabo · Cortes".
7. Conferir a montagem: transcrever ±1,5 s em volta de CADA emenda com `--model medium` (trecho curto com `ffmpeg -ss -to` do bruto
   pela EDL) e procurar palavra repetida/comida. Palavras para a legenda: a transcrição dos brutos + `paginar --edl` (já converte o
   tempo para a montagem).
8. Registrar decisões e alternativas no `EDICOES.md`.

## Números (CRT-01/02/04 do Matheus)
| Item | Regra |
|---|---|
| Pausa | ≥ 0,40 s sai; dentro do clipe fica ≤ 0,40 s; nunca > 0,50 s |
| Saída | fim da voz + 80 ms (40–130), mantém o decaimento |
| Entrada | até 1 quadro antes do início da voz, nunca depois |
| Retake | recomeço com ≥ 60 % das mesmas palavras → fica o último completo |
| Falso início | 1–3 palavras isoladas que se repetem no começo da frase seguinte → sai |
| Proibido | cortar dentro de palavra; clipe com voz < 0,30 s; voz da equipe; take que acaba com a fala andando |

## Quando o Matheus marca um corte
Ele diz o tempo na timeline do CapCut ("em 00:13:15 deveria pular para 00:15:06" — CapCut mostra mm:ss:quadros a 30 fps).
Converter para o tempo do bruto pela EDL (soma das durações anteriores), gravar a borda exata na seleção com o 5º campo
(`"!"`, `"!i"`, `"!f"`), recortar, remontar e **respeitar a marca dele**. A correção vira regra no `cortador_fala.py` + linha aqui.
