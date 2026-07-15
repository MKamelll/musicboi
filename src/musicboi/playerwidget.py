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
from playlistwidget import PlayListWidget
from controlswidget import ControlsWidget


class PlayerWidget(QWidget):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)

        self.vbox = QVBoxLayout(self)
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 0)
        self.progress_bar.hide()

        self.play_list = PlayListWidget()
        self.play_list.loading.connect(self.progress_bar.show)
        self.play_list.done.connect(self.progress_bar.hide)

        self.scroll_area = QScrollArea()
        self.scroll_area.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setWidget(self.play_list)

        self.clipboard = QApplication.clipboard()
        self.controls_widget = ControlsWidget(self)
        self.controls_widget.startPasting.connect(
            lambda: self.clipboard.dataChanged.connect(self.on_clipboard_change)
        )
        self.controls_widget.stopPasting.connect(
            lambda: self.clipboard.dataChanged.disconnect(self.on_clipboard_change)
        )

        self.vbox.addWidget(self.scroll_area)
        self.vbox.addWidget(self.progress_bar)
        self.vbox.addWidget(self.controls_widget)

    def is_url_backend(self, text: str, backend: str) -> bool:
        try:
            result = urlparse(text)
            is_real_url = all([result.scheme in ["http", "https"], result.netloc])
            is_backend = (
                True if result.hostname and backend in result.hostname else False
            )
            if is_real_url and is_backend:
                return True
        except ValueError:
            return False

    def on_clipboard_change(self) -> None:
        mime_data = self.clipboard.mimeData()
        if not mime_data.hasText():
            return
        lines = mime_data.text().splitlines()
        youtube_urls = [
            line for line in lines if self.is_url_backend(line, "youtube.com")
        ]
        self.play_list.on_youtube_urls(youtube_urls)
