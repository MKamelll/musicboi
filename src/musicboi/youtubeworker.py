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
