# clique.ps1 — clique/tecla na tela para o Editor Brabo operar o CapCut (coordenadas de tela do tela.ps1).
#   powershell -NoProfile -File clique.ps1 -X 1227 -Y -1109 [-Duplo] [-Teclas "^s"] [-Frente CapCut] [-SemClique]
# TRAVA (20/10/2026: um clique caiu no Chrome do Matheus porque o CapCut não veio para a frente): só clica/digita se a janela
# em primeiro plano E a janela sob o ponto forem do processo -Frente. Senão aborta com código 2 e não faz nada.
param([int]$X = 0, [int]$Y = 0, [switch]$Duplo, [string]$Teclas = "", [string]$Frente = "CapCut", [switch]$SemClique, [switch]$Maximizar)
Add-Type -AssemblyName System.Windows.Forms
Add-Type @"
using System; using System.Runtime.InteropServices;
public class CliBrabo {
  [StructLayout(LayoutKind.Sequential)] public struct P { public int X, Y; }
  [DllImport("user32.dll")] public static extern bool SetProcessDPIAware();
  [DllImport("user32.dll")] public static extern bool SetProcessDpiAwarenessContext(IntPtr c);
  [DllImport("user32.dll")] public static extern bool SetCursorPos(int x, int y);
  [DllImport("user32.dll")] public static extern void mouse_event(uint f, uint dx, uint dy, uint d, IntPtr e);
  [DllImport("user32.dll")] public static extern void keybd_event(byte k, byte s, uint f, IntPtr e);
  [DllImport("user32.dll")] public static extern bool SetForegroundWindow(IntPtr h);
  [DllImport("user32.dll")] public static extern IntPtr GetForegroundWindow();
  [DllImport("user32.dll")] public static extern bool ShowWindow(IntPtr h, int c);
  [DllImport("user32.dll")] public static extern IntPtr WindowFromPoint(P p);
  [DllImport("user32.dll")] public static extern IntPtr GetAncestor(IntPtr h, uint f);
  [DllImport("user32.dll")] public static extern uint GetWindowThreadProcessId(IntPtr h, out uint pid);
}
"@
# DPI por monitor (V2): captura e clique nas MESMAS coordenadas físicas (o monitor de cima está a 125%)
if (-not [CliBrabo]::SetProcessDpiAwarenessContext([IntPtr](-4))) { [CliBrabo]::SetProcessDPIAware() | Out-Null }

function Dono([IntPtr]$h) { $id = 0; [CliBrabo]::GetWindowThreadProcessId([CliBrabo]::GetAncestor($h, 2), [ref]$id) | Out-Null; try { (Get-Process -Id $id).ProcessName } catch { "?" } }

. "$PSScriptRoot\janela_capcut.ps1"
$hj = JanelaGrande $Frente      # a maior janela visível (o MainWindowHandle do CapCut às vezes é um pop-up de dica)
if ($hj -eq [IntPtr]::Zero) {   # minimizada: restaura a janela principal (20/10: o CapCut apareceu minimizado no meio da conferência)
  $p = Get-Process $Frente -ErrorAction SilentlyContinue | Where-Object { $_.MainWindowHandle -ne 0 } | Select-Object -First 1
  if ($p) { [CliBrabo]::ShowWindow($p.MainWindowHandle, 9) | Out-Null; Start-Sleep -Milliseconds 800; $hj = JanelaGrande $Frente }
}
if ($hj -eq [IntPtr]::Zero) { "ABORTADO: $Frente sem janela"; exit 2 }
if ((Dono ([CliBrabo]::GetForegroundWindow())) -ne $Frente) {
  [CliBrabo]::keybd_event(0x12, 0, 0, [IntPtr]::Zero); [CliBrabo]::keybd_event(0x12, 0, 2, [IntPtr]::Zero)   # Alt libera o primeiro plano
  [CliBrabo]::SetForegroundWindow($hj) | Out-Null
  Start-Sleep -Milliseconds 500
}
if ($Maximizar) { [CliBrabo]::ShowWindow($hj, 3) | Out-Null; Start-Sleep -Milliseconds 700 }   # posição fixa para os cliques
$fg = Dono ([CliBrabo]::GetForegroundWindow())
if ($fg -ne $Frente) { "ABORTADO: primeiro plano é '$fg', não $Frente"; exit 2 }
if ($SemClique -and -not $Teclas) { "primeiro plano: $Frente"; exit 0 }
if (-not $SemClique) {
  $p = New-Object CliBrabo+P; $p.X = $X; $p.Y = $Y
  $sob = Dono ([CliBrabo]::WindowFromPoint($p))
  if ($sob -ne $Frente) { "ABORTADO: em $X,$Y está '$sob', não $Frente"; exit 2 }
  [CliBrabo]::SetCursorPos($X, $Y) | Out-Null; Start-Sleep -Milliseconds 150
  $n = if ($Duplo) { 2 } else { 1 }
  for ($i = 0; $i -lt $n; $i++) { [CliBrabo]::mouse_event(2, 0, 0, 0, [IntPtr]::Zero); [CliBrabo]::mouse_event(4, 0, 0, 0, [IntPtr]::Zero); Start-Sleep -Milliseconds 90 }
  "clique em $X,$Y" + $(if ($Duplo) { " (duplo)" } else { "" })
}
if ($Teclas) { Start-Sleep -Milliseconds 200; [System.Windows.Forms.SendKeys]::SendWait($Teclas); "teclas $Teclas" }
