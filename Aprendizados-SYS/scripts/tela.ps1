# tela.ps1 — captura da tela (ou só da janela de um programa) para o Editor Brabo enxergar o CapCut.
#   powershell -NoProfile -File tela.ps1 -Saida C:\caminho\tela.png [-Janela CapCut] [-Largura 1600]
# Com -Janela, recorta a janela principal do processo e imprime o retângulo em pixels de tela (para clicar com clique.ps1).
param([string]$Saida = "$env:TEMP\brabo_tela.png", [string]$Janela = "", [int]$Largura = 1600, [string]$Retangulo = "")
# -Retangulo "x,y,w,h": captura esse pedaço da tela (o CapCut às vezes troca a "janela principal" por um pop-up de dica de 78×24)
Add-Type -AssemblyName System.Windows.Forms, System.Drawing
Add-Type @"
using System; using System.Runtime.InteropServices;
public class JanBrabo {
  [StructLayout(LayoutKind.Sequential)] public struct RECT { public int L, T, R, B; }
  [DllImport("user32.dll")] public static extern bool SetProcessDPIAware();
  [DllImport("user32.dll")] public static extern bool SetProcessDpiAwarenessContext(IntPtr c);
  [DllImport("user32.dll")] public static extern bool GetWindowRect(IntPtr h, out RECT r);
}
"@
# DPI por monitor (V2): captura e clique nas MESMAS coordenadas físicas (o monitor de cima está a 125%)
if (-not [JanBrabo]::SetProcessDpiAwarenessContext([IntPtr](-4))) { [JanBrabo]::SetProcessDPIAware() | Out-Null }
if ($Retangulo) {
  $x, $y, $w, $h = ($Retangulo -split "," | ForEach-Object { [int]$_ })
} elseif ($Janela) {
  . "$PSScriptRoot\janela_capcut.ps1"
  $hj = JanelaGrande $Janela
  if ($hj -eq [IntPtr]::Zero) { "sem janela visível de $Janela"; exit 2 }
  $r = New-Object JanBrabo+RECT
  [JanBrabo]::GetWindowRect($hj, [ref]$r) | Out-Null
  $x, $y, $w, $h = $r.L, $r.T, ($r.R - $r.L), ($r.B - $r.T)
} else {
  $b = [System.Windows.Forms.SystemInformation]::VirtualScreen
  $x, $y, $w, $h = $b.Left, $b.Top, $b.Width, $b.Height
}
$bmp = New-Object System.Drawing.Bitmap $w, $h
$g = [System.Drawing.Graphics]::FromImage($bmp)
$g.CopyFromScreen($x, $y, 0, 0, $bmp.Size)
if ($w -le $Largura) { $Largura = $w }
$h2 = [int]($h * $Largura / $w)
$out = New-Object System.Drawing.Bitmap $bmp, $Largura, $h2
$out.Save($Saida, [System.Drawing.Imaging.ImageFormat]::Png)
"$Saida  tela x=$x y=$y w=$w h=$h  -> imagem ${Largura}x$h2  (escala $([math]::Round($w / $Largura, 4)))"
