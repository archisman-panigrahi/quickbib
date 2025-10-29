#!/bin/bash
# Usage: ./update-version-number-all-files.sh <new_version> "<changelog message>"

set -euo pipefail


if [ $# -lt 2 ]; then
    echo "Usage: $0 <new_version> \"<changelog message>\""
    exit 1
fi

NEW_VERSION="$1"
CHANGELOG="$2"
AUTHOR_NAME="Archisman Panigrahi"
EMAIL="apandada1@gmail.com"
DATE_RFC2822=$(date -R)
DATE_ISO=$(date +%Y-%m-%d)

echo "Updating project files to version: $NEW_VERSION"

# Helper: replace a file atomically
atomic_write() {
    local dest="$1" tmp
    tmp=$(mktemp)
    cat > "$tmp"
    mv "$tmp" "$dest"
}

# 1) Update quickbib/app_info.py -> APP_VERSION = "x.y"
APP_INFO=quickbib/app_info.py
if [ -f "$APP_INFO" ]; then
    echo "- Updating $APP_INFO"
    awk -v v="$NEW_VERSION" '
    /^APP_VERSION[[:space:]]*=/ {
        printf "APP_VERSION = \"%s\"\n", v
        next
    }
    { print }
' "$APP_INFO" > "$APP_INFO.tmp" && mv "$APP_INFO.tmp" "$APP_INFO"
else
    echo "- Skipping $APP_INFO (not found)"
fi

# 2) Prepend debian/changelog with new entry
DEBIAN_CHANGELOG=debian/changelog
if [ -f "$DEBIAN_CHANGELOG" ]; then
    echo "- Updating $DEBIAN_CHANGELOG"
    PACKAGE=$(awk 'NR==1{print $1; exit}' "$DEBIAN_CHANGELOG" || true)
    PACKAGE=${PACKAGE:-quickbib}
    DEB_VERSION="${NEW_VERSION}-1"

    {
        printf "%s (%s) unstable; urgency=medium\n\n" "$PACKAGE" "$DEB_VERSION"
        printf "  * %s\n\n" "$CHANGELOG"
        printf " -- %s <%s>  %s\n\n" "$AUTHOR_NAME" "$EMAIL" "$DATE_RFC2822"
        cat "$DEBIAN_CHANGELOG"
    } > "$DEBIAN_CHANGELOG.tmp" && mv "$DEBIAN_CHANGELOG.tmp" "$DEBIAN_CHANGELOG"
else
    echo "- Skipping $DEBIAN_CHANGELOG (not found)"
fi

# 3) Update NSIS installer script version (windows_packaging/quickbib.nsi)
NSIS_FILE=windows_packaging/quickbib.nsi
if [ -f "$NSIS_FILE" ]; then
    echo "- Updating $NSIS_FILE"
    awk -v v="$NEW_VERSION" '
    /^!define[[:space:]]+VERSION[[:space:]]+/ {
        printf "!define VERSION \"%s\"\n", v
        next
    }
    { print }
' "$NSIS_FILE" > "$NSIS_FILE.tmp" && mv "$NSIS_FILE.tmp" "$NSIS_FILE"
else
    echo "- Skipping $NSIS_FILE (not found)"
fi

echo "All done. Version updated to $NEW_VERSION."