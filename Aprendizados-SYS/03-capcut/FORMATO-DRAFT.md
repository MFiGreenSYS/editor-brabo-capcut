# Formato do rascunho do CapCut desktop 9.5 (Windows) — medido em 20/10/2026

Fonte: rascunhos `1001` (projeto real, 146 s, 1920×1080, 17 trilhas) e `1019` (vazio, 9:16) desta máquina, mais a biblioteca de
referência `Pessoal.SYS\MR-Editor.SYS\Ref-editor-jason-cooperson\repos\capcut\pyCapCut` (formato de texto e keyframe).

## Onde fica
`%LOCALAPPDATA%\CapCut\User Data\Projects\com.lveditor.draft\<nome>\`
- `draft_content.json` — a linha do tempo (JSON ABERTO nesta versão; o `crypto_key_store.dat` existe mas o conteúdo não está cifrado).
- `Timelines\<id do draft_content>\draft_content.json` — **segunda cópia** (CapCut 9.x tem várias timelines por projeto; `timeline_layout.json`
  lista). O motor grava as duas e os `.bak`.
- `draft_meta_info.json` — nome, duração (`tm_duration`), lista de mídia importada. `root_meta_info.json` (na pasta-mãe) — lista da tela inicial.
- `template-2.tmp` tem o mesmo tamanho do conteúdo (temporário do CapCut; o motor não mexe).
Se uma versão futura cifrar o `draft_content.json` (1º byte ≠ `{`), o motor para e avisa.

## Estrutura
- `tracks[]`: `{id, type: video|audio|text|filter|effect|sticker, segments[], name, attribute, flag}`. A 1ª de vídeo é a principal.
- `segments[]`: `target_timerange {start, duration}` (na linha do tempo), `source_timerange` (no arquivo; `null` em texto),
  `speed`, `volume`, `clip {scale{x,y}, rotation, transform{x,y}, alpha, flip}`, `material_id`, `extra_material_refs[]`
  (speed, placeholder_info, canvas_color, sound_channel_mapping, vocal_separation, material_animation, transition…),
  `common_keyframes[]`.
- `materials{}`: listas por tipo (`videos`, `audios`, `texts`, `material_animations`, `transitions`, `effects`, `speeds`, `canvases`,
  `audio_fades`, `beats`, …), cada item com `id`.
- Tempo em **microssegundos**. `fps` 30. Segmento acelerado: `source.duration = target.duration × speed`.
- `clip.transform`: normalizado, 0 = centro, ±1 = borda; **y positivo = para cima**. Pixel (1080×1920): `y_px = 960 − y·960`.
  Zona segura do texto (y 420–1500 px) ⇒ y normalizado entre −0,5625 e +0,5625.
- Texto (`materials.texts[]`): `content` = string JSON `{"text": "...", "styles": [{fill, font, size, bold, range:[ini,fim], strokes, shadows}]}`;
  `range` em unidades UTF-16. Vários estilos = trechos com cor/fonte diferentes (é assim que o destaque verde é feito). `type` `text` ou `subtitle`.
- Keyframe: `common_keyframes[] = {id, property_type, keyframe_list[{id, time_offset, values[], curveType, left_control, right_control}]}`.
  `time_offset` relativo ao começo do segmento. Propriedades: `KFTypePositionX/Y`, `KFTypeRotation`, `UNIFORM_SCALE`, `KFTypeScaleX/Y`,
  `KFTypeAlpha`, `KFTypeVolume`, `KFTypeBrightness/Contrast/Saturation`. Curva personalizada: capturar de um key real (`capturar --curva`).
- Marcadores da timeline: `time_marks` (o motor mostra no raio-x).
- Recursos da biblioteca do CapCut (SFX, filtros, transições, animações) apontam para `User Data\Cache\…` com `effect_id`/`resource_id`:
  só funcionam se baixados nesta máquina → **capturar de um rascunho real**, nunca escrever do zero.

## Por que "esqueletos"
O JSON tem dezenas de campos que mudam entre versões. Em vez de inventar, o motor clona um segmento real (com materiais e
animações) e troca só tempo, texto, caminho e escala. Molde novo = Matheus faz uma vez no CapCut (MODELO iGreen) → `capturar`.
Esqueletos atuais: `video`, `audio` (do 1001). A capturar: `legenda`, `legenda-claro`, `titulo`, `nome`, `cta`, `curva`.

## Como o CapCut se comporta (medido pelo vigia em 20/10/2026)
- **Projeto aberto no editor = arquivo `.locked` na pasta do projeto** (criado ao abrir, apagado ao voltar para a tela inicial).
  O motor recusa gravar se ele existir.
- "Criar projeto" cria a pasta na hora (nome = data MMDD, ex.: `1020`), com `Timelines/<id>/`, `timeline_layout.json`,
  `Timelines/project.json`, `attachment/patch/mini_draft.json` e registra em `root_meta_info.json`.
- O card da tela inicial lê a duração do `draft_meta_info.json`; o motor não mexe nele (mostra 00:00 até o CapCut regravar).
- Fechar o CapCut pela janela (CloseMainWindow) primeiro volta à tela inicial; um segundo fechamento sai do programa.
- **Incidente 13:47:01 (20/10)**: com o CapCut aberto na tela inicial, o motor gravou no `1019` (incluindo o `draft_meta_info`);
  ~25 s depois o CapCut tirou o 1001 e o 1019 da lista, registrou-os em `.recycle_bin/root_meta_info.json`, mas as pastas sumiram
  e a Lixeira do app ficou vazia. 1001 perdido (timeline em texto: `_backups/1001_reconstrucao/TIMELINE-1001.md`). Causa não
  confirmada. Desde então: gravar só com o CapCut fechado, backup de TODOS os rascunhos, não tocar no `draft_meta_info`.

## Pendências de verificação (marcar aqui quando confirmar abrindo no CapCut)
- [x] Rascunho com cortes gerados pelo motor abre e toca no CapCut 9.5 (1020, 44 cortes de um .MOV 4K, 20/10/2026).
- [x] Legenda `basico` aparece com o texto certo (1020, 145 páginas) e o 2º estilo (destaque verde) funciona.
- [x] **Alfa por estilo de texto** (`fill.alpha` 0) funciona: legenda Apple com a palavra aparecendo no lugar (20/10, conferido na tela).
- [x] **Vídeo com alfa** (ProRes 4444 `yuva444p`) funciona como camada: texto atrás da pessoa (4 momentos, 20/10).
- [x] **Fonte por caminho de arquivo** (Inter da marca, sem instalar) funciona.
- [x] Keyframes `KFTypeScaleX` + `KFTypePositionX/Y` em vídeo e texto (pop do letreiro). O "zoom 1,18 medido" de 20/10 era o último valor parado
  (ver a regra do tempo da key abaixo).
- [x] `KFTypeAlpha` em vídeo (flash branco visível em 156,2 s).
- [x] Ordem das camadas = ordem das trilhas no JSON (trilha mais tarde = por cima).
- [x] Tamanho de texto: 1 unidade = 9,07 px de "em" em quadro de 1080 de altura (medido em 16:9).
- [x] **`KFTypeAlpha` em TEXTO NÃO funciona** (20/10: a palavra com alfa 0→0,42→0,70 aparece já cheia). Fade/blur de texto =
  animação nativa (capturar). Em VÍDEO/IMAGEM o alfa por keyframe funciona.
- [x] **Imagem (PNG) é ajustada à LARGURA do quadro** com escala 1: escala real = largura do PNG ÷ largura da tela (pílula gigante, 20/10).
- [x] **HDR do iPhone** (HEVC 10 bits HLG BT.2020 / Dolby Vision 8.4): camada derivada do bruto tem que manter a cor e as marcações
  (ffmpeg direto do bruto, sem passar pelo OpenCV) — senão a pessoa recortada fica lavada ("pele branca", 20/10).
- [x] **Animação nativa de texto pelos IDs da biblioteca** (metadados do pyCapCut, migrados do Jianying) funciona no CapCut 9.5:
  `material_animations` tipo `sticker_animation` com `{"type": "in"|"out", "id"=resource_id, "start", "duration"}` referenciado no
  segmento. Visto na tela em 22/10: **desfoque** (6923135604519604737, sai do blur) e **ampliar** (6724919499042066958, cresce +
  aparece). O CapCut baixa o efeito ao abrir o projeto (aparece "Cancelar" na timeline enquanto carrega).
- [x] **Tempo da key de VÍDEO/ÁUDIO = tempo NO ARQUIVO**, não do começo do segmento (medido em 22/10 no 1020: com keys de 0 a 7 s num corte que
  começa aos 75 s do bruto, o CapCut segurou o último valor; o recorte .mov, que começa no 0, andava certo). `time_offset` = início do
  trecho no bruto + tempo no segmento × vel. Texto (sem source_timerange) conta do segmento. O motor converte ao carregar/salvar
  (`tempo_das_keys`); rascunho antigo: `migrar-keys`. Conferido depois na tela (22/10, 16 quadros): câmera
  igual ao mandado (±0,01) e recorte colado (≤ 0,6 %). **Toda câmera/zoom/tremida do motor antes de 22/10 ficou parada no último valor.**
- [x] **`has_sound_separated: true` no material de vídeo = vídeo MUDO** (o CapCut acha que o som foi extraído). Veio do esqueleto do 1001.
- [x] **Material com id repetido**: o CapCut lê a 1ª cópia (o 1020 tinha 44 cópias do bruto). O motor deixa uma só (`garantir_voz`).
- [x] Pastas movidas: o painel de mídia (draft_meta_info) guarda os caminhos antigos e o CapCut abre "Vincular mídia" — "Cancelar" não
  afeta a timeline, que já está no caminho novo.
- [x] **Voz de verdade** (22/10, 2ª rodada): só `has_sound_separated: false` NÃO bastou — o material do esqueleto também trazia
  `extra_type_option: 1` e `check_flag: 62978047`. Com 0 e 63487 (import novo, igual ao pyCapCut) a **forma de onda aparece no clipe**
  = o CapCut reconhece o som. Conferência da voz pela tela: forma de onda embaixo dos cortes.
- [x] **Fonte com contornos sobrepostos** (Inter estática: flag OVERLAP_SIMPLE) vira emenda no texto do CapCut (risco na haste do D, no A).
  `fonte_limpa.py` une os contornos → `Aprendizados-SYS/fontes/Inter-limpa/` (mesmo desenho). Conferido na tela: D e A limpos.
- [x] **Trilha muda = `attribute` com bit 1** (pyCapCut: `attribute = int(mute)`). A «Brabo · SFX» voltou do CapCut com 1 e nenhum SFX tocava
  (22/10). Material de som do esqueleto (check_flag 1, music_id vazio) trocado pelo de import novo (check_flag 3, music_id = local_material_id
  = id). Depois disso o CapCut manteve 0 ao abrir, e a gravação da saída de som (`ouvir_saida.py`) achou o whoosh e o click no tempo.
- [ ] Os outros IDs do motor (`EFEITO_ENTRADA`/`EFEITO_SAIDA`: surgir, pular, brilho, varredura, sumir, encolher) ainda não vistos.
- [ ] Legenda do esqueleto `legenda` (MODELO iGreen).
- [ ] Áudio local importado (`type: extract_music`) toca — sons da casa precisam do ouvido do Matheus.

## Conferir no CapCut pela tela (método que funcionou, 20/10/2026)
- Abrir o CapCut, duplo clique no card, `clique.ps1 -SemClique -Maximizar`, depois `ver_quadros.ps1 -Quadros "…"`.
- Navegação SÓ por teclado: `{HOME}` = 0 · Shift+→ = +10 quadros · → = +1 (em blocos de 50; repetições grandes perdem teclas).
  Conferir o quadro pelo contador que aparece na captura (às vezes ainda se perde tecla: refazer o quadro).
- Esperar 4 s por quadro (o player leva 2–4 s para renderizar). A régua (clique) é imprecisa e já houve corte encurtado com o
  CapCut aberto: nada de clicar na timeline.
- O CapCut às vezes troca a "janela principal" por um pop-up, fica minimizado ou entra em tela cheia no player (`{ESC}` sai):
  `janela_capcut.ps1` acha a maior janela visível e o `clique.ps1` restaura se estiver minimizada.
- **Depois de conferir: `validar`** (pega timeline encurtada por baixo do texto).
