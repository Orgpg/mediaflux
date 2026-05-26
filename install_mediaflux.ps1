param(
  [string]$Repo = "OWNER/REPO",
  [string]$AssetFilter = "windows"
)

# Fetch latest release metadata
$headers = @{ 'User-Agent' = 'MediaFlux-Installer' }
$release = Invoke-RestMethod -Uri "https://api.github.com/repos/$Repo/releases/latest" -Headers $headers

# Find asset by filter in name
$asset = $release.assets | Where-Object { $_.name -like "*$AssetFilter*" } | Select-Object -First 1
if (-not $asset) {
  Write-Error "No release asset found matching filter '$AssetFilter' in release $($release.tag_name)"
  exit 1
}

$downloadUrl = $asset.browser_download_url
$dest = Join-Path $PSScriptRoot $asset.name

Write-Host "Downloading $($asset.name) from $($release.tag_name)..."
Invoke-WebRequest -Uri $downloadUrl -OutFile $dest -Headers $headers
Write-Host "Saved to: $dest"

# If it's an exe, offer to run
if ($dest -like "*.exe") {
  Write-Host "Starting executable..."
  Start-Process -FilePath $dest
} else {
  Write-Host "Downloaded file is not an .exe. Please extract/run as needed."
}

Write-Host "Done."

# Usage: .\install_mediaflux.ps1 -Repo "youruser/yourrepo" -AssetFilter "windows"
