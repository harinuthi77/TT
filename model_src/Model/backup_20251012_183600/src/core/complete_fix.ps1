$script = @'
# complete_fix.ps1
# Fix all remaining issues

$ErrorActionPreference = 'Stop'

Write-Host "Applying complete fixes..." -ForegroundColor Cyan
Write-Host ""

# 1) vision.py: ensure js_code uses raw triple-quoted strings (js_code = r"""...""")
Write-Host "1) Normalizing JavaScript strings in src\core\vision.py..." -ForegroundColor Yellow
if (Test-Path "src\core\vision.py") {
    $v = Get-Content "src\core\vision.py" -Raw
    $v = [regex]::Replace($v, 'js_code\s*=\s*r?"""', 'js_code = r"""')
    Set-Content "src\core\vision.py" -Value $v -NoNewline -Encoding UTF8
    Write-Host "   OK: vision.py updated" -ForegroundColor Green
} else {
    Write-Host "   WARN: src\core\vision.py not found" -ForegroundColor DarkYellow
}

# 2) single_task_agent.py: rename AutonomousAgent/Agent -> SingleTaskAgent
Write-Host ""
Write-Host "2) Ensuring class name in src\agents\single_task_agent.py..." -ForegroundColor Yellow
if (Test-Path "src\agents\single_task_agent.py") {
    $s = Get-Content "src\agents\single_task_agent.py" -Raw
    $orig = $s
    $s = [regex]::Replace($s, 'class\s+AutonomousAgent\s*:', 'class SingleTaskAgent:')
    $s = [regex]::Replace($s, 'class\s+Agent\s*:', 'class SingleTaskAgent:')
    if ($s -ne $orig) {
        Set-Content "src\agents\single_task_agent.py" -Value $s -NoNewline -Encoding UTF8
        Write-Host "   OK: SingleTaskAgent class name fixed" -ForegroundColor Green
    } else {
        Write-Host "   OK: No rename needed" -ForegroundColor Green
    }
} else {
    Write-Host "   WARN: src\agents\single_task_agent.py not found" -ForegroundColor DarkYellow
}

# 3) continuous_agent.py: verify/normalize class name -> ContinuousAgent
Write-Host ""
Write-Host "3) Verifying class name in src\agents\continuous_agent.py..." -ForegroundColor Yellow
if (Test-Path "src\agents\continuous_agent.py") {
    $c = Get-Content "src\agents\continuous_agent.py" -Raw
    if ($c -match 'class\s+[A-Za-z_][A-Za-z0-9_]*Agent\s*:') {
        $c = [regex]::Replace($c, 'class\s+[A-Za-z_][A-Za-z0-9_]*Agent\s*:', 'class ContinuousAgent:')
        Set-Content "src\agents\continuous_agent.py" -Value $c -NoNewline -Encoding UTF8
        Write-Host "   OK: Ensured ContinuousAgent class name" -ForegroundColor Green
    } else {
        Write-Host "   OK: No class definition adjustment needed" -ForegroundColor Green
    }
} else {
    Write-Host "   WARN: src\agents\continuous_agent.py not found" -ForegroundColor DarkYellow
}

# 4) guided_agent.py: verify/normalize class name -> GuidedAgent
Write-Host ""
Write-Host "4) Verifying class name in src\agents\guided_agent.py..." -ForegroundColor Yellow
if (Test-Path "src\agents\guided_agent.py") {
    $g = Get-Content "src\agents\guided_agent.py" -Raw
    if ($g -match 'class\s+[A-Za-z_][A-Za-z0-9_]*Agent\s*:') {
        $g = [regex]::Replace($g, 'class\s+[A-Za-z_][A-Za-z0-9_]*Agent\s*:', 'class GuidedAgent:')
        Set-Content "src\agents\guided_agent.py" -Value $g -NoNewline -Encoding UTF8
        Write-Host "   OK: Ensured GuidedAgent class name" -ForegroundColor Green
    } else {
        Write-Host "   OK: No class definition adjustment needed" -ForegroundColor Green
    }
} else {
    Write-Host "   WARN: src\agents\guided_agent.py not found" -ForegroundColor DarkYellow
}

# 5) Ensure __init__.py so Python treats these as packages
Write-Host ""
Write-Host "5) Ensuring package __init__.py files..." -ForegroundColor Yellow
$dirs = @('src','src\core','src\agents','src\learning')
foreach ($d in $dirs) {
    if (-not (Test-Path $d)) { continue }
    $initPath = Join-Path $d '__init__.py'
    if (-not (Test-Path $initPath)) {
        New-Item -ItemType File -Path $initPath | Out-Null
        Write-Host "   OK: created $initPath" -ForegroundColor Green
    } else {
        Write-Host "   OK: exists $initPath" -ForegroundColor Green
    }
}

# 6) Sanity scan for lingering bare imports
Write-Host ""
Write-Host "6) Scanning for lingering 'from memory import' / 'from vision import'..." -ForegroundColor Yellow
$hits = Select-String -Path 'src\**\*.py' -Pattern 'from memory import|from vision import' -ErrorAction SilentlyContinue
if ($hits) {
    Write-Host "   WARNING: Found potential issues:" -ForegroundColor Red
    $hits | ForEach-Object { Write-Host ("    " + $_.Path + " : " + $_.Line.Trim()) -ForegroundColor Red }
} else {
    Write-Host "   OK: No lingering bare imports detected" -ForegroundColor Green
}

Write-Host ""
Write-Host ("=" * 62) -ForegroundColor Cyan
Write-Host "All fixes applied!" -ForegroundColor Green
Write-Host ("=" * 62) -ForegroundColor Cyan
Write-Host ""
Write-Host "Now test with: python .\main.py" -ForegroundColor Cyan
Write-Host ""
'@

Set-Content -Path .\complete_fix.ps1 -Value $script -Encoding UTF8
