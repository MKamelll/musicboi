from PySide6.QtWidgets import (
    QMainWindow,
    QApplication,
    QListWidget,
    QWidget,
    QVBoxLayout,
    QLabel,
    QGroupBox,
    QListWidgetItem,
    QProgressBar,
    QScrollArea,
)
from PySide6.QtGui import QKeyEvent, QKeySequence

from PySide6.QtCore import Qt, Signal, QThread
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


class YoutubeWorker(QThread):
    result = Signal(TrackInfo)

    def __init__(self, urls: list[str]) -> None:
        super().__init__()
        self.urls = urls
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

    def run(self) -> None:
        for i, url in enumerate(self.urls):
            track = self.get_info(url)
            self.result.emit(track)


class PlayListItemWidget(QWidget):
    def __init__(self, track: TrackInfo, parent: QWidget | None) -> None:
        super().__init__(parent)

        self.vbox = QVBoxLayout(self)
        self.title_label = QLabel(f"Title: {track.title}")
        self.title_label.setWordWrap(True)

        d = int(track.duration_secs)
        hours, remainder = divmod(d, 3600)
        minutes, seconds = divmod(remainder, 60)

        if hours > 0:
            duration = f"{hours}:{minutes:02d}:{seconds:02d}"
        else:
            duration = f"{minutes}:{seconds:02d}"

        self.duration_secs_label = QLabel(f"Duration: {duration}")

        self.vbox.addWidget(self.title_label)
        self.vbox.addWidget(self.duration_secs_label)


class PlayListWidget(QListWidget):
    loading = Signal()
    done = Signal()

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.supported_backends = ["www.youtube.com"]

    def keyPressEvent(self, event: QKeyEvent) -> None:
        if event.matches(QKeySequence.StandardKey.Paste):
            self.handle_paste()
            return
        super().keyPressEvent(event)

    def on_result(self, track: TrackInfo) -> None:
        track_widget = PlayListItemWidget(track, self)
        item_widget = QListWidgetItem(self)
        item_widget.setSizeHint(track_widget.sizeHint())
        self.addItem(item_widget)
        self.setItemWidget(item_widget, track_widget)

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

        self.worker = YoutubeWorker(urls)
        self.worker.started.connect(self.loading)
        self.worker.result.connect(self.on_result)
        self.worker.finished.connect(self.done)
        self.worker.start()


class PlayerWidget(QWidget):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.vbox = QVBoxLayout(self)
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 0)
        self.progress_bar.hide()

        self.paste_label = QLabel("Copy into your clipboard, then paste here")
        self.play_list = PlayListWidget()
        self.play_list.loading.connect(self.progress_bar.show)
        self.play_list.done.connect(self.progress_bar.hide)
        self.play_list.done.connect(self.progress_bar.reset)

        self.scroll_area = QScrollArea()
        self.scroll_area.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setWidget(self.play_list)

        self.vbox.addWidget(
            self.paste_label,
            0,
            Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignCenter,
        )
        self.vbox.addWidget(self.scroll_area)
        self.vbox.addWidget(self.progress_bar)


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
