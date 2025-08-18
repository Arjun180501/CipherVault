import pyotp
import qrcode
from PIL import Image, ImageQt
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton, QLineEdit
from PyQt6.QtGui import QPixmap, QPalette, QBrush
from PyQt6.QtCore import Qt

from ciphervault.gui.utils.styles import ENTRY_DIALOG
from ciphervault.gui.utils.settings import BG_PATH

class TOTPDialog(QDialog):
    def __init__(self, vault_name, parent=None):
        super().__init__(parent)
        self.setModal(True)
        self.setWindowTitle("MFA Setup")
        self.success = False
        self.secret = None

        # Background
        self.setStyleSheet(ENTRY_DIALOG["dialog"])
        self.setMinimumWidth(500)
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
        layout.setSpacing(15)

        # Instructions
        instruction_label = QLabel(
            "Scan this QR code with your authenticator app (e.g. Google Authenticator, Authy). "
            "Then enter the 6-digit code generated to complete setup."
        )
        instruction_label.setStyleSheet("""
            color: #FFFFFF;
            font-size: 14px;
            margin-bottom: 10px;
        """)
        instruction_label.setWordWrap(True)
        layout.addWidget(instruction_label)

        # Generate QR code
        self.secret = pyotp.random_base32()
        uri = f"otpauth://totp/{vault_name}?secret={self.secret}&issuer=CipherVault"

        qr_img = qrcode.make(uri)
        if not isinstance(qr_img, Image.Image):
            qr_img = qr_img.get_image()

        qt_img = ImageQt.ImageQt(qr_img)
        pixmap = QPixmap.fromImage(qt_img)

        qr_label = QLabel()
        qr_label.setPixmap(pixmap.scaled(250, 250, Qt.AspectRatioMode.KeepAspectRatio))
        qr_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(qr_label)

        # Secret key display
        secret_label = QLabel(f"Secret Key: {self.secret}")
        secret_label.setStyleSheet("color: #FF6D00; font-size: 14px;")
        secret_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(secret_label)

        # Code input
        self.input_code = QLineEdit()
        self.input_code.setPlaceholderText("Enter 6-digit code")
        self.input_code.setStyleSheet(ENTRY_DIALOG["button"])
        self.input_code.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.input_code)

        # Verify button
        verify_btn = QPushButton("Verify and Continue")
        verify_btn.setStyleSheet(ENTRY_DIALOG["button"])
        verify_btn.clicked.connect(self.verify_code)
        layout.addWidget(verify_btn)

        self.setLayout(layout)

    def verify_code(self):
        entered_code = self.input_code.text().strip()
        totp = pyotp.TOTP(self.secret)
        if totp.verify(entered_code):
            self.success = True
            self.accept()
        else:
            error = QLabel("Invalid code. Please try again.")
            error.setStyleSheet("color: #FF6D00; font-size: 14px;")
            self.layout().addWidget(error)
