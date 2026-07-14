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
from playerwidget import PlayerWidget


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("musicboi")
        self.resize(600, 400)
        player = PlayerWidget(self)
        self.setCentralWidget(player)


if __name__ == "__main__":
    app = QApplication()
    with open("style.css", "r") as f:
        app.setStyleSheet(f.read())
    w = MainWindow()
    w.show()
    sys.exit(app.exec())
