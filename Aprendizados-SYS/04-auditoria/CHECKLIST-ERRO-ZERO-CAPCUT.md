# Checklist erro zero · CapCut MKT iGreen (reler antes de toda entrega)

Herdado dos erros que o Matheus já pegou no Editor Brabo (`AUDITORIA-PROJETOS.md` de lá: margem 5×, emenda de fala 7×, grafia,
texto inventado) + regras de marca. Cada erro novo pego pelo Matheus vira linha aqui com data e o portão certo.

## Portão 1 — Conteúdo e marca
- [ ] Toda palavra na tela foi falada ou é copy aprovada. Nada inventado; dado que falta = perguntar.
- [ ] Grafia: **iGreen** (e produtos) conferida em TODA legenda (o whisper erra). Vocabulário: conexões, graduação, recorrência.
- [ ] Logo/ícone dos arquivos oficiais, sem distorcer, sem recorte. Nome digitado no lugar do logo = reprovado.
- [ ] Uma peça, um público, um CTA. CTA com hold ≥ 3 s.
- [ ] Verde `#18FF00` só no destaque (fundo claro: `#0B7A00`). Nada de verde chapado, céu azul, luz branca de estúdio.

## Portão 2 — Fala e som
- [ ] Forma de onda aparece embaixo dos cortes do vídeo principal (sem ela, o CapCut acha que o vídeo não tem som).
- [ ] **A voz do apresentador está tocando** (dar play com som em 3 pontos; `validar` reprova vídeo principal mudo). Nunca tirar a voz.
- [ ] Emendas: nenhuma palavra comida/repetida (ouvir cada corte; transcrição da montagem conferida).
- [ ] Nenhuma pausa > 0,5 s, nenhuma voz da equipe, nenhum "gravando".
- [ ] Voz −19,5…−16 LUFS, pico ≤ −1 dBTP, voz ≥ 12 dB acima da trilha (trilha ~ −23 dB no volume do CapCut 0,07).
- [ ] SFX no pico de cada troca; nada estourando. Trilhas de som sem mudo (`validar`) e ouvidas: `ouvir_saida.py` + correlação com o .wav.

## Portão 3 — Tela (grade do Instagram, 1080×1920)
- [ ] Texto em y 420–1500 e x 32,5–1047,5; fora da coluna de ícones (x > 1000 em y 1020–1500).
- [ ] Linha ≤ 760 px centrada; nenhuma palavra sozinha; página não termina em o/de/em/a/que/pra/com.
- [ ] Texto nunca no rosto. Rosto em y ~700–780 no plano normal.
- [ ] `revisar_export.py` → olhar `zona.jpg` quadro a quadro.

## Portão 4 — Movimento
- [ ] A câmera ANDA na tela (comparar 2 quadros do mesmo corte: escala diferente). Key parada no último valor = tempo da key errado.
- [ ] Texto atrás: contorno da pessoa colado (braço/notebook sem duplicar) em 3 quadros de cada momento.
- [ ] Zoom/keyframe com a curva aprovada (esqueleto `curva`), nunca linear em movimento visível.
- [ ] Elemento principal nunca sai do quadro; punch mantém o olho no mesmo lugar.
- [ ] Uma transição-assinatura por vídeo; pico do efeito no quadro exato do corte.

## Portão 5 — Projeto e entrega
- [ ] `capcut_brabo.py validar <projeto>` = VALIDAÇÃO OK (sem mídia offline, sem sobreposição).
- [ ] Edição manual do Matheus intacta (raio-x antes/depois das trilhas dele).
- [ ] Export só se ele pediu: 1080×1920, 30 fps, H.264, nome `DD-MM-AAAA_Projeto_vN.mp4` em `PROJETOS/<projeto>/export/`.
- [ ] `EDICOES.md` do projeto atualizado; aprendizado novo registrado.

## Erros já cometidos neste sistema
| Data | Erro | Regra criada |
|---|---|---|
| 22/10/2026 | 4ª rodada: "só os whoosh" — clicks a 35 % ficavam −5,5 dB abaixo da voz (só agudo, 9 ms) e sumiam. | Click com corpo + `nivelar-sons --acima 5`; conferido gravando a saída (click certo com correlação 0,75–0,84). |
| 22/10/2026 | 3ª rodada: "não saiu os sons dos clicks e zoom" — trilha «Brabo · SFX» MUDA (attribute 1) e material de som do esqueleto. | Motor desmuta trilha própria a cada gravação, som como import novo, `validar` reprova trilha muda; conferência ouvindo a saída (`ouvir_saida.py`). |
| 22/10/2026 | 2ª rodada: ainda sem voz (o esqueleto também marcava extra_type_option 1 / check_flag 62978047) e emendas no D e no A (Inter estática com contornos sobrepostos). | Material de vídeo como import novo (0 / 63487); conferir a forma de onda no clipe. Fonte = Inter limpa (`fonte_limpa.py`); conferir letra grande em zoom na tela. |
| 22/10/2026 | O 1020 inteiro estava MUDO desde o 1º teste: o esqueleto `video` (do 1001) trazia `has_sound_separated: true`; e 44 cópias do material (o CapCut lê a 1ª). Ninguém ouviu antes de entregar. | `garantir_voz` em toda gravação; `validar` reprova; teste no `test_motor`. Conferência sempre com som. |
| 22/10/2026 | "A máscara mexe": a câmera do vídeo principal nunca andou (keys de vídeo contadas do segmento; o CapCut conta do arquivo) e o recorte, que andava, desencontrava do vídeo parado. O "zoom 1,18 medido" de 20/10 era o valor parado. | Motor grava keys de vídeo no tempo do arquivo (`tempo_das_keys`), `migrar-keys` para rascunhos antigos, `validar` acusa keys fora do trecho, teste. Conferir movimento em 2 quadros, não em 1. |
| 20/10/2026 | Com o CapCut aberto durante a conferência (cliques na régua), o 1º corte do 1020 virou 0,9 s e toda a timeline andou 4,7 s; o CapCut salvou sozinho. Legendas e som ficariam 4,7 s fora. | Conferência só por teclado, sem clicar na timeline. `validar` acusa trilha principal mais curta que o texto. Antes de gravar por cima, `validar`. |
| 20/10/2026 | Letreiros laterais saíam cortados na borda e, encostados, passavam por cima do rosto. | Motor mede a largura (Inter, 9,07 px/unidade), reduz até caber em 34 % da largura e encosta na margem de 5 %. |
| 20/10/2026 | "Pele branca": recorte da pessoa gerado pelo OpenCV a partir do HDR do iPhone, sem marcação de cor. | `recorte_pessoa.py` lê o bruto pelo ffmpeg em 10 bits e copia as marcações (BT.2020/HLG); diferença medida 0,15 %. |
| 20/10/2026 | Letras saindo da borda: entrada "zoom" 1,6× em blocos largos; letreiros encostados sem folga do pop. | `teto_escala` por bloco; encostar com folga de 8 %. |
| 20/10/2026 | Legenda e câmera "não puxavam as skills": animação na página (não na palavra), punch estático, sem deriva/zoom out. | `legenda-palavras` e `camera` medidos nos renders aprovados do After (06-referencias). |
| 20/10/2026 | Captura da tela pegou pop-up de 78×24 / a janela do Claude / o player em tela cheia. | `janela_capcut.ps1` (maior janela visível), recaptura com o CapCut na frente, `{ESC}` antes. |
| 20/10/2026 | Teste "ao vivo": o motor gravou no 1019 com o CapCut aberto na tela inicial (13:46:35); às 13:47:01 os projetos 1001 e 1019 saíram da lista e as pastas sumiram do disco. 1001 sem backup (o motor só tinha lido); a Lixeira do CapCut ficou vazia → 1001 perdido. Causa não confirmada. | Proibido gravar com o CapCut aberto. Antes de qualquer escrita, backup de TODOS os rascunhos da pasta (não só do que vai ser gravado). |
