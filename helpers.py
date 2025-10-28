#!/usr/bin/env python3

from doi2bib3.backend import get_bibtex_from_doi, DOIError
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
    try:
        pyperclip.copy(text)
        return True
    except Exception:
        return False
