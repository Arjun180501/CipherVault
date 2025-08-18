from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QPushButton, QHBoxLayout
)
from PyQt6.QtGui import QPixmap, QPalette, QBrush
from PyQt6.QtCore import Qt

from ciphervault.gui.utils.styles import ENTRY_DIALOG
from ciphervault.gui.utils.settings import BG_PATH, LOGO_PATH


class PopupDialog(QDialog):
    def __init__(self, title: str, message: str, yes_label: str = "OK", no_label: str = None, parent=None):
        super().__init__(parent)

        self.setWindowTitle(title)
        self.setModal(True)
        self.setStyleSheet(ENTRY_DIALOG["dialog"])
        self.setMinimumWidth(400)

        # Brick background
        self.setAutoFillBackground(True)
        palette = QPalette()
        bg_pixmap = QPixmap(BG_PATH).scaled(
            800,
            600,
            Qt.AspectRatioMode.IgnoreAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )
        palette.setBrush(QPalette.ColorRole.Window, QBrush(bg_pixmap))
        self.setPalette(palette)

        layout = QVBoxLayout()
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)

        # Logo
        logo_pixmap = QPixmap(LOGO_PATH).scaled(
            100, 100,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )
        logo_label = QLabel()
        logo_label.setPixmap(logo_pixmap)
        logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(logo_label)

        # Title
        title_label = QLabel(title)
        title_label.setStyleSheet(ENTRY_DIALOG["title_label"])
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)

        # Message
        message_label = QLabel(message)
        message_label.setStyleSheet(ENTRY_DIALOG["message_label"])
        message_label.setWordWrap(True)
        message_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(message_label)

        # Buttons
        button_bar = QHBoxLayout()
        button_bar.setSpacing(20)

        yes_btn = QPushButton(yes_label)
        yes_btn.setStyleSheet(ENTRY_DIALOG["button"])
        yes_btn.clicked.connect(self.accept)
        button_bar.addWidget(yes_btn)

        if no_label:
            no_btn = QPushButton(no_label)
            no_btn.setStyleSheet(ENTRY_DIALOG["button"])
            no_btn.clicked.connect(self.reject)
            button_bar.addWidget(no_btn)

        layout.addLayout(button_bar)
        self.setLayout(layout)