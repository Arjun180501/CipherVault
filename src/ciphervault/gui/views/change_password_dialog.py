from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QPushButton, QHBoxLayout, QLineEdit, QFormLayout
)
from PyQt6.QtGui import QPixmap, QPalette, QBrush
from PyQt6.QtCore import Qt

from ciphervault.gui.utils.styles import ENTRY_DIALOG
from ciphervault.gui.utils.settings import BG_PATH, LOGO_PATH


class ChangePasswordDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Change Master Password")
        self.setModal(True)
        self.setMinimumWidth(400)
        self.setStyleSheet(ENTRY_DIALOG["dialog"])

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

        # Layout setup
        layout = QVBoxLayout()
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)

        # Logo
        logo_pixmap = QPixmap(LOGO_PATH).scaled(100, 100, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        logo_label = QLabel()
        logo_label.setPixmap(logo_pixmap)
        logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(logo_label)

        # Title
        title_label = QLabel("Change Master Password")
        title_label.setStyleSheet(ENTRY_DIALOG["title_label"])
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)

        # Form
        form = QFormLayout()
        self.old_pwd = QLineEdit()
        self.old_pwd.setEchoMode(QLineEdit.EchoMode.Password)
        self.new_pwd = QLineEdit()
        self.new_pwd.setEchoMode(QLineEdit.EchoMode.Password)
        self.confirm_pwd = QLineEdit()
        self.confirm_pwd.setEchoMode(QLineEdit.EchoMode.Password)

        form.addRow("Current Password:", self.old_pwd)
        form.addRow("New Password:", self.new_pwd)
        form.addRow("Confirm Password:", self.confirm_pwd)
        layout.addLayout(form)

        # Buttons
        button_bar = QHBoxLayout()
        button_bar.setSpacing(20)

        self.update_btn = QPushButton("Update Password")
        self.update_btn.setStyleSheet(ENTRY_DIALOG["button"])
        self.update_btn.clicked.connect(self.accept)
        button_bar.addWidget(self.update_btn)

        cancel_btn = QPushButton("Cancel")
        cancel_btn.setStyleSheet(ENTRY_DIALOG["button"])
        cancel_btn.clicked.connect(self.reject)
        button_bar.addWidget(cancel_btn)

        layout.addLayout(button_bar)
        self.setLayout(layout)

    def get_passwords(self):
        return self.old_pwd.text(), self.new_pwd.text(), self.confirm_pwd.text()
