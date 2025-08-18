from PyQt6.QtWidgets import (
    QDialog, QLabel, QPushButton, QVBoxLayout, QFrame,
    QTextBrowser, QHBoxLayout, QGraphicsDropShadowEffect, QWidget
)
from PyQt6.QtCore import Qt, QPropertyAnimation, QRect
from PyQt6.QtGui import QPixmap, QColor, QPalette, QBrush

from ciphervault.gui.utils.settings import LOGO_PATH, BG_PATH
from ciphervault.gui.utils.styles import HELP

class HelpOverlay(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        # Background
        self.setAutoFillBackground(True)
        palette = QPalette()
        bg_pixmap = QPixmap(BG_PATH).scaled(
            self.size(),
            Qt.AspectRatioMode.IgnoreAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )
        palette.setBrush(QPalette.ColorRole.Window, QBrush(bg_pixmap))
        self.setPalette(palette)
        self.setWindowTitle("Help & Instructions")
        self.setModal(True)
        self.setFixedSize(600,600)

        layout = QVBoxLayout()

        # Logo
        logo = QLabel()
        pixmap = QPixmap(LOGO_PATH).scaledToWidth(100, Qt.TransformationMode.SmoothTransformation)
        logo.setPixmap(pixmap)
        logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(logo)

        # Title
        title = QLabel("Help & Instructions")
        title.setStyleSheet("font-size: 22px; font-weight: bold; color: orange;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        # Help text
        help_text = QTextBrowser()
        help_text.setStyleSheet("font-size: 14px; background-color: transparent; color: #CCCCCC; border: none;")
        help_text.setHtml("""
        🔐 <b>Vault Tab</b><br>View, add, edit, or delete your stored passwords.<br><br>
        🛡 <b>Breach Check</b><br>Check if your saved passwords have been compromised. Note: Breach check needs internet connectivity.<br><br>
        🧑‍💼 <b>Settings</b><br>View user info, toggle features like TOTP, breach check, clipboard timer and session timeout. Change Master password or Encryption algorithm.<br><br>
        🔧 <b>Password Generation Tools</b><br>Use Auto or Custom to generate strong passwords.<br><br>
        🛠 <b>Encryption Methods</b><br>CipherVault supports AES-GCM, ChaCha20_Poly1305 encryption techniques. Hybrid method picks the best encryption technique based on user device configuration. Recommended: Please choose hybrid for best security.<br><br>
        📋 <b>Copy Password/Username</b><br>Copy stored passwords/usernames quickly to clipboard.<br><br>
        💡 <b>Tip:</b> Use the search bar to filter entries by service or username.
        """)
        layout.addWidget(help_text)

        # OK button
        ok_btn = QPushButton("OK")
        ok_btn.setStyleSheet(HELP['button'])
        ok_btn.clicked.connect(self.accept)
        layout.addWidget(ok_btn, alignment=Qt.AlignmentFlag.AlignCenter)

        self.setLayout(layout)


class SlideHelpPanel(QFrame):
    def __init__(self, parent):
        super().__init__(parent)
        self.setParent(parent)
        self.setStyleSheet("background-color: #222; color: white;")
        self.setGeometry(parent.width(), 0, 300, parent.height())
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)

        layout = QVBoxLayout()
        layout.setContentsMargins(10, 20, 10, 10)

        title = QLabel("Quick Help")
        title.setStyleSheet("font-size: 18px; color: orange; font-weight: bold;")
        layout.addWidget(title)

        tips = [
            "🔐 Use Vault tab to manage credentials.",
            "🛡 Use Breach tab to check password leaks.",
            "🧑‍💼 Go to Profile to enable TOTP & other settings.",
            "💡 Use Search to filter your passwords.",
        ]

        for tip in tips:
            lbl = QLabel(tip)
            lbl.setWordWrap(True)
            layout.addWidget(lbl)

        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.hide_slide)
        layout.addWidget(close_btn)

        self.setLayout(layout)

        # Drop shadow
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(15)
        shadow.setOffset(0)
        shadow.setColor(QColor(0, 0, 0, 160))
        self.setGraphicsEffect(shadow)

    def show_slide(self):
        self.anim = QPropertyAnimation(self, b"geometry")
        self.anim.setDuration(300)
        self.anim.setStartValue(QRect(self.parent().width(), 0, 300, self.parent().height()))
        self.anim.setEndValue(QRect(self.parent().width() - 300, 0, 300, self.parent().height()))
        self.anim.start()
        self.show()

    def hide_slide(self):
        self.anim = QPropertyAnimation(self, b"geometry")
        self.anim.setDuration(300)
        self.anim.setStartValue(QRect(self.parent().width() - 300, 0, 300, self.parent().height()))
        self.anim.setEndValue(QRect(self.parent().width(), 0, 300, self.parent().height()))
        self.anim.finished.connect(self.hide)
        self.anim.start()
