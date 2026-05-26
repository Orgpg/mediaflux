#!/usr/bin/env bash
# Simple installer: downloads the latest release asset matching a filter and runs it (if executable).
# Usage: ./install_mediaflux.sh OWNER/REPO linux

REPO="$1"
FILTER="$2"
if [ -z "$REPO" ]; then
  echo "Usage: $0 OWNER/REPO [filter]"
  exit 1
fi
if [ -z "$FILTER" ]; then
  FILTER=linux
fi

echo "Fetching latest release for $REPO..."
RELEASE_JSON=$(curl -s "https://api.github.com/repos/$REPO/releases/latest")
ASSET_URL=$(python - <<PY
import sys, json
r = json.load(sys.stdin)
assets = r.get('assets', [])
for a in assets:
    if '$FILTER' in a.get('name',''):
        print(a.get('browser_download_url'))
        sys.exit(0)
sys.exit(1)
PY
 <<< "$RELEASE_JSON")

if [ -z "$ASSET_URL" ]; then
  echo "No asset found matching filter '$FILTER'."
  exit 1
fi

FILENAME=$(basename "$ASSET_URL")

echo "Downloading $FILENAME..."
curl -L "$ASSET_URL" -o "$FILENAME"
chmod +x "$FILENAME" || true

if [[ "$FILENAME" == *.sh || -x "$FILENAME" ]]; then
  echo "Running $FILENAME"
  ./"$FILENAME"
else
  echo "Downloaded to $FILENAME. Run or extract as needed."
fi

exit 0
