import json
import urllib.request
import webbrowser
from PyQt6.QtCore import QObject, pyqtSignal

from .app_info import APP_VERSION, HOMEPAGE


class UpdateWorker(QObject):
    """Check GitHub Releases for the latest release and compare with APP_VERSION.

    Emits finished(update_available: bool, latest_version: str, info_url: str, error: object)
    """
    finished = pyqtSignal(bool, str, str, object)

    def __init__(self):
        super().__init__()

    def run(self):
        try:
            url = "https://api.github.com/repos/archisman-panigrahi/quickbib/releases/latest"
            req = urllib.request.Request(url, headers={"User-Agent": "QuickBib Update Checker"})
            with urllib.request.urlopen(req, timeout=10) as resp:
                data = resp.read().decode()
            obj = json.loads(data)
            tag = obj.get("tag_name") or obj.get("name") or ""
            latest = tag.lstrip("v")
            html_url = obj.get("html_url") or HOMEPAGE

            def parse_ver(s: str):
                parts = []
                for p in s.split('.'):
                    num = ''
                    for ch in p:
                        if ch.isdigit():
                            num += ch
                        else:
                            break
                    parts.append(int(num) if num else 0)
                return parts

            latest_parts = parse_ver(latest)
            current_parts = parse_ver(APP_VERSION)

            # compare lexicographically
            update_available = latest_parts > current_parts

            self.finished.emit(update_available, latest, html_url, None)
        except Exception as e:
            self.finished.emit(False, "", HOMEPAGE, str(e))
