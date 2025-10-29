#!/usr/bin/env python3

import sys
from pathlib import Path
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QIcon

from .app_info import APP_NAME, APP_VERSION, HOMEPAGE, REPO_URL, LICENSE_PATH
from .main_window import QuickBibWindow


def main(argv):
    app = QApplication(argv)
    try:
        theme_icon = QIcon.fromTheme("io.github.archisman_panigrahi.quickbib")
        if not theme_icon.isNull():
            app.setWindowIcon(theme_icon)
        else:
            # assets are installed under share/quickbib/assets
            asset_path = Path(__file__).parent.parent / "assets" / "icon" / "64x64" / "io.github.archisman_panigrahi.quickbib.png"
            if asset_path.exists():
                app.setWindowIcon(QIcon(str(asset_path)))
    except Exception:
        pass
    win = QuickBibWindow()
    win.show()
    return app.exec()


if __name__ == "__main__":
    sys.exit(main(sys.argv))
