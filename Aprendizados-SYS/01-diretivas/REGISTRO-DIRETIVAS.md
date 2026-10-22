# Registro de diretivas do Matheus · Editor Brabo CapCut (MKT iGreen)

Uma linha por diretiva, com data. A mais nova em cima. Diretiva que vale também para o After fica no registro de lá;
aqui só o que é do CapCut/MKT iGreen ou o que veio de lá e vale aqui (marcado "(herdada)").

| Data | Diretiva | Onde aplicar |
|---|---|---|
| 22/10/2026 | "Transformar isso para replicar para outros editores, Claude etc., de forma idêntica cada uma das skills": o sistema virou repositório Git (regras sim, projetos não). Melhoria = branch + MOTOR OK + PR aprovado pelo Matheus. | todo o sistema |
| 22/10/2026 | "Não saiu os sons dos clicks e zoom… tem que ser dinâmicos": SFX tem que tocar e variar (rodízio de click_a/b/c e whoosh_a/b/c, volume variando). "Tá excelente" no resto (voz, letras, câmera). | sound design |
| 22/10/2026 | "Os textos tão recortados, linhas nos A, precisam ser textos editáveis": letreiro é TEXTO do CapCut (editável), com a Inter limpa (sem emenda). "Click quando mudar a posição da câmera com zoom… não em todos, alternando": `cliques-camera --a-cada 2`. | letreiros, texto atrás, sound design, câmera |
| 22/10/2026 | **"Nunca tire a voz do apresentador"** (o 1020 estava mudo) e "a máscara mexe" (a pessoa recortada não casava com o vídeo de baixo). A voz é intocável; o recorte tem que bater quadro a quadro. Travado no motor (`garantir_voz`, `validar`, teste). | todas; texto atrás, câmera |
| 22/10/2026 | "Retire os textos abaixo e deixe somente os textos impactantes… utilize efeitos de textos" (aula ACADEMY M1, 16:9): sem legenda corrida embaixo; só letreiros de impacto e texto atrás, com efeito de texto nativo do CapCut (desfoque/ampliar). Confirmar se vale para toda aula 16:9. | letreiros, texto atrás, legendas |
| 20/10/2026 | "Tem letras saindo das bordas, a pele está branca, não está puxando as skills… olhe o projeto do After": nenhuma letra fora da tela nem na animação; cor da pessoa recortada igual ao vídeo; legenda e câmera como nos renders aprovados do After. | letreiros, texto atrás, legenda, câmera |
| 20/10/2026 | Criar skills de edição no CapCut "no estilo do Editor Brabo do After", **exclusivas para o MKT iGreen**. | todo o sistema |
| 25/09/2026 (herdada) | Não renderizar/exportar sem ele pedir; revisar por quadros. | `capcut-igreen-revisao-entrega` |
| 25/09/2026 (herdada) | Movimento com keyframe velocity 65/65 (alternativas 100→10, 65→100, 40→100); nada de 33 %. No CapCut = curva personalizada capturada. | `capcut-igreen-movimento` |
| 24/09/2026 (herdada) | Não alucinar: entender a lógica, planejar e perguntar o que faltar antes de montar. | todas |
| 12/10/2026 (herdada) | Plano editável antes de montar ("aplicar isso em tudo antes"). | `capcut-igreen-reels` |
| 11/10/2026 (herdada) | Zona segura do Instagram: texto em y 420–1500, x 32,5–1047,5, fora da coluna de ícones (x > 1000 em y 1020–1500). | legendas, revisão |
| 01/10/2026 (iGreen.SYS) | Ícone e logo SEMPRE de `07_Marca-Assets\Aplicações logo iGreen\` (Regra 4). | `capcut-igreen-marca` |
| 29/09/2026 (iGreen.SYS) | Projeto novo = pasta `DD-MM-AAAA_Nome`. | `novo_projeto.py` |

## Pendentes de confirmar com o Matheus (não tratar como regra ainda)
- Estilo da legenda de marca (proposta em `00-CEREBRO.md` §2): Inter ExtraBold branca + destaque `#18FF00` + sombra suave.
- "consultor" × "licenciado" no texto de vídeo (o site novo usa "licenciado").
- "iGreen Energy" × "Grupo iGreen" na assinatura final.
- Zoom: no After é câmera 3D com profundidade; no CapCut a proposta é escala por keyframe 65/65 (+ desfoque de fundo quando
  houver elemento em destaque). Precisa do ok dele.
