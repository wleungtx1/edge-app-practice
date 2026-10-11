# Build the stand-in Windows installer: EdgeApp-practice-<version>.msi plus its .sha256.
# The "MSI" is a zip of app/, templates/ and requirements.txt renamed to .msi — the real repo
# builds a proper MSI here. Only the file name, location and checksum format matter for practice.
#
# Usage: pwsh installer/windows/build_msi.ps1 -Version 0.1.0 [-OutDir dist]
param(
    [Parameter(Mandatory = $true)][string]$Version,
    [string]$OutDir = "dist"
)
$ErrorActionPreference = "Stop"

$root = (Resolve-Path (Join-Path $PSScriptRoot "..\..")).Path
New-Item -ItemType Directory -Force -Path $OutDir | Out-Null
$name = "EdgeApp-practice-$Version.msi"
$out = Join-Path (Resolve-Path $OutDir).Path $name
$zip = [IO.Path]::ChangeExtension($out, ".zip")

$sources = @("app", "templates", "requirements.txt") | ForEach-Object { Join-Path $root $_ }
Compress-Archive -Path $sources -DestinationPath $zip -Force
Move-Item -Force -Path $zip -Destination $out

# Same "<hash>  <name>" format as sha256sum, LF-terminated, so `sha256sum -c` works on it.
$hash = (Get-FileHash -Algorithm SHA256 -Path $out).Hash.ToLower()
[IO.File]::WriteAllText("$out.sha256", "$hash  $name`n")

Write-Host "Built $out"
Get-Content "$out.sha256"
