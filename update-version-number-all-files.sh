#!/bin/bash
# Usage: ./update-version-number-all-files.sh <new_version>
# <changelog message>

set -e

if [ $# -lt 2 ]; then
    echo "Usage: $0 <new_version>"
    echo "\"<changelog message>\""
    exit 1
fi

NEW_VERSION="$1"
CHANGELOG="$2"
EMAIL="apandada1@gmail.com"
DATE_RFC2822=$(date -R)
DATE_ISO=$(date +%Y-%m-%d)

echo "Updating version to $NEW_VERSION with changelog: $CHANGELOG"

# 1. Update meson.build
if [ -f meson.build ]; then
    sed -i "s/project('quickbib', 'c', version : '[^']*')/project('quickbib', 'c', version : '$NEW_VERSION')/" meson.build
    echo "Updated meson.build"
fi

# 2. Update quickbib/app_info.py
if [ -f quickbib/app_info.py ]; then
    sed -i "s/APP_VERSION = \"[^\"]*\"/APP_VERSION = \"$NEW_VERSION\"/" quickbib/app_info.py
    echo "Updated quickbib/app_info.py"
fi

# 3. Update snap/snapcraft.yaml
if [ -f snap/snapcraft.yaml ]; then
    sed -i "s/^version: '[^']*'/version: '$NEW_VERSION'/" snap/snapcraft.yaml
    echo "Updated snap/snapcraft.yaml"
fi

# 4. Update quickbib.spec (spec file version)
if [ -f quickbib.spec ]; then
    # Look for __version__ = "..." in the spec file
    sed -i "s/__version__ = \"[^\"]*\"/__version__ = \"$NEW_VERSION\"/" quickbib.spec 2>/dev/null || true
    echo "Updated quickbib.spec"
fi

# 5. Update windows_packaging/quickbib.nsi
if [ -f windows_packaging/quickbib.nsi ]; then
    sed -i "s/!define VERSION \"[^\"]*\"/!define VERSION \"$NEW_VERSION\"/" windows_packaging/quickbib.nsi
    echo "Updated windows_packaging/quickbib.nsi"
fi

# 6. Update debian/changelog - prepend new entry
if [ -f debian/changelog ]; then
    PACKAGE=$(head -1 debian/changelog | awk '{print $1}')
    {
        echo "$PACKAGE ($NEW_VERSION) unstable; urgency=medium"
        echo ""
        echo "  * $CHANGELOG"
        echo ""
        echo " -- Archisman Panigrahi <$EMAIL>  $DATE_RFC2822"
        echo ""
        cat debian/changelog
    } > debian/changelog.new && mv debian/changelog.new debian/changelog
    echo "Updated debian/changelog"
fi

# 6. Update io.github.archisman_panigrahi.QuickBib.metainfo.xml
METAINFO="io.github.archisman_panigrahi.QuickBib.metainfo.xml"
if [ -f "$METAINFO" ]; then
    RELEASE_ENTRY="    <release version=\"$NEW_VERSION\" date=\"$DATE_ISO\">
      <description>
        <p>$CHANGELOG</p>
      </description>
      <url type=\"details\">https://github.com/archisman-panigrahi/QuickBib/releases/tag/v$NEW_VERSION</url>
    </release>"
    # Insert after <releases>
    awk -v entry="$RELEASE_ENTRY" '
        /<releases>/ && !x {print; print entry; x=1; next} 1
    ' "$METAINFO" > "$METAINFO.tmp" && mv "$METAINFO.tmp" "$METAINFO"
    echo "Updated $METAINFO"
fi

echo "All done. Version updated to $NEW_VERSION."