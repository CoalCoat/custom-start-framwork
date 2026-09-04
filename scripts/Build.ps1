$ErrorActionPreference = 'Stop'
$Root = Split-Path $PSScriptRoot -Parent
$Csproj = Join-Path $Root 'framework\CustomStartFramework.csproj'
$OutDir = Join-Path $Root 'dist\release'
$Dll = 'CustomStartFramework.dll'

function Get-ProjectVersion([string]$csprojPath) {
    $content = Get-Content $csprojPath -Raw
    if ($content -match '<Version>([^<]+)</Version>') { return $Matches[1].Trim() }
    throw "Version not found in $csprojPath"
}

function Clear-OldDistDlls([string]$outDir, [string]$dll) {
    $base = [System.IO.Path]::GetFileNameWithoutExtension($dll)
    foreach ($pattern in @("$base-*.dll", "$base.en-*.dll", "$base.dll", "$base.en.dll")) {
        Get-ChildItem -Path $outDir -Filter $pattern -ErrorAction SilentlyContinue | Remove-Item -Force
    }
}

if (-not (Test-Path $Csproj)) { throw "Project not found: $Csproj" }

$version = Get-ProjectVersion $Csproj
$destName = "$([System.IO.Path]::GetFileNameWithoutExtension($Dll))-$version.dll"

Write-Host '=== Building Custom Start Framework ===' -ForegroundColor Cyan

New-Item -ItemType Directory -Force -Path $OutDir | Out-Null
Clear-OldDistDlls $OutDir $Dll

Write-Host "  dotnet build $Csproj -c Release"
dotnet build $Csproj -c Release --nologo -v q
if ($LASTEXITCODE -ne 0) { throw 'Build failed' }

$projDir = Split-Path $Csproj -Parent
$srcDll = Join-Path $projDir "bin\Release\$Dll"
if (-not (Test-Path $srcDll)) { throw "Output DLL not found: $srcDll" }

Copy-Item -Force $srcDll (Join-Path $OutDir $destName)
Write-Host "    -> dist\release\$destName" -ForegroundColor DarkGreen

$changeLog = Join-Path (Split-Path $Csproj -Parent) 'change.log'
if (Test-Path $changeLog) {
    Copy-Item -Force $changeLog (Join-Path $OutDir 'change.log')
}

Write-Host 'Done.' -ForegroundColor Green
