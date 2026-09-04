param(
    [switch]$SkipBuild
)

$ErrorActionPreference = 'Stop'
$Root = Split-Path $PSScriptRoot -Parent
$Csproj = Join-Path $Root 'framework\CustomStartFramework.csproj'
$FrameworkRoot = Join-Path $Root 'framework'
$OutDir = Join-Path $Root 'dist\release'
$EditorDir = Join-Path $OutDir 'editor'
$ZipPath = Join-Path $Root 'dist\custom-start-framework.zip'

function Get-ProjectVersion([string]$csprojPath) {
    $content = Get-Content $csprojPath -Raw
    if ($content -match '<Version>([^<]+)</Version>') { return $Matches[1].Trim() }
    throw "Version not found in $csprojPath"
}

if (-not (Test-Path $Csproj)) { throw "Project not found: $Csproj" }

$version = Get-ProjectVersion $Csproj
$dllName = "CustomStartFramework-$version.dll"

Write-Host '=== Packaging Custom Start Framework ===' -ForegroundColor Cyan

if (-not $SkipBuild) {
    & (Join-Path $PSScriptRoot 'Build.ps1')
} elseif (-not (Test-Path (Join-Path $OutDir $dllName))) {
    throw "Built DLL not found: $(Join-Path $OutDir $dllName)"
}

$keepDlls = @{ $dllName = $true }

if (Test-Path $OutDir) {
    Get-ChildItem $OutDir -File -Filter '*.dll' | Where-Object { -not $keepDlls.ContainsKey($_.Name) } | Remove-Item -Force
} else {
    New-Item -ItemType Directory -Force -Path $OutDir | Out-Null
}
New-Item -ItemType Directory -Force -Path $EditorDir | Out-Null

$readmeSrc = Join-Path $FrameworkRoot 'README.md'
if (Test-Path $readmeSrc) { Copy-Item -Force $readmeSrc (Join-Path $OutDir 'README.md') }
$guideInRelease = Join-Path $OutDir 'GUIDE.md'
if (Test-Path $guideInRelease) { Remove-Item -Force $guideInRelease }

$changeLogSrc = Join-Path $FrameworkRoot 'change.log'
if (Test-Path $changeLogSrc) { Copy-Item -Force $changeLogSrc (Join-Path $OutDir 'change.log') }

$editorSrc = Join-Path $FrameworkRoot 'editor'
if (Test-Path $editorSrc) { Copy-Item -Force (Join-Path $editorSrc '*') $EditorDir }
@(
    '@echo off',
    'cd /d "%~dp0"',
    '',
    'set "PY="',
    'where python >nul 2>&1 && set "PY=python"',
    'if not defined PY where py >nul 2>&1 && set "PY=py -3"',
    'if not defined PY (',
    '  echo [Error] Python 3 not found. Install from https://www.python.org/downloads/',
    '  echo         and enable "Add python.exe to PATH" during setup.',
    '  pause',
    '  exit /b 1',
    ')',
    '',
    '%PY% edit_profiles.py %*',
    'set "RC=%ERRORLEVEL%"',
    'if not "%RC%"=="0" (',
    '  echo.',
    '  echo Editor exited with error %RC%.',
    '  pause',
    ')'
) | Set-Content -Path (Join-Path $EditorDir 'run_editor.bat') -Encoding ASCII

if (Test-Path $ZipPath) { Remove-Item -Force $ZipPath }
Compress-Archive -Path (Join-Path $OutDir '*') -DestinationPath $ZipPath -Force

Write-Host "  -> dist\release\" -ForegroundColor DarkGreen
Write-Host "  -> dist\custom-start-framework.zip" -ForegroundColor DarkGreen
Write-Host 'Done.' -ForegroundColor Green
