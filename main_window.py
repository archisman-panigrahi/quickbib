import threading
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

from helpers import get_bibtex_for_doi, copy_to_clipboard
from about_dialog import AboutDialog
from app_info import LICENSE_PATH


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
        self.setWindowTitle("Quickbib: DOI → BibTeX")
        self.resize(500, 360)

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
                self.status.setText("✅ Copied to clipboard!")
            else:
                self.status.setText("Failed to copy to clipboard.")
        else:
            self.status.setText("Nothing to copy.")
