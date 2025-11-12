#!/usr/bin/env bash
set -euo pipefail

# macos_create_app.sh
# Create a minimal macOS .app bundle that runs the installed Python package `quickbib`.
# Usage: ./macos_create_app.sh [--python /path/to/python] [--icon /path/to/icon.png] [--name QuickBib] [--dest /path/to/Applications]
#
# Notes:
# - This script should be run on macOS (it uses `sips` and `iconutil`).
# - The created .app is unsigned. Gatekeeper will warn users unless they allow the app
#   explicitly (right-click -> Open) or the app is signed/notarized with an Apple Developer account.

APP_NAME="QuickBib"
BUNDLE_ID="io.github.archisman_panigrahi.QuickBib"
DEST_DIR="$HOME/Applications"
PYTHON_EXEC=""
ICON_SRC=""

print_usage(){
  cat <<USAGE
Usage: $0 [--python /path/to/python] [--icon /path/to/icon.png] [--name AppName] [--dest /path/to/Applications]

This creates AppName.app in ~/Applications (or --dest) which runs: python -m quickbib
It will try to make an .icns from the provided icon PNG using sips/iconutil (macOS tools).
If not run on macOS the script will exit.
USAGE
}

while [[ ${1-} != "" ]]; do
  case "$1" in
    --python) PYTHON_EXEC="$2"; shift 2;;
    --icon) ICON_SRC="$2"; shift 2;;
    --name) APP_NAME="$2"; shift 2;;
    --dest) DEST_DIR="$2"; shift 2;;
    -h|--help) print_usage; exit 0;;
    *) echo "Unknown arg: $1"; print_usage; exit 1;;
  esac
done

# Ensure macOS
if [[ "$(uname -s)" != "Darwin" ]]; then
  echo "This script must be run on macOS (Darwin). Exiting." >&2
  exit 2
fi

# Find Python if not provided
if [[ -z "$PYTHON_EXEC" ]]; then
  if command -v python3 >/dev/null 2>&1; then
    PYTHON_EXEC="$(command -v python3)"
  elif command -v python >/dev/null 2>&1; then
    PYTHON_EXEC="$(command -v python)"
  else
    echo "No python3/python found on PATH. Please install Python or pass --python." >&2
    exit 3
  fi
fi

# Verify the quickbib module is importable with that python
if ! "$PYTHON_EXEC" -c "import importlib, sys; importlib.import_module('quickbib')" >/dev/null 2>&1; then
  echo "The Python executable '$PYTHON_EXEC' cannot import 'quickbib'. Ensure the package is installed in that interpreter." >&2
  exit 4
fi

# Try to locate a default icon inside the installed package if none provided
if [[ -z "$ICON_SRC" ]]; then
  ICON_SRC="$($PYTHON_EXEC - <<PY
import quickbib, os
base=os.path.join(os.path.dirname(quickbib.__file__), 'assets', 'icon')
candidates=[
  os.path.join(base,'128x128','io.github.archisman_panigrahi.QuickBib.png'),
  os.path.join(base,'64x64','io.github.archisman_panigrahi.QuickBib.png'),
  os.path.join(base,'scalable','io.github.archisman_panigrahi.QuickBib.svg'),
  os.path.join(base,'32x32','io.github.archisman_panigrahi.QuickBib.png')
]
for p in candidates:
    if os.path.exists(p):
        print(p); break
print('')
PY
)"
  ICON_SRC="${ICON_SRC//[$'\t\n\r']}"
fi

if [[ -n "$ICON_SRC" && ! -f "$ICON_SRC" ]]; then
  echo "Found icon path '$ICON_SRC' is not a file. Ignoring." >&2
  ICON_SRC=""
fi

APP_BUNDLE_PATH="$DEST_DIR/$APP_NAME.app"

echo "Creating $APP_NAME.app -> $APP_BUNDLE_PATH"

rm -rf "$APP_BUNDLE_PATH"
mkdir -p "$APP_BUNDLE_PATH/Contents/MacOS"
mkdir -p "$APP_BUNDLE_PATH/Contents/Resources"

# Create the executable stub that launches the module
EXECUTABLE_PATH="$APP_BUNDLE_PATH/Contents/MacOS/$APP_NAME"
cat > "$EXECUTABLE_PATH" <<SH
#!/usr/bin/env bash
# Exec the selected Python interpreter and run the quickbib module
exec "$PYTHON_EXEC" -m quickbib "\$@"
SH
chmod +x "$EXECUTABLE_PATH"

# Create Info.plist
INFO_PLIST="$APP_BUNDLE_PATH/Contents/Info.plist"
cat > "$INFO_PLIST" <<PLIST
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>CFBundleName</key>
  <string>$APP_NAME</string>
  <key>CFBundleDisplayName</key>
  <string>$APP_NAME</string>
  <key>CFBundleIdentifier</key>
  <string>$BUNDLE_ID</string>
  <key>CFBundleExecutable</key>
  <string>$APP_NAME</string>
  <key>CFBundleIconFile</key>
  <string>Icon</string>
  <key>CFBundlePackageType</key>
  <string>APPL</string>
  <key>LSMinimumSystemVersion</key>
  <string>10.10</string>
</dict>
</plist>
PLIST

# Create .icns from provided PNG (if available)
if [[ -n "$ICON_SRC" ]]; then
  if ! command -v iconutil >/dev/null 2>&1; then
    echo "iconutil not found. Skipping icon creation. You can provide a prebuilt .icns with --icon /path/to/Icon.icns" >&2
  else
    ICONSET_DIR="$(mktemp -d)/${APP_NAME}.iconset"
    mkdir -p "$ICONSET_DIR"

    # Sizes to generate: 16,32,128,256,512 and the @2x variants
    sizes=(16 32 128 256 512)
    for s in "${sizes[@]}"; do
      out="$ICONSET_DIR/icon_${s}x${s}.png"
      sips -z $s $s "$ICON_SRC" --out "$out" >/dev/null
      # @2x
      out2="$ICONSET_DIR/icon_${s}x${s}@2x.png"
      sips -z $((s*2)) $((s*2)) "$ICON_SRC" --out "$out2" >/dev/null
    done

    ICON_ICNS="$APP_BUNDLE_PATH/Contents/Resources/Icon.icns"
    iconutil -c icns "$ICONSET_DIR" -o "$ICON_ICNS" >/dev/null
    rm -rf "$ICONSET_DIR"
    echo "Created Icon.icns in app bundle."
  fi
else
  echo "No icon provided or found in package. App will have default icon." >&2
fi

# Ensure Finder / LaunchServices sees the new app
if [[ -x "/System/Library/Frameworks/CoreServices.framework/Frameworks/LaunchServices.framework/Support/lsregister" ]]; then
  /System/Library/Frameworks/CoreServices.framework/Frameworks/LaunchServices.framework/Support/lsregister -f "$APP_BUNDLE_PATH" >/dev/null 2>&1 || true
fi

echo "Created $APP_BUNDLE_PATH"
echo "You can move it to /Applications if desired. Open it once (right-click -> Open) to satisfy Gatekeeper if macOS blocks it (unsigned)."
echo "Note: To avoid Gatekeeper warnings you must sign and notarize the app with an Apple Developer account (paid)."

exit 0
