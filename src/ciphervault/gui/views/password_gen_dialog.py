from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QSpinBox, QCheckBox, QPushButton,
    QLineEdit, QLabel
)
from PyQt6.QtGui import QPixmap, QPalette, QBrush
from PyQt6.QtCore import Qt

from ciphervault.core.utils import generate_strong_password
from ciphervault.gui.utils.settings import BG_PATH, LOGO_PATH
from ciphervault.gui.utils.styles import DASHBOARD

class PasswordGeneratorDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Customize Password Generator")

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

        self.length_spin = QSpinBox()
        self.length_spin.setRange(8, 64)
        self.length_spin.setValue(16)
        self.length_spin.setMinimum(8)

        self.uppercase_cb = QCheckBox("Include uppercase")
        self.uppercase_cb.setChecked(True)
        self.digits_cb = QCheckBox("Include digits")
        self.digits_cb.setChecked(True)
        self.symbols_cb = QCheckBox("Include symbols")
        self.symbols_cb.setChecked(True)

        self.result_field = QLineEdit()
        self.result_field.setReadOnly(True)

        generate_btn = QPushButton("Generate")
        generate_btn.setStyleSheet(DASHBOARD['button'])
        use_btn = QPushButton("Use Password")
        use_btn.setStyleSheet(DASHBOARD['button'])
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setStyleSheet(DASHBOARD['button'])

        generate_btn.clicked.connect(self._generate)
        use_btn.clicked.connect(self.accept)
        cancel_btn.clicked.connect(self.reject)

        layout.addWidget(QLabel("Password Length:"))
        layout.addWidget(self.length_spin)
        layout.addWidget(self.uppercase_cb)
        layout.addWidget(self.digits_cb)
        layout.addWidget(self.symbols_cb)
        layout.addWidget(QLabel("Generated Password:"))
        layout.addWidget(self.result_field)

        btn_row = QHBoxLayout()
        btn_row.addWidget(generate_btn)
        btn_row.addWidget(use_btn)
        btn_row.addWidget(cancel_btn)
        layout.addLayout(btn_row)

        self.setLayout(layout)
        self._generate()

    def _generate(self):
        pwd = generate_strong_password(
            length=self.length_spin.value(),
            use_uppercase=self.uppercase_cb.isChecked(),
            use_digits=self.digits_cb.isChecked(),
            use_symbols=self.symbols_cb.isChecked()
        )
        self.result_field.setText(pwd)

    def get_password(self) -> str:
        return self.result_field.text()