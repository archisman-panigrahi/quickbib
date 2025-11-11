from pathlib import Path

# Application metadata
APP_NAME = "QuickBib"
APP_VERSION = "0.3.3"
HOMEPAGE = "https://archisman-panigrahi.github.io/QuickBib/"
REPO_URL = "https://github.com/archisman-panigrahi/QuickBib"
# LICENSE is located in the repository root (one level up from the package dir)
# Use resolve().parent.parent so this works when the package is imported from
# an installed location or run from source.
LICENSE_PATH = Path(__file__).resolve().parent.parent / "LICENSE"
