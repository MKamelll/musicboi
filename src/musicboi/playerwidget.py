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

from PySide6.QtCore import Qt, Signal, QThread, QUrl
from PySide6.QtMultimedia import QMediaPlayer, QAudioOutput
import sys
from urllib.parse import urlparse
import yt_dlp
from dataclasses import dataclass
from typing import Any
from playlistwidget import PlayListWidget, PlayListItemWidget
from controlswidget import ControlsWidget


class PlayerWidget(QWidget):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)

        self.vbox = QVBoxLayout(self)
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 0)
        self.progress_bar.hide()

        self.audio_output = QAudioOutput(self)
        self.media_player = QMediaPlayer(self)
        self.media_player.setAudioOutput(self.audio_output)
        self.media_player.errorOccurred.connect(
            lambda _, msg: print(f"Error Playback: {msg}")
        )

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
        self.controls_widget.playing.connect(self.on_playing)
        self.controls_widget.paused.connect(self.on_paused)
        self.controls_widget.forward.connect(self.on_forward)
        self.controls_widget.backward.connect(self.on_backward)

        self.vbox.addWidget(self.scroll_area)
        self.vbox.addWidget(self.progress_bar)
        self.vbox.addWidget(self.controls_widget)

    def on_playing(self) -> None:
        item = self.play_list.currentItem()
        widget: PlayListItemWidget | None = self.play_list.itemWidget(item)
        if not widget:
            return
        url = QUrl(widget.track.audio_url)
        self.media_player.setSource(url)
        self.media_player.play()

    def on_paused(self) -> None:
        self.media_player.pause()

    def on_forward(self) -> None:
        next_row = min(self.play_list.currentRow() + 1, self.play_list.count() - 1)
        self.play_list.setCurrentRow(next_row)
        item = self.play_list.item(next_row)
        widget: PlayListItemWidget | None = self.play_list.itemWidget(item)
        if not widget:
            return
        url = QUrl(widget.track.audio_url)
        self.media_player.setSource(url)
        self.media_player.play()

    def on_backward(self) -> None:
        prev_row = max(self.play_list.currentRow() - 1, 0)
        self.play_list.setCurrentRow(prev_row)
        item = self.play_list.item(prev_row)
        widget: PlayListItemWidget | None = self.play_list.itemWidget(item)
        if not widget:
            return
        url = QUrl(widget.track.audio_url)
        self.media_player.setSource(url)
        self.media_player.play()

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
