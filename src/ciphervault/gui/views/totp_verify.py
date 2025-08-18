from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton, QHBoxLayout
from PyQt6.QtGui import QPixmap, QPalette, QBrush
from PyQt6.QtCore import Qt

from ciphervault.gui.utils.styles import ENTRY_DIALOG
from ciphervault.gui.utils.settings import BG_PATH, LOGO_PATH

class TotpVerify(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Two-Factor Authentication")
        self.setModal(True)
        self.setStyleSheet(ENTRY_DIALOG["dialog"])
        self.setMinimumWidth(400)

        # Background
        self.setAutoFillBackground(True)
        palette = QPalette()
        bg_pixmap = QPixmap(BG_PATH).scaled(
            800, 600,
            Qt.AspectRatioMode.IgnoreAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )
        palette.setBrush(QPalette.ColorRole.Window, QBrush(bg_pixmap))
        self.setPalette(palette)

        layout = QVBoxLayout()
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)

        # Logo
        logo_pixmap = QPixmap(LOGO_PATH).scaled(100, 100, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        logo_label = QLabel()
        logo_label.setPixmap(logo_pixmap)
        logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(logo_label)

        # Title and message
        title_label = QLabel("Two-Factor Authentication")
        title_label.setStyleSheet(ENTRY_DIALOG["title_label"])
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)

        message_label = QLabel("This vault requires a TOTP code. Please enter it:")
        message_label.setStyleSheet(ENTRY_DIALOG["message_label"])
        message_label.setWordWrap(True)
        message_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(message_label)

        # TOTP input field
        self.totp_input = QLineEdit()
        self.totp_input.setPlaceholderText("TOTP Code")
        self.totp_input.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.totp_input)

        # Buttons
        button_bar = QHBoxLayout()
        button_bar.setSpacing(20)

        yes_btn = QPushButton("OK")
        yes_btn.setStyleSheet(ENTRY_DIALOG["button"])
        yes_btn.clicked.connect(self.accept)
        button_bar.addWidget(yes_btn)

        no_btn = QPushButton("Cancel")
        no_btn.setStyleSheet(ENTRY_DIALOG["button"])
        no_btn.clicked.connect(self.reject)
        button_bar.addWidget(no_btn)

        layout.addLayout(button_bar)
        self.setLayout(layout)

    def get_code(self):
        return self.totp_input.text().strip()
