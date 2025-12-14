from PyQt6.QtWidgets import (
        QDialog,
        QVBoxLayout,
        QHBoxLayout,
        QPushButton,
        QLabel,
        QPlainTextEdit,
)
from PyQt6.QtGui import QFont, QTextCharFormat, QColor, QSyntaxHighlighter, QFontMetrics, QFontDatabase
from PyQt6.QtCore import Qt, QRegularExpression


class HowToUseDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("How to use QuickBib")
        self.resize(700, 460)

        vbox = QVBoxLayout()
        vbox.setContentsMargins(12, 12, 12, 12)
        vbox.setSpacing(8)
        self.setLayout(vbox)

        header = QLabel("Quick examples and usage")
        header_font = QFont()
        header_font.setPointSize(14)
        header_font.setBold(True)
        header.setFont(header_font)
        header.setAlignment(Qt.AlignmentFlag.AlignLeft)
        vbox.addWidget(header)

        # Intro text removed: examples are shown below as individual code widgets

        # Show individual example items as monospace, read-only code widgets
        # Choose a reliable monospace font: prefer system fixed font, fall back to Courier New
        try:
            code_font = QFontDatabase.systemFont(QFontDatabase.FixedFont)
            code_font.setPointSize(10)
        except Exception:
            code_font = QFont("Courier New", 10)

        # Ensure the font is treated as monospace/fixed-pitch
        code_font.setStyleHint(QFont.StyleHint.Monospace)
        code_font.setFixedPitch(True)

        # Precompute font metrics for the monospace font once
        fm = QFontMetrics(code_font)

        examples = [
            ("DOI", "10.1038/nphys1170"),
            ("DOI link", "https://doi.org/10.1038/nphys1170"),
            ("arXiv URL", "https://arxiv.org/abs/2411.08091"),
            ("arXiv ID", "arXiv:2411.08091"),
            ("arXiv ID (short)", "2411.08091"),
            ("Old arXiv ID", "hep-th/9901001"),
            ("Journal URL (works with APS, AMS, AMS, PNAS, Nature...)", "https://journals.aps.org/prl/abstract/10.1103/v6r7-4ph9"),
            ("Title (fuzzy search)", "Projected Topological Branes"),
        ]

        # Define a simple highlighter to apply to each example code widget
        class SimpleHighlighter(QSyntaxHighlighter):
            def __init__(self, parent=None):
                super().__init__(parent)
                self.rules = []
                # Strings format
                str_fmt = QTextCharFormat()
                str_fmt.setForeground(QColor('#008000'))
                self.rules.append((QRegularExpression(r'".*?"'), str_fmt))
                self.rules.append((QRegularExpression(r"'.*?'"), str_fmt))

                # URLs (simple)
                url_fmt = QTextCharFormat()
                url_fmt.setForeground(QColor('#0000FF'))
                self.rules.append((QRegularExpression(r'https?://[^\s]+'), url_fmt))

        # Create code widgets for each example and attach the highlighter
        for label_text, example_text in examples:
            lbl = QLabel(label_text)
            vbox.addWidget(lbl)
            w = QPlainTextEdit()
            w.setReadOnly(True)
            w.setFont(code_font)
            # Trim and set the example text exactly, avoid trailing newlines
            text = example_text.strip()
            w.setPlainText(text)
            # Compute a compact height: one line + small padding
            line_height = fm.lineSpacing()
            # number of lines in text (split on \n)
            lines = max(1, text.count('\n') + 1)
            padding = 8
            w.setFixedHeight(line_height * lines + padding)

            vbox.addWidget(w)
            SimpleHighlighter(w.document())

        btn_hbox = QHBoxLayout()
        btn_hbox.addStretch()
        close_btn = QPushButton("\u2715 Close")
        close_btn.setFixedHeight(28)
        close_btn.clicked.connect(self.reject)
        btn_hbox.addWidget(close_btn)
        vbox.addLayout(btn_hbox)
