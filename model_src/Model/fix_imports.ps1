$ErrorActionPreference = 'Stop'

Write-Host "🛠 Fixing imports..." -ForegroundColor Cyan

function Fix-File {
  param(
    [Parameter(Mandatory=$true)][string]$Path,
    [Parameter(Mandatory=$true)][hashtable]$Replacements
  )
  if (-not (Test-Path $Path)) {
    Write-Host "Skip (missing): $Path" -ForegroundColor DarkYellow
    return
  }
  $text = Get-Content $Path -Raw
  foreach ($k in $Replacements.Keys) {
    $text = $text -replace $k, $Replacements[$k]
  }
  Set-Content -Path $Path -Value $text -NoNewline -Encoding UTF8
  Write-Host "Fixed: $Path" -ForegroundColor Yellow
}

# Ensure packages
foreach ($d in @('src','src\core','src\agents','src\learning')) {
  if (-not (Test-Path "$d\__init__.py")) { New-Item -ItemType File -Path "$d\__init__.py" | Out-Null }
}

# Core files (relative imports)
Fix-File -Path 'src\core\vision.py' -Replacements @{
  'from memory import' = 'from .memory import'
}
Fix-File -Path 'src\core\cognition.py' -Replacements @{
  'from memory import' = 'from .memory import'
  'from vision import' = 'from .vision import'
}
Fix-File -Path 'src\core\executor.py' -Replacements @{
  'from memory import' = 'from .memory import'
}

# Learning files (absolute to src.core)
Fix-File -Path 'src\learning\adaptive_engine.py' -Replacements @{
  'from memory import' = 'from src.core.memory import'
  'from vision import' = 'from src.core.vision import'
}
Fix-File -Path 'src\learning\adaptive_learning.py' -Replacements @{
  'from memory import' = 'from src.core.memory import'
}

Write-Host ""
Write-Host "✅ All imports fixed!" -ForegroundColor Green
Write-Host "Now run: python .\main.py" -ForegroundColor Cyan
