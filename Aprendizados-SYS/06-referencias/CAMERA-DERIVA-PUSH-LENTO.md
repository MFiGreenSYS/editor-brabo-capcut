# Ficha · Câmera: deriva / push lento contínuo (nenhum plano de fala parado)

Estudo de 20/10/2026 nos renders e no código reais do Editor Brabo do After (`Desktop\Pessoal.SYS\AFTER-EDITORBRABO`).
Evidência: E1 medido no render · E2 visto no quadro · E3 lido no código (não medido) · E4 desconhecido.
Medição: casamento SIFT + RANSAC (similaridade) de cada quadro do render com o quadro do clipe-fonte estabilizado (`VIDEOS\est`),
escala relativa à fonte preenchendo 1080 de largura. Scripts e CSVs: scratchpad da sessão 58ed7cbb, `estudo_camera\scripts\`
(`medir_escala.py`, `auto_movs.py`, `curvas.py`) e `estudo_camera\saidas\`.
**Os renders são 23,976 fps**: quadro do render = q24; no CapCut a 30 fps, q30 = q24 × 1,2513.

## Fontes
- `PACHECO\ANTARES\Enviar\ANTARES_Reels_musica.mp4` (APROVADO rev3, "top, ficou excelente", modelo oficial de Reels de construtora).
  Câmera do build: `ANTARES\_trabalho\montagem.json` → `cam` (gerado por `scripts\07_textos.py` l. 99–124).
- `PACHECO\DHAUSS\Enviar\DHAUSS_Reels_musica.mp4` (APROVADO rev5, "ficou top").
- `ARANTES\render\▶ Story 4-7 · Fernando- o rooftop de 16 milhões.mp4` (entregue 12/10). Código `ARANTES\scripts\04_build.jsx` l. 101–103.
- Código sem render local (HD D: desconectado): `Aprendizados-SYS\scripts\plano_reel.py` (ADV/PEDRO talking head),
  `formula_plano.py` (fórmula Joseph), `replica_loira.jsx` (CASA).

## Lógica
- Toda tomada de FALA anda desde o 1º quadro (regra 15/10 "nenhuma imagem começa parada"; 12/10 "fala parada > 2–3 s leva zoom").
  A deriva é um push in lento e contínuo, em escala, até o fim do plano; depois de qualquer zoom rápido ela continua.
- A deriva começa ANTES do corte (key fora do clipe): o 1º quadro visível já está em movimento.
- Quando NÃO: b-roll/drone que já se move (ANTARES q702–780: 99,6 % constante, nenhum zoom digital, E1); plano com letras grandes
  atrás da pessoa no talking head (`plano_reel.py` l. 261, E3); plano tão fechado que a cabeça sairia da grade (`sem_zoom`, E3).
  Pessoa andando até a câmera: deriva menor (gancho ANTARES 106→114 %, comentário "ele mesmo vem até a câmera", E3).

## Receita (números)
| Caso | Escala | Duração / início | Curva | Prova |
|---|---|---|---|---|
| Fala nova (corte de tomada) | base 115 % → +5 % (115,0→120,7) | plano inteiro (128 q24); 1º key 10 q24 (12,5 q30) antes do corte | cam65 (RMSE 0,016 %) | ANTARES q236–364, E1 |
| Fala depois de b-roll | 115,2→120,8 % | 1º key 24 q24 (30 q30) antes | cam65 (0,011 %) | ANTARES q858–969, E1 |
| Gancho (ele anda até a câmera) | 106,0→114,0 % | 198 q24 | cam65 (0,010 %) | ANTARES q0–188, E1 |
| CTA | 134,4→141,9 % (build 1,34→1,42) | 1º key 24 q24 antes | cam65 (0,15 %) | ANTARES q1231–1361, E1 |
| Depois do zoom IN que fica | ×1,03 (147,3→151,7 %) | até o fim do pedaço | cam65 (0,018 %) | ANTARES q369–511, E1 |
| Depois do zoom rápido do número | 230→240 % (+4,3 %) | 22 q24 | cam65 (0,077 %) | ANTARES q584–601, E1 |
| Stories (fala longa) | 100→105 %, âncora no centro (540, 960) | 392 q24 = 16,35 s | cam65 (q90 = 100,27 % = previsto) | ARANTES Story 4 q0–392, E1 |
| Cobertura de imagem | alterna: ímpar afasta 105→100 % | plano inteiro | cam65 | `04_build.jsx` l. 101–103, E3 |
| Talking head ADV | ×1,045 em peça ≥ 2,0 s sem push nem letras de fundo | peça inteira | cam65 | `plano_reel.py` l. 30, 261–263, E3 |
| Fórmula Joseph | +6 % por cena | cena inteira | cam65 por trecho | `formula_plano.py` l. 155–157, E3 |
| Detalhe parado | 50→54 % de camada (×1,08) + desliza ±52 px | plano | cam65 | `AUDITORIA-PROJETOS.md` C12, E3 |
Velocidade medida: +0,5 a +1,1 %/s nos planos longos do ANTARES; até +3 %/s em plano curto (D HAUSS q474–545: +8,7 % em 2,9 s, E1).
Nitidez: a deriva não borra (variância do Laplaciano sem queda nos trechos de deriva, E1).

## Âncora (o ponto que não se move)
- Construtora: ponto fixo r calculado para o rosto cair em (540, 600) no zoom-alvo z: `r = (z·p − tela)/(z − 1)`, preso a
  [0..1080]×[0..1920] (`07_textos.py` l. 106, E3). Medido: ANTARES q0–188 âncora (552, 534) constante; q236–364 (1080, 0) (alvo no
  TOPO: ele desce e o nome cabe acima da cabeça); q1231 (1080, 585) (E1).
- Talking head ADV/PEDRO: âncora nos olhos (`cam = olho + (centro − olho)/z`), olhos a 36 % da altura (y 691) no ADV, 29 % no Pedro (E3).
- D HAUSS (regra D12): rosto em y 700–780 (E3, `MODELO-REELS-CONSTRUTORA\README.md`).

## Tradução CapCut [MOTOR]
- Keys de escala a cada 2 q30 seguindo a curva cam65; posição compensada para a âncora não andar:
  `T = (r − C)·(1 − s)` em px (C = 540, 960) → `transform.x = Tx/540`, `transform.y = −Ty/960` (unidade = meio canvas, y para cima).
- O After interpola a DISTÂNCIA da câmera 3D (1/escala), não a escala: `s(t) = 1 / (1/s0 + y(t)·(1/s1 − 1/s0))`, y = cubic-bezier
  da curva. Em deriva (+5 %) a diferença é desprezível (RMSE 0,016 % contra 0,032 % na escala direta, E1).
- Pré-rolagem: calcule o valor no 1º quadro do clipe como se a curva tivesse começado 12,5 q30 antes (30 q30 depois de b-roll/CTA).
- cam65 normalizada (0 a 100 % do tempo, passos de 10 %): 0 · 0,009 · 0,042 · 0,112 · 0,252 · 0,500 · 0,748 · 0,888 · 0,958 · 0,991 · 1.

## Gatilhos de pedido
"nada parado", "cena parecendo foto / muito parada" (Madalena C12), "fala parada", "dá vida", "câmera viva".
