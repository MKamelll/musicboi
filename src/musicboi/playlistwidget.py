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
from youtubeworker import YoutubeWorker, TrackInfo


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

    def on_result(self, track: TrackInfo) -> None:
        track_widget = PlayListItemWidget(track, self)
        item_widget = QListWidgetItem(self)
        item_widget.setSizeHint(track_widget.sizeHint())
        self.addItem(item_widget)
        self.setItemWidget(item_widget, track_widget)

    def on_youtube_urls(self, urls: list[str]) -> None:
        self.worker = YoutubeWorker(urls)
        self.worker.started.connect(self.loading)
        self.worker.result.connect(self.on_result)
        self.worker.finished.connect(self.done)
        self.worker.start()
