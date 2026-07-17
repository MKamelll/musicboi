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
from youtube import ydl, TrackInfo


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

    def run(self) -> None:
        self.signals.started.emit()
        track = ydl.get_info(self.url)
        self.signals.result.emit(track)
        self.signals.finished.emit()
