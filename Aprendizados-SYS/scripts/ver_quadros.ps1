# ver_quadros.ps1 — leva a agulha do CapCut a cada QUADRO pedido e fotografa a janela (editor maximizado).
#   powershell -NoProfile -File ver_quadros.ps1 -Quadros "45,84,1725" -Pasta C:\saida
# Navegação só por teclado, exata (medido 20/10/2026): {HOME} = quadro 0 · Shift+→ = +10 quadros · → = +1 quadro.
# Nada de clicar na régua (os cliques caíam em tempos errados quando a janela mudava) e nada de clicar em clipe.
# Teclas sempre pelo clique.ps1 (trava: só digita com o CapCut em primeiro plano).
param([string]$Quadros, [string]$Pasta)
$aqui = Split-Path -Parent $MyInvocation.MyCommand.Path
New-Item -ItemType Directory -Force $Pasta | Out-Null
function Teclas([string]$k) {
  & powershell -NoProfile -ExecutionPolicy Bypass -File "$aqui\clique.ps1" -SemClique -Teclas $k | Out-Null
  if ($LASTEXITCODE -ne 0) { "ABORTADO: CapCut não está na frente"; exit 2 }
}
foreach ($qs in ($Quadros -split ",")) {
  $q = [int]$qs
  Teclas "{HOME}"; Start-Sleep -Milliseconds 500
  $dez = [math]::Floor($q / 10); $um = $q % 10
  while ($dez -gt 0) {                                   # blocos de 50: repetições grandes perdiam teclas (20/10)
    $b = [math]::Min(50, $dez); Teclas "+{RIGHT $b}"; $dez -= $b; Start-Sleep -Milliseconds 350
  }
  if ($um -gt 0) { Teclas "{RIGHT $um}" }
  Start-Sleep -Milliseconds (4000 + [int]($q / 30))      # o player leva 2–4 s para mostrar o quadro novo
  & powershell -NoProfile -ExecutionPolicy Bypass -File "$aqui\clique.ps1" -SemClique | Out-Null   # o Claude às vezes vem para a frente
  Start-Sleep -Milliseconds 400
  $nome = "q{0:00000}.png" -f $q
  & powershell -NoProfile -ExecutionPolicy Bypass -File "$aqui\tela.ps1" -Janela CapCut -Largura 1600 -Saida (Join-Path $Pasta $nome) | Out-Null
  "quadro $q ($([math]::Round($q / 30.0, 3)) s) -> $nome"
}
