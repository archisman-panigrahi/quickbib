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

from doi2bib3.backend import get_bibtex_from_doi, DOIError


def get_bibtex_for_doi(doi: str):
    """Fetch BibTeX for a DOI.
    Returns a tuple (found: bool, bibtex: str, error: str|None).
    - If found is True, bibtex contains the BibTeX string and error is None.
    - If found is False and error is None, the DOI was not found.
    - If an exception occurred, found is False, bibtex is empty and error
      contains the string representation of the exception.
    """
    try:
        # doi2bib3 provides get_bibtex_from_doi which returns the BibTeX
        # string or raises DOIError on resolution problems. To preserve the
        # original contract, return (True, bibtex, None) on success and
        # (False, "", error) on failure.
        bibtex = get_bibtex_from_doi(doi)
        return True, bibtex, None
    except DOIError as e:
        # DOIError indicates resolution/lookup failure; return found=False
        # and include the error message so the UI can display it.
        return False, "", str(e)
    except Exception as e:
        # Any other unexpected exception
        return False, "", str(e)


def copy_to_clipboard(text: str) -> bool:
    """Copy text to the system clipboard.
    Returns True on success, False otherwise.
    """
    # Use the native Qt clipboard only. If there is no active Qt
    # application instance, return False (caller should ensure a
    # QApplication/QGuiApplication is running when using this helper).
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
