param(
    [string]$Root = "",
    [ValidateSet('zh', 'en', 'auto')]
    [string]$Language = 'auto'
)

$ErrorActionPreference = 'Stop'
$RepoRoot = Split-Path $PSScriptRoot -Parent
$Editor = Join-Path $RepoRoot 'framework\editor\edit_profiles.py'

if (-not (Test-Path $Editor)) {
    throw "Editor not found: $Editor"
}

if (-not $Root) {
    $candidates = @(
        (Join-Path $RepoRoot 'example\custom-start'),
        (Join-Path $RepoRoot 'dist\example\custom-start')
    )
    foreach ($c in $candidates) {
        if (Test-Path $c) { $Root = $c; break }
    }
    if (-not $Root) {
        $Root = Join-Path $RepoRoot 'example\custom-start'
    }
}

Write-Host "Editor: $Editor" -ForegroundColor Cyan
Write-Host "Root:   $Root" -ForegroundColor Cyan
if ($Language -eq 'auto') {
    python $Editor -r $Root
} else {
    python $Editor -r $Root --lang $Language
}
