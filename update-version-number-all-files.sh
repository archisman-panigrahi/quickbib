#!/usr/bin/env bash
# update-version-number-all-files.sh
# Enhanced updater:
# - Infers current version (from meson.build / quickbib/app_info.py / snapcraft.yaml)
# - Performs a dry-run by default
# - Replaces exact occurrences of the old version with the new version across the repo
# - Skips `debian/changelog` historical entries by default; can prepend a new changelog entry
# - Optional: git commit, tag, and push

set -euo pipefail

SCRIPT_NAME=$(basename "$0")

usage() {
    cat <<EOF
Usage: $SCRIPT_NAME [options] <new-version>

Options:
  -n, --dry-run          Show what would be changed (default)
  -f, --force            Apply changes (not dry-run)
  -o, --old <version>    Specify the old version to replace (inferred if omitted)
  -c, --changelog "msg"  Add a new debian/changelog entry with this message
      --no-changelog     Don't touch debian/changelog (default)
      --commit           Create a git commit for the changes
      --tag              Create an annotated git tag named v<new-version>
      --push             Push commit and tag to origin (only if --commit used)
  -h, --help             Show this help and exit

Examples:
  $SCRIPT_NAME -n 0.3.3               # dry-run, infer old version
  $SCRIPT_NAME -f --commit --tag 0.3.3 # perform changes, commit and tag
  $SCRIPT_NAME -f -o 0.3.2 -c "Release notes" 0.3.3
EOF
}

# Defaults
DRY_RUN=1
FORCE=0
OLD_VERSION=""
NEW_VERSION=""
CHANGELOG_MSG=""
DO_CHANGELOG=0
GIT_COMMIT=0
GIT_TAG=0
GIT_PUSH=0

if [ $# -eq 0 ]; then
    usage
    exit 1
fi

# Parse args (simple)
while [ $# -gt 0 ]; do
    case "$1" in
        -n|--dry-run)
            DRY_RUN=1; shift ;;
        -f|--force)
            DRY_RUN=0; FORCE=1; shift ;;
        -o|--old)
            OLD_VERSION="$2"; shift 2 ;;
        -c|--changelog)
            CHANGELOG_MSG="$2"; DO_CHANGELOG=1; shift 2 ;;
        --no-changelog)
            DO_CHANGELOG=0; shift ;;
        --commit)
            GIT_COMMIT=1; shift ;;
        --tag)
            GIT_TAG=1; shift ;;
        --push)
            GIT_PUSH=1; shift ;;
        -h|--help)
            usage; exit 0 ;;
        --)
            shift; break ;;
        -* )
            echo "Unknown option: $1"; usage; exit 1 ;;
        * )
            if [ -z "$NEW_VERSION" ]; then
                NEW_VERSION="$1"
                shift
            else
                echo "Unexpected argument: $1"; usage; exit 1
            fi
            ;;
    esac
done

if [ -z "$NEW_VERSION" ]; then
    echo "Error: new version is required."
    usage
    exit 1
fi

AUTHOR_NAME="Archisman Panigrahi"
AUTHOR_EMAIL="apandada1@gmail.com"
DATE_RFC2822=$(date -R)
DATE_ISO=$(date +%Y-%m-%d)

echo "New version: $NEW_VERSION"
if [ $DRY_RUN -eq 1 ]; then
    echo "Mode: dry-run (no files will be modified). Use -f/--force to apply changes."
fi

escape_for_sed() {
    printf '%s' "$1" | sed -e 's/[\/&]/\\&/g'
}

infer_old_version() {
    # Try meson.build project(...) line first
    if [ -f meson.build ]; then
        v=$(sed -n "s/.*version[[:space:]]*:[[:space:]]*['\"]\([^'\"]*\)['\"].*/\1/p" meson.build | head -n1 || true)
        if [ -n "$v" ]; then
            printf '%s' "$v"
            return 0
        fi
    fi
    # Try quickbib/app_info.py
    if [ -f quickbib/app_info.py ]; then
        v=$(sed -n "s/.*APP_VERSION[[:space:]]*=[[:space:]]*['\"]\([^'\"]*\)['\"].*/\1/p" quickbib/app_info.py | head -n1 || true)
        if [ -n "$v" ]; then
            printf '%s' "$v"
            return 0
        fi
    fi
    # Try snapcraft.yaml version: 'x'
    if [ -f snap/snapcraft.yaml ]; then
        v=$(sed -n "s/^version:[[:space:]]*['\"]\([^'\"]*\)['\"].*/\1/p" snap/snapcraft.yaml | head -n1 || true)
        if [ -n "$v" ]; then
            printf '%s' "$v"
            return 0
        fi
    fi
    return 1
}

if [ -z "$OLD_VERSION" ]; then
    if oldv=$(infer_old_version); then
        OLD_VERSION=$oldv
        echo "Inferred old version: $OLD_VERSION"
    else
        echo "Could not infer old version. Use -o/--old to specify it explicitly." >&2
        exit 1
    fi
else
    echo "Using provided old version: $OLD_VERSION"
fi

if [ "$OLD_VERSION" = "$NEW_VERSION" ]; then
    echo "Old and new version are the same ($OLD_VERSION). Nothing to do."; exit 0
fi

# Find files containing the exact old version string
# Exclude .git directory, this script file, and flatpak json files from search results
# (flatpak JSON may contain embedded hashes/URLs which we don't want to mangle).
mapfile -t FILES_WITH_OLD < <(grep -R --line-number --binary-files=without-match -I --exclude-dir=.git --exclude-dir=flatpak --exclude="$(basename "$0")" "${OLD_VERSION}" . | cut -d: -f1 | sort -u)

# By default, do not replace occurrences in debian/changelog (historical)
FILTERED_FILES=()
# Files we should never mass-replace the version in because they contain historical
# release entries or are handled separately: debian/changelog and the metainfo xml.
METAFILE=io.github.archisman_panigrahi.QuickBib.metainfo.xml
for f in "${FILES_WITH_OLD[@]}"; do
    case "$f" in
        ./debian/changelog|debian/changelog)
            # keep for optional changelog handling
            continue
            ;;
        ./$METAFILE|$METAFILE)
            # metainfo is updated by insertion logic below; do not mass-replace its version
            continue
            ;;
        *)
            FILTERED_FILES+=("$f")
            ;;
    esac
done

if [ ${#FILTERED_FILES[@]} -eq 0 ]; then
    echo "No files (excluding debian/changelog) contain '$OLD_VERSION'."
else
    echo "Files containing old version (to be updated):"
    for f in "${FILTERED_FILES[@]}"; do
        echo "  - $f"
    done
fi

if [ $DO_CHANGELOG -eq 1 ]; then
    echo "Will prepend debian/changelog with: $CHANGELOG_MSG"
fi

if [ $DRY_RUN -eq 1 ]; then
    echo
    echo "--- Dry-run preview ---"
    esc_old=$(escape_for_sed "$OLD_VERSION")
    esc_new=$(escape_for_sed "$NEW_VERSION")
    for f in "${FILTERED_FILES[@]}"; do
        echo
        echo "File: $f"
        echo "--- Matches (lines showing old -> new):"
        # show lines containing old version and show replacement
        grep -n --color=always -I "$OLD_VERSION" "$f" || true
        echo "--- Proposed replacement (first 5 occurrences):"
        sed -n "/$esc_old/ {=; p; q; }" "$f" 2>/dev/null || true
        # Show a tiny sed preview for the first few lines where it occurs
        grep -n -m5 -I "$OLD_VERSION" "$f" | sed -n '1,5p' || true
    done
    if [ $DO_CHANGELOG -eq 1 ]; then
        echo
        echo "debian/changelog would be prepended with a new entry:"
        printf "%s (%s-1) unstable; urgency=medium\n\n  * %s\n\n -- %s <%s>  %s\n\n" "$(awk 'NR==1{print $1; exit}' debian/changelog 2>/dev/null || echo quickbib)" "$NEW_VERSION" "$CHANGELOG_MSG" "$AUTHOR_NAME" "$AUTHOR_EMAIL" "$DATE_RFC2822"
    fi
    echo
    echo "Dry-run finished. Use -f/--force to apply the changes." 
    exit 0
fi

# At this point we will apply changes
echo "Applying changes..."

esc_old=$(escape_for_sed "$OLD_VERSION")
esc_new=$(escape_for_sed "$NEW_VERSION")

modified_files=()
for f in "${FILTERED_FILES[@]}"; do
    # Make an atomic replacement of the exact string
    if [ ! -f "$f" ]; then
        continue
    fi
    tmp=$(mktemp)
    # Use sed to replace all exact OLD_VERSION occurrences
    sed "s/${esc_old}/${esc_new}/g" "$f" > "$tmp"
    mv "$tmp" "$f"
    modified_files+=("$f")
    echo "Updated: $f"
done

# Handle debian/changelog: prepend entry if requested
if [ $DO_CHANGELOG -eq 1 ]; then
    DC=debian/changelog
    if [ -f "$DC" ]; then
        PACKAGE=$(awk 'NR==1{print $1; exit}' "$DC" || true)
        PACKAGE=${PACKAGE:-quickbib}
        DEB_VERSION="${NEW_VERSION}-1"
        tmp=$(mktemp)
        {
            printf "%s (%s) unstable; urgency=medium\n\n" "$PACKAGE" "$DEB_VERSION"
            printf "  * %s\n\n" "$CHANGELOG_MSG"
            printf " -- %s <%s>  %s\n\n" "$AUTHOR_NAME" "$AUTHOR_EMAIL" "$DATE_RFC2822"
            cat "$DC"
        } > "$tmp"
        mv "$tmp" "$DC"
        modified_files+=("$DC")
        echo "Prepended debian/changelog"
    else
        echo "debian/changelog not found; skipping changelog update"
    fi
    # Also add a release entry with description to the AppStream/metainfo XML if present
    METAFILE=io.github.archisman_panigrahi.QuickBib.metainfo.xml
    if [ -f "$METAFILE" ]; then
        tmp2=$(mktemp)
        # Insert a new <release> entry immediately after the opening <releases> tag
        awk -v ver="$NEW_VERSION" -v date="$DATE_ISO" -v msg="$CHANGELOG_MSG" -v repourl="https://github.com/archisman-panigrahi/QuickBib/releases/tag/v" '
        /^\s*<releases>/ {
            print
            print "    <release version=\"" ver "\" date=\"" date "\">"
            print "      <description>"
            print "        <p>" msg "</p>"
            print "      </description>"
            print "      <url type=\"details\">" repourl ver "</url>"
            print "    </release>"
            next
        }
        { print }
        ' "$METAFILE" > "$tmp2" && mv "$tmp2" "$METAFILE"
        modified_files+=("$METAFILE")
        echo "Updated metainfo: $METAFILE"
    else
        echo "Metainfo file $METAFILE not found; skipping metainfo update"
    fi
fi

echo
echo "Files modified:"
for f in "${modified_files[@]}"; do
    echo "  - $f"
done

if [ ${#modified_files[@]} -eq 0 ]; then
    echo "No files were modified. Exiting."
    exit 0
fi

if [ $GIT_COMMIT -eq 1 ]; then
    if ! command -v git >/dev/null 2>&1; then
        echo "git not found; cannot commit"; exit 1
    fi
    # Ensure we are in a git repo
    if ! git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
        echo "Not inside a git repository; cannot commit"; exit 1
    fi
    # Check clean working tree (allow our modified files)
    if [ -n "$(git status --porcelain | grep -v '^ M ' || true)" ]; then
        echo "Working tree has other changes. Please commit or stash them first."; exit 1
    fi
    git add "${modified_files[@]}"
    git commit -m "Bump version: ${OLD_VERSION} -> ${NEW_VERSION}"
    echo "Committed changes"
    if [ $GIT_TAG -eq 1 ]; then
        TAGNAME="v${NEW_VERSION}"
        git tag -a "$TAGNAME" -m "Release $TAGNAME"
        echo "Created tag $TAGNAME"
        if [ $GIT_PUSH -eq 1 ]; then
            git push origin HEAD
            git push origin "$TAGNAME"
            echo "Pushed commit and tag to origin"
        fi
    fi
fi

echo "All done. Updated version from $OLD_VERSION to $NEW_VERSION."