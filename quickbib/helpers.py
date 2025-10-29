#!/usr/bin/env python3
from doi2bib3.backend import get_bibtex_from_doi, DOIError


def get_bibtex_for_doi(doi: str):
    try:
        bibtex = get_bibtex_from_doi(doi)
        return True, bibtex, None
    except DOIError as e:
        return False, "", str(e)
    except Exception as e:
        return False, "", str(e)


def copy_to_clipboard(text: str) -> bool:
    try:
        from PyQt6.QtGui import QGuiApplication

        app = QGuiApplication.instance()
        if app is None:
            return False
        cb = QGuiApplication.clipboard()
        cb.setText(text)
        return True
    except Exception:
        return False
