from PySide6.QtWidgets import QWidget, QHBoxLayout, QPushButton
from PySide6.QtCore import Signal, Qt


class ControlsWidget(QWidget):
    startPasting = Signal()
    stopPasting = Signal()
    playing = Signal()
    paused = Signal()
    forward = Signal()
    backward = Signal()

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.hbox = QHBoxLayout(self)
        self.backwards_btn = QPushButton("back")
        self.play_toggle = QPushButton("play")
        self.play_toggle.setCheckable(True)
        self.play_toggle.toggled.connect(self.on_play_toggle)
        self.forwards_btn = QPushButton("forward")
        self.hbox.addWidget(self.backwards_btn)
        self.hbox.addWidget(self.play_toggle)
        self.hbox.addWidget(self.forwards_btn)
        self.hbox.addStretch(1)

        self.magnet_toggle = QPushButton("magnet")
        self.magnet_toggle.setToolTip("toggle this and start copying links")
        self.magnet_toggle.setCheckable(True)
        self.magnet_toggle.toggled.connect(self.on_magnet_toggle)
        self.hbox.addWidget(self.magnet_toggle)

    def on_play_toggle(self, is_toggled: bool) -> None:
        if is_toggled:
            self.play_toggle.setText("pause")
            self.playing.emit()
        else:
            self.play_toggle.setText("play")
            self.paused.emit()

    def on_magnet_toggle(self, is_toggled: bool) -> None:
        if is_toggled:
            self.startPasting.emit()
        else:
            self.stopPasting.emit()
