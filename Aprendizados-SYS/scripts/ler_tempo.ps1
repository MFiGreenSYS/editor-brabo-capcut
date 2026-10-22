# ler_tempo.ps1 — lê o contador de tempo do player do CapCut (hh:mm:ss:qq) com o OCR do próprio Windows (Windows.Media.Ocr).
#   powershell -NoProfile -File ler_tempo.ps1 -Imagem recorte.png   → imprime "segundos quadro_total texto" ou "?"
param([string]$Imagem)
Add-Type -AssemblyName System.Runtime.WindowsRuntime
$null = [Windows.Storage.StorageFile, Windows.Storage, ContentType = WindowsRuntime]
$null = [Windows.Media.Ocr.OcrEngine, Windows.Foundation, ContentType = WindowsRuntime]
$null = [Windows.Graphics.Imaging.BitmapDecoder, Windows.Foundation, ContentType = WindowsRuntime]
$asTask = ([System.WindowsRuntimeSystemExtensions].GetMethods() | Where-Object { $_.Name -eq 'AsTask' -and $_.GetParameters().Count -eq 1 -and $_.GetParameters()[0].ParameterType.Name -eq 'IAsyncOperation`1' })[0]
function Espera($op, [Type]$tipo) { $t = $asTask.MakeGenericMethod($tipo).Invoke($null, @($op)); $t.Wait(-1) | Out-Null; $t.Result }
$arq = Espera ([Windows.Storage.StorageFile]::GetFileFromPathAsync((Resolve-Path $Imagem).Path)) ([Windows.Storage.StorageFile])
$fluxo = Espera ($arq.OpenAsync([Windows.Storage.FileAccessMode]::Read)) ([Windows.Storage.Streams.IRandomAccessStream])
$dec = Espera ([Windows.Graphics.Imaging.BitmapDecoder]::CreateAsync($fluxo)) ([Windows.Graphics.Imaging.BitmapDecoder])
$bmp = Espera ($dec.GetSoftwareBitmapAsync()) ([Windows.Graphics.Imaging.SoftwareBitmap])
$ocr = [Windows.Media.Ocr.OcrEngine]::TryCreateFromUserProfileLanguages()
$res = Espera ($ocr.RecognizeAsync($bmp)) ([Windows.Media.Ocr.OcrResult])
$txt = ($res.Text -replace '[Oo]', '0' -replace '[Il|]', '1' -replace '\s', '')
$m = [regex]::Match($txt, '(\d\d):(\d\d):(\d\d):(\d\d)')
if ($m.Success) {
  $q = ([int]$m.Groups[1].Value * 3600 + [int]$m.Groups[2].Value * 60 + [int]$m.Groups[3].Value) * 30 + [int]$m.Groups[4].Value
  "{0:0.000} {1} {2}" -f ($q / 30.0), $q, $m.Value
} else { "? $txt" }
