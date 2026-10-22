---
name: capcut-igreen-estudar-referencia
description: Estudar e replicar referências de vídeo para o MKT iGreen no CapCut pelo método do Editor Brabo - medir número (nunca adjetivo), ficha por técnica com etiqueta CapCut (MOTOR / CAPTURAR / ASSAR / SEM EQ.), engine de replicação em 8 etapas com evidência E1-E4 e validação P0-P3, replicar efeito decompondo forma/textura/luz/câmera/revelação. Use quando o Matheus mandar vídeo, print, perfil, playlist ou tutorial de referência, ou pedir "faz igual a esse", "replica", "estuda essas referências", "aprende esse efeito".
---

# Editor Brabo CapCut · Estudar e replicar referências

Método herdado: `Aprendizados-SYS/05-herdado-do-after/LEIS-E-METODO.md` §E. Fichas novas vão para `Aprendizados-SYS/06-referencias/`.

## Estudar (analista: mede, não anima)
1. Material: vídeo local (pedir ok antes de baixar; `yt-dlp` só com o tamanho dito). Quadros: `ffmpeg` em pontos de corte
   (`select='gt(scene,0.3)'`) e folha de contato; transcrição com tempo (`whisper --word_timestamps`).
2. Ficha por técnica: **lógica** (quando usar e quando NÃO) · material de entrada · **receita com números** (px em 1080×1920 ou
   1920×1080, quadros a 30 fps, curvas traduzidas para as 4 da casa) e quadro-prova · o que é motor e o que é clique ·
   **etiqueta CapCut** [MOTOR] / [CAPTURAR: recurso] / [ASSAR] / [SEM EQ.] · upgrade pelas leis da casa · gatilhos de pedido.
3. Fecha com síntese (o que é fixo, recorrente, contextual, exceção) + linha no `00-CEREBRO.md` + diretiva se o Matheus decidir.
Evidência: E1 medido · E2 visto · E3 inferido · E4 desconhecido. Correlação ≠ causa. Não inventar o que não mediu.

## Replicar (diretor + motor)
1. Spec: cada evento com tempo, elemento, entrada/saída, curva, som — campo não determinado fica `null` e vira pergunta.
2. Plano aprovado (página editável) com a **lista de captura** (tudo [CAPTURAR] feito 1× na interface antes do build).
3. Build pelo motor; texturas/partículas/luz [ASSAR] como MOV/PNG com alfa que o motor posiciona e anima.
4. Piloto num trecho → validação: tempo antes de cor; tipografia região por região; gancho e fecho (3 s) pesam mais.
   Defeitos P0 nada comparável · P1 tempo/corte/tipografia > 2 q · P2 enquadramento/cor/som · P3 menor. Pendente não é aprovado.
5. "2D simples que reproduz > efeito complexo." Réplica não copia os erros da referência. Versões quando houver dúvida de gosto.

## Revisor (BLOQUEIA / DEVE CORRIGIR / PODE MELHORAR, sempre com quadro + evidência + correção)
Lista do que reprova: `LEIS-E-METODO.md` §F e `04-auditoria/CHECKLIST-ERRO-ZERO-CAPCUT.md`. Não entrega com BLOQUEIA aberto.
Agentes do sistema: `.claude/agents/capcut-analista.md`, `capcut-diretor.md`, `capcut-revisor.md`.
