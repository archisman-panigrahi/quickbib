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
import threading
from pathlib import Path
from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QDialog,
    QTabWidget,
    QTextBrowser,
    QDialogButtonBox,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QTextEdit,
    QMessageBox,
    QFrame,
    QStyle,
)
from PyQt6.QtGui import QAction, QPixmap, QFont
from PyQt6.QtCore import QObject, pyqtSignal, Qt

from helpers import get_bibtex_for_doi, copy_to_clipboard

# Application metadata
APP_NAME = "QuickBib"
APP_VERSION = "0.1"
HOMEPAGE = "https://github.com/archisman-panigrahi/quickbib"
REPO_URL = HOMEPAGE
LICENSE_PATH = Path(__file__).with_name("LICENSE")


class FetchWorker(QObject):
    finished = pyqtSignal(bool, str, object)  # found, bibtex, error

    def __init__(self, doi: str):
        super().__init__()
        self.doi = doi

    def run(self):
        try:
            found, bibtex, error = get_bibtex_for_doi(self.doi)
        except Exception as e:
            found, bibtex, error = False, "", str(e)
        self.finished.emit(found, bibtex, error)


class AboutDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("About QuickBib")
        self.resize(600, 320)

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
        # Try to get a meaningful application icon; fall back to a generic style icon
        try:
            app_icon = QApplication.instance().windowIcon()
            pix = app_icon.pixmap(64, 64)
            if pix.isNull():
                raise Exception()
        except Exception:
            pix = self.style().standardIcon(QStyle.StandardPixmap.SP_ComputerIcon).pixmap(64, 64)
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

        # Styling to approximate the screenshot (subtle gray tabs and rounded pane)
        self.setStyleSheet("""
        QTabWidget::pane { border: 1px solid #d0d0d0; background: #ffffff; border-radius: 6px; }
        QTabBar::tab { background: #e9e9e9; padding: 6px 12px; border-top-left-radius: 4px; border-top-right-radius: 4px; }
        QTabBar::tab:selected { background: #f5f5f5; }
        QTextBrowser { background: transparent; }
        # make links blue and underlined
        QTextBrowser::anchor { color: #1a73e8; text-decoration: underline; }
        """)
        # About tab
        about_text = QTextBrowser()
        about_html = f"""
        <h2>{APP_NAME} <small>v{APP_VERSION}</small></h2>
        <p>{APP_NAME} fetches BibTeX entries from DOIs, arXiv IDs, and known journal URLs.
        It's a small utility to quickly convert identifiers into usable BibTeX records.</p>
        <p> Quickbib uses <a href="https://github.com/archisman-panigrahi/doi2bib3">doi2bib3</a>
        as its backend for DOI to BibTeX conversion.</p>
        <p>
          <b>Homepage:</b> <a href="{HOMEPAGE}">{HOMEPAGE}</a><br/>
        </p>
        <p>License: Released under GPLv3. See the <i>License</i> tab for details.</p>
        """
        about_text.setHtml(about_html)
        about_text.setOpenExternalLinks(True)
        tabs.addTab(about_text, "About")

        # Authors tab
        authors_text = QTextBrowser()
        authors_html = """
        <h3>Authors & Contributors</h3>
        <ul>
          <li><a href="">Archisman Panigrahi</a></li>
        </ul>
        <p>Contributions, issues and pull requests are welcome on the project's GitHub page.</p>
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

        # Close button right-aligned
        btn_hbox = QHBoxLayout()
        btn_hbox.addStretch()
        close_btn = QPushButton("\u2715 Close")
        close_btn.clicked.connect(self.reject)
        # use a small subtle style for the button
        close_btn.setFixedHeight(28)
        btn_hbox.addWidget(close_btn)
        vbox.addLayout(btn_hbox)


class QuickBibWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("DOI → BibTeX")
        self.resize(640, 360)

        central = QWidget()
        self.setCentralWidget(central)

        vbox = QVBoxLayout()
        central.setLayout(vbox)

        # Menu bar
        menubar = self.menuBar()
        file_menu = menubar.addMenu("&File")
        quit_action = QAction("&Quit", self)
        quit_action.triggered.connect(self.close)
        file_menu.addAction(quit_action)

        edit_menu = menubar.addMenu("&Edit")
        copy_action = QAction("&Copy BibTeX", self)
        copy_action.setShortcut("Ctrl+C")
        copy_action.triggered.connect(self.copy_to_clipboard)
        edit_menu.addAction(copy_action)

        help_menu = menubar.addMenu("&Help")
        about_action = QAction("&About", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)

        # DOI entry
        entry_box = QHBoxLayout()
        vbox.addLayout(entry_box)

        label = QLabel("DOI:")
        entry_box.addWidget(label)

        self.doi_entry = QLineEdit()
        self.doi_entry.setPlaceholderText("DOI or arXiv ID or arXiv URL or Journal URL")
        entry_box.addWidget(self.doi_entry)

        fetch_btn = QPushButton("Fetch")
        fetch_btn.clicked.connect(self.fetch_bibtex)
        entry_box.addWidget(fetch_btn)

        # Status label
        self.status = QLabel("")
        self.status.setAlignment(Qt.AlignmentFlag.AlignLeft)
        vbox.addWidget(self.status)

        # Text view
        self.textview = QTextEdit()
        self.textview.setReadOnly(True)
        self.textview.setLineWrapMode(QTextEdit.LineWrapMode.WidgetWidth)
        self.textview.setMinimumHeight(250)
        vbox.addWidget(self.textview)

        # Buttons
        btn_box = QHBoxLayout()
        btn_box.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        vbox.addLayout(btn_box)

        copy_btn = QPushButton("📋 Copy to clipboard")
        copy_btn.clicked.connect(self.copy_to_clipboard)
        btn_box.addWidget(copy_btn)

        # Keep references to worker/thread so they don't get GC'd
        self._worker_thread = None

    def show_about(self):
        dlg = AboutDialog(self)
        dlg.exec()

    def fetch_bibtex(self):
        doi = self.doi_entry.text().strip()
        if not doi:
            self.status.setText("Please enter a DOI.")
            return

        self.status.setText("Fetching BibTeX...")
        self.textview.clear()

        # Run the fetch in a background thread to avoid blocking the UI.
        worker = FetchWorker(doi)

        # Use Python thread to call worker.run and then emit finished via Qt
        def thread_target():
            worker.run()

        # Connect the finished signal to UI handler
        worker.finished.connect(self.on_fetch_finished)

        t = threading.Thread(target=thread_target, daemon=True)
        t.start()

        # keep a reference so GC doesn't remove worker until finished
        self._worker_thread = (worker, t)

    def on_fetch_finished(self, found: bool, bibtex: str, error: object):
        if found:
            self.textview.setPlainText(bibtex)
            self.status.setText("✅ Fetched successfully.")
        else:
            self.textview.clear()
            if error:
                self.status.setText(f"Error: {error}")
            else:
                self.status.setText("Error: DOI not found or CrossRef request failed.")

        # release worker ref
        self._worker_thread = None

    def copy_to_clipboard(self):
        text = self.textview.toPlainText()
        if text.strip():
            ok = copy_to_clipboard(text)
            if ok:
                self.status.setText("Copied to clipboard!")
            else:
                self.status.setText("Failed to copy to clipboard.")
        else:
            self.status.setText("Nothing to copy.")


def main(argv):
    app = QApplication(argv)
    win = QuickBibWindow()
    win.show()
    return app.exec()


if __name__ == "__main__":
    sys.exit(main(sys.argv))
