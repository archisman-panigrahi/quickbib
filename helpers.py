#!/usr/bin/env python3

from doi2bib.crossref import get_bib_from_doi
import pyperclip


def get_bibtex_for_doi(doi: str):
    """Fetch BibTeX for a DOI.
    Returns a tuple (found: bool, bibtex: str, error: str|None).
    - If found is True, bibtex contains the BibTeX string and error is None.
    - If found is False and error is None, the DOI was not found.
    - If an exception occurred, found is False, bibtex is empty and error
      contains the string representation of the exception.
    """
    try:
        found, bibtex = get_bib_from_doi(doi)
        return found, bibtex, None
    except Exception as e:
        return False, "", str(e)


def copy_to_clipboard(text: str) -> bool:
    """Copy text to the system clipboard.
    Returns True on success, False otherwise.
    """
    try:
        pyperclip.copy(text)
        return True
    except Exception:
        return False
