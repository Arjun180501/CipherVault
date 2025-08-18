from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QPushButton, QHBoxLayout, QCheckBox, QScrollArea, QWidget
)
from PyQt6.QtGui import QPixmap, QPalette, QBrush
from PyQt6.QtCore import Qt

from ciphervault.gui.utils.styles import ENTRY_DIALOG
from ciphervault.gui.utils.settings import BG_PATH, LOGO_PATH

class VaultExportDialog(QDialog):
    def __init__(self, vault_names, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Select Vaults to Export")
        self.setModal(True)
        self.setMinimumWidth(400)
        self.setStyleSheet(ENTRY_DIALOG["dialog"])

        # Brick background
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
        title_label = QLabel("Select Vaults to Export")
        title_label.setStyleSheet(ENTRY_DIALOG["title_label"])
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)

        # Scrollable list of checkboxes for vaults
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        content = QWidget()
        vbox = QVBoxLayout(content)
        self.checkboxes = []
        self.select_all_cb = QCheckBox("Select All Vaults")
        self.select_all_cb.setStyleSheet(ENTRY_DIALOG.get("checkbox", ""))
        self.select_all_cb.setChecked(False)
        self.select_all_cb.stateChanged.connect(self.toggle_all)
        vbox.addWidget(self.select_all_cb)
        for name in vault_names:
            cb = QCheckBox(name)
            cb.setStyleSheet(ENTRY_DIALOG.get("checkbox", ""))
            self.checkboxes.append(cb)
            vbox.addWidget(cb)
        content.setLayout(vbox)
        scroll.setWidget(content)
        layout.addWidget(scroll)

        # Buttons
        button_bar = QHBoxLayout()
        button_bar.setSpacing(20)

        ok_btn = QPushButton("OK")
        ok_btn.setStyleSheet(ENTRY_DIALOG["button"])
        ok_btn.clicked.connect(self.accept)
        button_bar.addWidget(ok_btn)

        cancel_btn = QPushButton("Cancel")
        cancel_btn.setStyleSheet(ENTRY_DIALOG["button"])
        cancel_btn.clicked.connect(self.reject)
        button_bar.addWidget(cancel_btn)

        layout.addLayout(button_bar)
        self.setLayout(layout)

    def get_selected_vaults(self):
        return [cb.text() for cb in self.checkboxes if cb.isChecked()]

    def toggle_all(self):
        checked = self.select_all_cb.isChecked()
        for cb in self.checkboxes:
            cb.setChecked(checked)