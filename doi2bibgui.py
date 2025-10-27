#!/usr/bin/env python3

import sys
import gi
gi.require_version('Gtk', '4.0')
from gi.repository import Gtk, GLib
import pyperclip
from doi2bib.crossref import get_bib_from_doi

class Doi2BibWindow(Gtk.ApplicationWindow):
    def __init__(self, app):
        super().__init__(application=app)
        self.set_title("DOI → BibTeX")
        self.set_default_size(700, 400)
        # self.set_margin_top(12)
        # self.set_margin_bottom(12)
        # self.set_margin_start(12)
        # self.set_margin_end(12)

        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        self.set_child(box)

        # DOI entry
        entry_box = Gtk.Box(spacing=8)
        box.append(entry_box)

        label = Gtk.Label(label="DOI:")
        label.set_halign(Gtk.Align.START)
        entry_box.append(label)

        self.doi_entry = Gtk.Entry()
        self.doi_entry.set_placeholder_text("10.1038/s41586-019-1666-5")
        self.doi_entry.set_hexpand(True)
        entry_box.append(self.doi_entry)

        fetch_btn = Gtk.Button(label="Fetch")
        fetch_btn.connect("clicked", self.fetch_bibtex)
        entry_box.append(fetch_btn)

        # Status label
        self.status = Gtk.Label(label="")
        self.status.set_halign(Gtk.Align.START)
        box.append(self.status)

        # Text view
        scroller = Gtk.ScrolledWindow()
        scroller.set_min_content_height(250)
        box.append(scroller)

        self.textview = Gtk.TextView()
        # Wrap long lines so output never extends off the visible area
        self.textview.set_wrap_mode(Gtk.WrapMode.WORD)
        self.textview.set_editable(False)
        self.textbuffer = self.textview.get_buffer()
        scroller.set_child(self.textview)

        # Buttons
        btn_box = Gtk.Box(spacing=8)
        box.append(btn_box)

        copy_btn = Gtk.Button(label="📋 Copy to clipboard")
        copy_btn.connect("clicked", self.copy_to_clipboard)
        btn_box.append(copy_btn)

    def fetch_bibtex(self, _btn):
        doi = self.doi_entry.get_text().strip()
        if not doi:
            self.status.set_text("Please enter a DOI.")
            return

        self.status.set_text("Fetching BibTeX...")
        GLib.idle_add(self._fetch_bibtex_async, doi)

    def _fetch_bibtex_async(self, doi):
        try:
            found, bibtex = get_bib_from_doi(doi)
            if found:
                self.textbuffer.set_text(bibtex)
                self.status.set_text("✅ Fetched successfully.")
            else:
                self.textbuffer.set_text("")
                self.status.set_text("Error: DOI not found or CrossRef request failed.")
        except Exception as e:
            self.textbuffer.set_text("")
            self.status.set_text(f"Error: {e}")

    def copy_to_clipboard(self, _btn):
        start, end = self.textbuffer.get_bounds()
        text = self.textbuffer.get_text(start, end, False)
        if text.strip():
            pyperclip.copy(text)
            self.status.set_text("Copied to clipboard!")
        else:
            self.status.set_text("Nothing to copy.")


class Doi2BibApp(Gtk.Application):
    def __init__(self):
        super().__init__(application_id="org.example.doi2bib")
        self.connect("activate", self.on_activate)

    def on_activate(self, app):
        win = Doi2BibWindow(self)
        win.present()


if __name__ == "__main__":
    app = Doi2BibApp()
    app.run(sys.argv)
