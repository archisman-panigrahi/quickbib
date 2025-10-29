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

from pathlib import Path
from PyQt6.QtWidgets import (
    QDialog,
    QTabWidget,
    QTextBrowser,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QFrame,
)
from PyQt6.QtGui import QPixmap, QFont, QIcon
from PyQt6.QtCore import Qt

from app_info import APP_NAME, APP_VERSION, HOMEPAGE, REPO_URL, LICENSE_PATH


class AboutDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("About QuickBib")
        self.resize(600, 360)

        # Main layout
        vbox = QVBoxLayout()
        vbox.setContentsMargins(12, 12, 12, 12)
        vbox.setSpacing(12)
        self.setLayout(vbox)

        # Header: icon + title
        header = QHBoxLayout()
        header.setSpacing(12)
        vbox.addLayout(header)

        icon_label = QLabel()
        # Try system/theme icon; if not found, fallback to bundled asset.
        try:
            theme_icon = QIcon.fromTheme("io.github.archisman_panigrahi.quickbib")
            if not theme_icon.isNull():
                pix = theme_icon.pixmap(64, 64)
            else:
                asset_path = Path(__file__).parent / "assets" / "icon" / "64x64" / "io.github.archisman_panigrahi.quickbib.png"
                if asset_path.exists():
                    pix = QPixmap(str(asset_path))
                    if pix.isNull():
                        pix = QPixmap()
                else:
                    pix = QPixmap()
        except Exception:
            pix = QPixmap()
        icon_label.setPixmap(pix)
        header.addWidget(icon_label)

        title_layout = QVBoxLayout()
        title_label = QLabel(f"{APP_NAME}")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_layout.addWidget(title_label)

        subtitle = QLabel(f"Version {APP_VERSION}")
        subtitle.setStyleSheet("color: #666;")
        title_layout.addWidget(subtitle)

        header.addLayout(title_layout)

        # Tabs frame (gives a boxed area similar to the screenshot)
        frame = QFrame()
        frame.setFrameShape(QFrame.Shape.StyledPanel)
        frame.setObjectName("aboutFrame")
        frame_layout = QVBoxLayout()
        frame_layout.setContentsMargins(8, 8, 8, 8)
        frame.setLayout(frame_layout)
        vbox.addWidget(frame)

        tabs = QTabWidget()
        frame_layout.addWidget(tabs)

        # About tab
        about_text = QTextBrowser()
        about_html = f"""
        <p>{APP_NAME} fetches BibTeX entries from DOIs, arXiv IDs, and known journal URLs.
        It is a small utility to quickly convert identifiers into usable BibTeX records.</p>
        <p> Quickbib uses <a href="https://github.com/archisman-panigrahi/doi2bib3">doi2bib3</a>
        as its backend for DOI to BibTeX conversion.</p>
        <p>
          <b>Homepage:</b> <a href="{HOMEPAGE}">{HOMEPAGE}</a>
        </p>
        <p><b>License:</b> Released under GNU General Public License Version 3. See the <i>License</i> tab for details.</p>
        """
        about_text.setHtml(about_html)
        about_text.setOpenExternalLinks(True)
        tabs.addTab(about_text, "About")

        # Authors tab
        authors_text = QTextBrowser()
        authors_html = """
        <h3>Authors & Contributors</h3>
        <ul>
          <li><a href="https://github.com/archisman-panigrahi/">Archisman Panigrahi</a></li>
        </ul>
        <p>Bug reports and pull requests are welcome on the <a href="{HOMEPAGE}">project's GitHub page</a>.</p>
        """
        authors_text.setHtml(authors_html)
        authors_text.setOpenExternalLinks(True)
        tabs.addTab(authors_text, "Authors")

        # License tab
        license_text = QTextBrowser()
        if LICENSE_PATH.exists():
            try:
                license_content = LICENSE_PATH.read_text(encoding="utf-8")
                # present license as preformatted text for readability
                license_text.setPlainText(license_content)
            except Exception:
                license_text.setHtml("<p>Unable to read LICENSE file.</p>")
        else:
            license_text.setHtml(f"<p>License file not found in repository. See <a href=\"{REPO_URL}\">project page</a>.</p>")
        tabs.addTab(license_text, "License")

        # Bottom bar with centered dedication and right-aligned Close button
        btn_hbox = QHBoxLayout()
        # left spacer
        btn_hbox.addStretch()

        # centered dedication label
        dedication = QLabel("<em>Dedicated to all my friends</em>")
        dedication.setAlignment(Qt.AlignmentFlag.AlignCenter)
        # give it an expanding policy so it sits centered
        dedication.setMinimumWidth(240)
        btn_hbox.addWidget(dedication)

        # right side: close button
        btn_hbox.addStretch()
        close_btn = QPushButton("\u2715 Close")
        close_btn.clicked.connect(self.reject)
        close_btn.setFixedHeight(28)
        btn_hbox.addWidget(close_btn)
        vbox.addLayout(btn_hbox)
