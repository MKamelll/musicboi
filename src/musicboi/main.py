from PySide6.QtWidgets import (
    QMainWindow,
    QApplication,
    QListWidget,
    QWidget,
    QVBoxLayout,
    QLabel,
)
from PySide6.QtGui import QKeyEvent, QKeySequence

from PySide6.QtCore import Qt, Signal
import sys
from urllib.parse import urlparse
import yt_dlp
from dataclasses import dataclass
from typing import Any


@dataclass
class TrackInfo:
    title: str
    duration_secs: str
    uploader: str
    description: str
    thumbnails: list[dict[str, Any]]


class YoutubeBackend:
    def __init__(self) -> None:
        self.opts: Any = {
            "skip_download": True,
            "quiet": True,
        }

    def get_info(self, url: str) -> TrackInfo:
        with yt_dlp.YoutubeDL(self.opts) as ydl:
            info = ydl.extract_info(url)
            return TrackInfo(
                title=info["title"] or "N/A",
                duration_secs=str(info["duration"]) or "N/A",
                uploader=info["uploader"] or "N/A",
                description=info["description"] or "N/A",
                thumbnails=info["thumbnails"] or [],
            )


youtube = YoutubeBackend()


class PlayListWidget(QListWidget):
    total_urls = Signal(int)
    progress = Signal(int)

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.supported_backends = ["www.youtube.com"]

    def keyPressEvent(self, event: QKeyEvent) -> None:
        if event.matches(QKeySequence.StandardKey.Paste):
            self.handle_paste()
            return
        super().keyPressEvent(event)

    def handle_paste(self) -> None:
        clipboard = QApplication.clipboard()
        text = clipboard.text()
        if not text:
            return

        urls: list[str] = []
        for line in text.splitlines():
            try:
                result = urlparse(line)
                is_real_url = all([result.scheme in ["http", "https"], result.netloc])
                is_supported = result.hostname in self.supported_backends
                if is_real_url and is_supported:
                    urls.append(result.geturl())
            except ValueError:
                pass

        tracks = [youtube.get_info(url) for url in urls]
        for track in tracks:
            print(track)


class PlayerWidget(QWidget):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.vbox = QVBoxLayout(self)
        self.paste_label = QLabel("Copy into your clipboard, then paste here")
        self.play_list = PlayListWidget()
        self.vbox.addWidget(
            self.paste_label,
            0,
            Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignCenter,
        )
        self.vbox.addWidget(self.play_list)


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("musicboi")
        self.resize(600, 400)
        player = PlayerWidget(self)
        self.setCentralWidget(player)


if __name__ == "__main__":
    app = QApplication()
    w = MainWindow()
    w.show()
    sys.exit(app.exec())
