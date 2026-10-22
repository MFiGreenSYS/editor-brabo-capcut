# janela_capcut.ps1 — achar a janela DE VERDADE de um programa (a maior janela visível dos processos dele).
# O CapCut troca o "MainWindowHandle" por pop-ups de dica (78×24, 109×21) e aí captura/clique/maximizar caem no lugar errado.
# Uso (dot-source): . "$PSScriptRoot\janela_capcut.ps1"; $h = JanelaGrande "CapCut"  → IntPtr (0 se não achar)
if (-not ("JanBrabo2" -as [type])) {
Add-Type @"
using System; using System.Collections.Generic; using System.Runtime.InteropServices;
public class JanBrabo2 {
  [StructLayout(LayoutKind.Sequential)] public struct RECT { public int L, T, R, B; }
  public delegate bool EnumProc(IntPtr h, IntPtr p);
  [DllImport("user32.dll")] public static extern bool EnumWindows(EnumProc f, IntPtr p);
  [DllImport("user32.dll")] public static extern bool IsWindowVisible(IntPtr h);
  [DllImport("user32.dll")] public static extern bool IsIconic(IntPtr h);
  [DllImport("user32.dll")] public static extern uint GetWindowThreadProcessId(IntPtr h, out uint pid);
  [DllImport("user32.dll")] public static extern bool GetWindowRect(IntPtr h, out RECT r);
  public static IntPtr Maior(uint[] pids) {
    IntPtr melhor = IntPtr.Zero; long area = 0; var ids = new HashSet<uint>(pids);
    EnumWindows((h, p) => {
      uint pid; GetWindowThreadProcessId(h, out pid);
      if (ids.Contains(pid) && IsWindowVisible(h) && !IsIconic(h)) {
        RECT r; GetWindowRect(h, out r); long a = (long)(r.R - r.L) * (r.B - r.T);
        if (a > area) { area = a; melhor = h; }
      }
      return true; }, IntPtr.Zero);
    return melhor;
  }
}
"@
}
function JanelaGrande([string]$nome) {
  $pids = @(Get-Process $nome -ErrorAction SilentlyContinue | ForEach-Object { [uint32]$_.Id })
  if (-not $pids) { return [IntPtr]::Zero }
  return [JanBrabo2]::Maior([uint32[]]$pids)
}
