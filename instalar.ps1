# instalar.ps1 — prepara este PC para o Editor Brabo CapCut (MKT iGreen) e prova que o motor funciona aqui.
# Uso (PowerShell, na pasta do repositório):   powershell -NoProfile -ExecutionPolicy Bypass -File .\instalar.ps1
# Não instala o CapCut nem o Claude: só confere, instala as bibliotecas Python e roda o teste do motor (MOTOR OK).
$ErrorActionPreference = "Stop"
$raiz = Split-Path -Parent $MyInvocation.MyCommand.Path
$falhas = @()
function Ok($m) { Write-Host "  OK    $m" -ForegroundColor Green }
function Falta($m, $como) { Write-Host "  FALTA $m" -ForegroundColor Red; if ($como) { Write-Host "        → $como" -ForegroundColor Yellow }; $script:falhas += $m }

Write-Host "`nEditor Brabo CapCut · conferindo este PC`n" -ForegroundColor Cyan

# 1. Python 3.12+
$py = Get-Command python -ErrorAction SilentlyContinue
if ($py) {
  $v = (& python --version) 2>&1
  if ("$v" -match "Python 3\.(1[2-9]|[2-9]\d)") { Ok "$v" } else { Falta "Python 3.12 ou mais novo (achei: $v)" "winget install Python.Python.3.12" }
} else { Falta "Python" "winget install Python.Python.3.12  (marque 'Add to PATH')" }

# 2. ffmpeg + ffprobe
foreach ($exe in "ffmpeg", "ffprobe") {
  if (Get-Command $exe -ErrorAction SilentlyContinue) { Ok "$exe no PATH" } else { Falta "$exe" "winget install Gyan.FFmpeg  (e abra um terminal novo)" }
}

# 3. CapCut desktop 9.5 (o formato do rascunho foi medido nesta versão)
$apps = Join-Path $env:LOCALAPPDATA "CapCut\Apps"
$ver = if (Test-Path $apps) { Get-ChildItem $apps -Directory | Where-Object Name -match '^\d+\.\d+' | Sort-Object { [version]$_.Name } | Select-Object -Last 1 } else { $null }
if (-not $ver) { Falta "CapCut desktop" "instale pelo site oficial (capcut.com) e abra uma vez" }
elseif ($ver.Name -like "9.5.*") { Ok "CapCut $($ver.Name)" }
else { Write-Host "  AVISO CapCut $($ver.Name): o sistema foi validado no 9.5. O teste abaixo diz se o formato mudou." -ForegroundColor Yellow }
$rascunhos = Join-Path $env:LOCALAPPDATA "CapCut\User Data\Projects\com.lveditor.draft"
if (Test-Path $rascunhos) { Ok "pasta de rascunhos do CapCut" } else { Write-Host "  AVISO pasta de rascunhos ainda não existe (abra o CapCut e crie um projeto vazio)" -ForegroundColor Yellow }

# 4. bibliotecas Python
if ($py) {
  Write-Host "`nInstalando as bibliotecas (requirements.txt; o whisper traz o torch e demora na 1ª vez)..." -ForegroundColor Cyan
  & python -m pip install --user -r (Join-Path $raiz "requirements.txt")
  if ($LASTEXITCODE -eq 0) { Ok "bibliotecas Python" } else { Falta "bibliotecas Python" "rode de novo e veja o erro do pip acima" }
}

# 5. teste do motor (grava só numa cópia temporária; pode rodar com o CapCut aberto)
if ($falhas.Count -eq 0) {
  Write-Host "`nTeste do motor..." -ForegroundColor Cyan
  $saida = & python -I (Join-Path $raiz "Aprendizados-SYS\scripts\test_motor.py") 2>&1
  $saida | Select-Object -Last 6 | ForEach-Object { Write-Host "  $_" }
  if ("$saida" -match "MOTOR OK") { Ok "MOTOR OK" } else { Falta "teste do motor" "mande a saída acima para o Matheus (ou abra o Claude nesta pasta e peça para investigar)" }
}

Write-Host ""
if ($falhas.Count -eq 0) {
  Write-Host "Tudo pronto. Abra o Claude Code (aba Code do app) NESTA pasta e peça, por exemplo:" -ForegroundColor Green
  Write-Host "  'novo projeto: Reels do licenciado X' · 'decupa e legenda esse vídeo' · 'texto atrás da pessoa'" -ForegroundColor Green
} else {
  Write-Host "Faltou: $($falhas -join ', '). Resolva e rode o instalar.ps1 de novo." -ForegroundColor Red
  exit 1
}
