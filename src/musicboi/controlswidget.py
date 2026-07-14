from PySide6.QtWidgets import QWidget, QHBoxLayout, QPushButton
from PySide6.QtCore import Signal, Qt


class ControlsWidget(QWidget):
    startPasting = Signal()
    stopPasting = Signal()

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.hbox = QHBoxLayout(self)
        self.magnet_toggle = QPushButton("magnet")
        self.magnet_toggle.setToolTip("toggle this and start copying links")
        self.magnet_toggle.setCheckable(True)
        self.magnet_toggle.toggled.connect(self.on_magnet_toggle)
        self.hbox.addWidget(self.magnet_toggle, 0, Qt.AlignmentFlag.AlignLeft)

    def on_magnet_toggle(self, is_toggled: bool) -> None:
        if is_toggled:
            self.startPasting.emit()
        else:
            self.stopPasting.emit()
