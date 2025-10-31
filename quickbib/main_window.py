import threading
import sys
from pathlib import Path
from PyQt6.QtWidgets import (
    QMainWindow,
    QWidget,
    QTabWidget,
    QTextBrowser,
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
from PyQt6.QtGui import QAction, QPixmap, QFont, QIcon
from PyQt6.QtCore import QObject, pyqtSignal, Qt

from .helpers import get_bibtex_for_doi, copy_to_clipboard
from .about_dialog import AboutDialog
from .app_info import LICENSE_PATH

# Import Windows-only update checker (not imported on other platforms so it
# won't be bundled with Linux packages). The module is optional.
UpdateWorker = None
if sys.platform == "win32":
    try:
        from .windows_update import UpdateWorker
    except Exception:
        UpdateWorker = None


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


class QuickBibWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("QuickBib: DOI → BibTeX")
        self.resize(500, 380)

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

        # Windows-only update menu entry
        if UpdateWorker is not None:
            check_updates_action = QAction("Check for &updates...", self)
            check_updates_action.triggered.connect(self.check_for_updates)
            help_menu.addAction(check_updates_action)

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
        self._update_worker_thread = None
        # Run a silent update check on startup only on Windows
        if UpdateWorker is not None:
            try:
                if "--check-updates" in sys.argv or True:
                    self._start_update_check(silent=True)
            except Exception:
                pass

    def show_about(self):
        dlg = AboutDialog(self)
        dlg.exec()

    def _start_update_check(self, silent: bool = False):
        if UpdateWorker is None:
            return
        worker = UpdateWorker()

        def thread_target():
            worker.run()

        worker.finished.connect(lambda available, latest, url, error: self.on_update_check_finished(available, latest, url, error, silent))

        t = threading.Thread(target=thread_target, daemon=True)
        t.start()

        self._update_worker_thread = (worker, t)

    def check_for_updates(self):
        # user-initiated check (show dialog)
        if UpdateWorker is None:
            QMessageBox.information(self, "Updates not supported", "Update checking is only available on the Windows build.")
            return
        self.status.setText("Checking for updates...")
        self._start_update_check(silent=False)

    def on_update_check_finished(self, available: bool, latest: str, url: str, error: object, silent: bool):
        self._update_worker_thread = None
        if error:
            if not silent:
                QMessageBox.information(self, "Update check failed", f"Could not check for updates: {error}")
            self.status.setText("")
            return

        if available:
            msg = QMessageBox(self)
            msg.setWindowTitle("Update available")
            msg.setText(f"A new QuickBib release is available: {latest}")
            msg.setInformativeText("Would you like to open the Releases page to download the latest build?")
            msg.setStandardButtons(QMessageBox.StandardButton.Open | QMessageBox.StandardButton.Cancel)
            ret = msg.exec()
            if ret == QMessageBox.StandardButton.Open:
                import webbrowser

                webbrowser.open(url)
            self.status.setText("Update available")
        else:
            if not silent:
                QMessageBox.information(self, "Up to date", f"You are running the latest version.")
            self.status.setText("Up to date")

    def fetch_bibtex(self):
        doi = self.doi_entry.text().strip()
        if not doi:
            self.status.setText("Please enter a DOI.")
            return

        self.status.setText("Fetching BibTeX...")
        self.textview.clear()

        worker = FetchWorker(doi)

        def thread_target():
            worker.run()

        worker.finished.connect(self.on_fetch_finished)

        t = threading.Thread(target=thread_target, daemon=True)
        t.start()

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

        self._worker_thread = None

    def copy_to_clipboard(self):
        text = self.textview.toPlainText()
        if text.strip():
            ok = copy_to_clipboard(text)
            if ok:
                self.status.setText("✅ Copied to clipboard!")
            else:
                self.status.setText("Failed to copy to clipboard.")
        else:
            self.status.setText("Nothing to copy.")
