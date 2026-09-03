$ErrorActionPreference = 'Stop'
$Root = Split-Path $PSScriptRoot -Parent
$ExampleRoot = Join-Path $Root 'example'
$OutDir = Join-Path $Root 'dist\example'
$ZipPath = Join-Path $Root 'dist\example.zip'

Write-Host '=== Packaging example profiles ===' -ForegroundColor Cyan

if (Test-Path $OutDir) { Remove-Item -Recurse -Force $OutDir }
New-Item -ItemType Directory -Force -Path $OutDir | Out-Null

Copy-Item -Recurse -Force (Join-Path $ExampleRoot 'custom-start') (Join-Path $OutDir 'custom-start')

$readme = Join-Path $ExampleRoot 'README.md'
if (Test-Path $readme) { Copy-Item -Force $readme (Join-Path $OutDir 'README.md') }

if (Test-Path $ZipPath) { Remove-Item -Force $ZipPath }
Compress-Archive -Path (Join-Path $OutDir '*') -DestinationPath $ZipPath -Force

Write-Host "  -> dist\example\" -ForegroundColor DarkGreen
Write-Host "  -> dist\example.zip" -ForegroundColor DarkGreen
Write-Host 'Done.' -ForegroundColor Green
