param(
    [ValidateSet('zh', 'en', 'all')]
    [string]$Language = 'all'
)

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

function Get-DistDllName([string]$dll, [string]$Lang, [string]$Version) {
    $base = [System.IO.Path]::GetFileNameWithoutExtension($dll)
    if ($Lang -eq 'en') { return "$base.en-$Version.dll" }
    return "$base-$Version.dll"
}

function Clear-OldDistDlls([string]$outDir, [string]$dll) {
    $base = [System.IO.Path]::GetFileNameWithoutExtension($dll)
    foreach ($pattern in @("$base-*.dll", "$base.en-*.dll", "$base.dll", "$base.en.dll")) {
        Get-ChildItem -Path $outDir -Filter $pattern -ErrorAction SilentlyContinue | Remove-Item -Force
    }
}

if (-not (Test-Path $Csproj)) { throw "Project not found: $Csproj" }

$version = Get-ProjectVersion $Csproj
$languages = if ($Language -eq 'all') { @('zh', 'en') } else { @($Language) }

Write-Host "=== Building Custom Start Framework (languages: $($languages -join ', ')) ===" -ForegroundColor Cyan

New-Item -ItemType Directory -Force -Path $OutDir | Out-Null
Clear-OldDistDlls $OutDir $Dll

foreach ($lang in $languages) {
    Write-Host "  [$lang] dotnet build $Csproj -c Release -p:ModLanguage=$lang"
    dotnet build $Csproj -c Release -p:ModLanguage=$lang --nologo -v q
    if ($LASTEXITCODE -ne 0) { throw "Build failed ($lang)" }

    $projDir = Split-Path $Csproj -Parent
    $srcDll = Join-Path $projDir "bin\Release\$Dll"
    if (-not (Test-Path $srcDll)) { throw "Output DLL not found: $srcDll" }

    $destName = Get-DistDllName $Dll $lang $version
    Copy-Item -Force $srcDll (Join-Path $OutDir $destName)
    Write-Host "    -> dist\release\$destName" -ForegroundColor DarkGreen
}

$changeLog = Join-Path (Split-Path $Csproj -Parent) 'change.log'
if (Test-Path $changeLog) {
    Copy-Item -Force $changeLog (Join-Path $OutDir 'change.log')
}

Write-Host "Done." -ForegroundColor Green
