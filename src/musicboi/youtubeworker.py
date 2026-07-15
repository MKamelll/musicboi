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

from PySide6.QtCore import Qt, Signal, QRunnable, QObject
import sys
from urllib.parse import urlparse
import yt_dlp
from dataclasses import dataclass
from typing import Any, Callable


@dataclass
class TrackInfo:
    title: str
    duration_secs: str
    uploader: str
    description: str
    thumbnails: list[dict[str, Any]]


class WorkerSignals(QObject):
    started = Signal()
    finished = Signal()
    result = Signal(TrackInfo)


class YoutubeWorker(QRunnable):
    def __init__(self, url: str) -> None:
        super().__init__()
        self.setAutoDelete(True)
        self.url = url
        self.signals = WorkerSignals()
        self.opts: Any = {
            "skip_download": True,
            "quiet": True,
        }

    def get_info(self, url: str) -> TrackInfo:
        with yt_dlp.YoutubeDL(self.opts) as ydl:
            info = ydl.extract_info(url)
            default_value = "N/A"
            return TrackInfo(
                title=info.get("title") or default_value,
                duration_secs=str(info.get("duration")) or default_value,
                uploader=info.get("uploader") or default_value,
                description=info.get("description") or default_value,
                thumbnails=info.get("thumbnails") or [],
            )

    def run(self) -> None:
        self.signals.started.emit()
        track = self.get_info(self.url)
        self.signals.result.emit(track)
        self.signals.finished.emit()
