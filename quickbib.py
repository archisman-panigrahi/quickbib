#!/usr/bin/env python3

# Copyright (c) 2025 Archisman Panigrahi <apandada1ATgmail.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import sys
import sys
from pathlib import Path
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QIcon

from app_info import APP_NAME, APP_VERSION, HOMEPAGE, REPO_URL, LICENSE_PATH
from main_window import QuickBibWindow


def main(argv):
    app = QApplication(argv)
    # Try to set the application icon from the system theme (one attempt only).
    try:
        theme_icon = QIcon.fromTheme("io.github.archisman_panigrahi.quickbib")
        if not theme_icon.isNull():
            app.setWindowIcon(theme_icon)
        else:
            asset_path = Path(__file__).parent / "assets" / "icon" / "64x64" / "io.github.archisman_panigrahi.quickbib.png"
            if asset_path.exists():
                print("Falling back to bundled icon asset.")
                app.setWindowIcon(QIcon(str(asset_path)))
    except Exception:
        pass
    win = QuickBibWindow()
    win.show()
    return app.exec()


if __name__ == "__main__":
    import sys
    sys.exit(main(sys.argv))
