from PyQt6.QtWidgets import (
    QWidget, QLabel, QVBoxLayout, QHBoxLayout, QPushButton, QSlider, QCheckBox,
    QGroupBox, QLineEdit, QComboBox, QDialog, QFormLayout, QSizePolicy, QFileDialog, QInputDialog, QDialogButtonBox, QListWidgetItem, QListWidget
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap

from ciphervault.gui.utils.settings import USER_ICON
from ciphervault.gui.utils.styles import HELP
from ciphervault.gui.widgets.toggle_switch import ToggleSwitch
from ciphervault.gui.widgets.slider_fill import FilledSlider
from ciphervault.gui.views.popup_dialog import PopupDialog
from ciphervault.gui.views.change_password_dialog import ChangePasswordDialog
from ciphervault.gui.views.totp_dialog import TOTPDialog

from ciphervault.core.utils import get_vaults_dir
import os, shutil

class SettingsPage(QWidget):
    def __init__(self, controller, vaultname):
        super().__init__()
        self.controller = controller
        self.vaultname = vaultname
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        # --- Title ---
        title = QLabel("⚙️ Settings")
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: #CCCCCC; padding-bottom: 20px;")
        layout.addWidget(title)

        # --- User Profile Section ---
        username = self.controller.get_config("username")
        user_email = self.controller.get_config("email")
        layout.addWidget(self._create_user_profile_section(username, user_email))
        layout.addSpacing(15)
        layout.addStretch()

        # --- Features Section ---
        features_box = QGroupBox("Features")
        features_box.setStyleSheet("background-color: #121212 !important; border:none; color: #CCCCCC; font-weight: bold; font-size: 14px; padding: 10px 20px")
        features_layout = QVBoxLayout()

        # TOTP
        self.totp_toggle = ToggleSwitch()
        if str(self.controller.get_config("totp_enabled")).lower() == "true":
            self.totp_toggle.setChecked(True)
        else:
            self.totp_toggle.setChecked(False)
        totp_label = QLabel("Enable Two-Factor Authentication (TOTP)")
        totp_label.setStyleSheet("color: #CCCCCC; font-weight: bold; font-size: 14px")
        totp_toggle_row = QHBoxLayout()
        totp_toggle_row.addWidget(totp_label)
        totp_toggle_row.addStretch()
        totp_toggle_row.addWidget(self.totp_toggle)
        totp_toggle_row.setSpacing(25)
        features_layout.addLayout(totp_toggle_row)

        # Breach Check
        self.breach_toggle = ToggleSwitch()
        if str(self.controller.get_config("breach_chk_enabled")).lower() == "true":
            self.breach_toggle.setChecked(True)
        else:
            self.breach_toggle.setChecked(False)
        breach_label = QLabel("Enable Auto Breach Check")
        breach_label.setStyleSheet("color: #CCCCCC; font-weight: bold; font-size: 14px")
        breach_toggle_row = QHBoxLayout()
        breach_toggle_row.addWidget(breach_label)
        breach_toggle_row.addStretch()
        breach_toggle_row.addWidget(self.breach_toggle)
        breach_toggle_row.setSpacing(25)
        features_layout.addLayout(breach_toggle_row)


        # Clipboard Timer
        clip_layout = QHBoxLayout()
        clip_layout.setSpacing(25)
        clip_label = QLabel("Clipboard Timeout")
        clip_label.setStyleSheet("color: #CCCCCC; font-weight: bold; font-size: 14px")
        self.clip_slider = FilledSlider(Qt.Orientation.Horizontal)
        self.clip_slider.setRange(10, 60)
        self.clip_slider.setValue(int(self.controller.get_config("clipboard_timeout")))
        self.clip_slider.valueChanged.connect(self._on_clip_slider_changed)
        self.clip_time = QLabel(f"{self.clip_slider.value()}s")
        clip_layout.addWidget(clip_label)
        clip_layout.addWidget(self.clip_slider)
        clip_layout.addWidget(self.clip_time)
        features_layout.addLayout(clip_layout)

        # Session Timeout
        session_layout = QHBoxLayout()
        session_layout.setSpacing(25)
        session_label = QLabel("Session Timeout")
        session_label.setStyleSheet("color: #CCCCCC; font-weight: bold; font-size: 14px")
        self.session_slider = FilledSlider(Qt.Orientation.Horizontal)
        self.session_slider.setRange(5, 15)
        self.session_slider.setValue(int(self.controller.get_config("session_timeout")))
        self.session_slider.valueChanged.connect(self._on_session_slider_changed)
        self.session_time = QLabel(f"{self.session_slider.value()} m")

        session_layout.addWidget(session_label)
        session_layout.addWidget(self.session_slider)
        session_layout.addWidget(self.session_time)
        features_layout.addLayout(session_layout)

        features_box.setLayout(features_layout)
        layout.addWidget(features_box)
        layout.addStretch()

        # --- Security Section ---
        security_box = QGroupBox("Security Settings")
        security_box.setStyleSheet("background-color: #121212 !important; border: none; color: #CCCCCC; font-weight: bold; font-size: 14px; padding: 10px 20px")
        security_layout = QFormLayout()

        # Change master password
        change_pwd_btn = QPushButton("Change")
        change_pwd_btn.setStyleSheet(HELP['button'])
        change_pwd_btn.clicked.connect(self.change_password)
        change_pwd_btn.setFixedWidth(80)
        security_layout.addRow(QLabel("Change Master Password"), change_pwd_btn)

        # Encryption method dropdown
        self.encryption_dropdown = QComboBox()
        self.encryption_dropdown.addItems(["aes", "chacha", "hybrid"])
        current_method = self.controller.get_config("algorithm_mechanism")
        self.encryption_dropdown.setCurrentText(current_method)
        self.encryption_dropdown.setFixedWidth(150)
        security_layout.addRow(QLabel("Encryption Method"), self.encryption_dropdown)

        security_box.setLayout(security_layout)
        layout.addWidget(security_box)
        layout.addStretch()

        # Save Button
        save_btn = QPushButton("💾 Apply Settings")
        save_btn.setStyleSheet(HELP['button'])
        save_btn.clicked.connect(self.save_settings)
        save_btn.setFixedWidth(150)
        
        layout.addWidget(save_btn)

        self.setStyleSheet("""
            QSlider::groove:horizontal {
                height: 6px;
                border-radius: 3px;
                background: #444;
            }
            QSlider::handle:horizontal {
                background: #FF6D00;
                width: 14px;
                height: 14px;
                border-radius: 7px;
                margin: -5px 0;
            }
        """)

    def save_settings(self):
        totp_enabled_prev = self.controller.get_config("totp_enabled")
        breach_check_prev = self.controller.get_config("breach_check")
        encryption_prev = self.controller.get_config("algorithm_mechanism")

        new_settings = {
            "totp_enabled": str(self.totp_toggle.isChecked()).lower(),
            "breach_chk_enabled": str(self.breach_toggle.isChecked()).lower(),
            "clipboard_timeout": str(self.clip_slider.value()),
            "session_timeout": str(self.session_slider.value()),
            "algorithm_mechanism": str(self.encryption_dropdown.currentText()).lower()
        }

        config_keys = ["totp_enabled", "breach_chk_enabled", "clipboard_timeout", "session_timeout", "algorithm_mechanism"]

        changes = []
        for k in config_keys:
           old_val = str(self.controller.get_config(k))
           new_val = new_settings[k]
           if old_val != new_val:
               label = k.replace("_", " ").capitalize()
               if old_val in ("true", "false") or new_val in ("true", "false"):
                   old_val = "Enabled" if old_val == "true" else "Disabled"
                   new_val = "Enabled" if new_val == "true" else "Disabled"
               changes.append(f"{label}: '{old_val}' to '{new_val}'")


        encryption_changed = (encryption_prev != new_settings["algorithm_mechanism"])
        if changes:
            msg = "<br>".join(changes)
            if encryption_changed:
               msg += "<hr><b style='color:red;'>Warning:</b> Changing encryption re-encrypts all data in vault!"

            confirm = PopupDialog(
               "Confirm Settings Changes",
               f"You are about to change:<br>{msg}<br><br>Do you want to proceed?",
               yes_label="Apply", no_label="Cancel"
            )
            if confirm.exec() != PopupDialog.DialogCode.Accepted:
                if encryption_changed:
                    self.encryption_dropdown.blockSignals(True)
                    self.encryption_dropdown.setCurrentText(encryption_prev)
                    self.encryption_dropdown.blockSignals(False)
                    self.totp_toggle.setChecked(totp_enabled_prev == "true")
                    self.breach_toggle.setChecked(breach_check_prev == "true")
                    self.clip_slider.blockSignals(True)
                    self.clip_slider.setValue(int(self.controller.get_config("clipboard_timeout")))
                    self.clip_slider.blockSignals(False)
                    self.session_slider.blockSignals(True)
                    self.session_slider.setValue(int(self.controller.get_config("session_timeout")))
                    self.session_slider.blockSignals(False)
                    self.clip_time.setText(f"{self.clip_slider.value()}s")
                    self.session_time.setText(f"{self.session_slider.value()} m")
                    return
            if encryption_changed:
                self.controller.change_algorithm(new_settings["algorithm_mechanism"])
                self.encryption_dropdown.blockSignals(True)
                self.encryption_dropdown.setCurrentText(new_settings["algorithm_mechanism"])
                self.encryption_dropdown.blockSignals(False)

            if totp_enabled_prev != new_settings["totp_enabled"]:
                self.controller.update_config("totp_enabled", new_settings["totp_enabled"])
            if new_settings["totp_enabled"] == "true" and not self.controller.get_config("totp_secret"):
                self.totp_secret = None
                dialog = TOTPDialog(self.vaultname, parent=self)
                if dialog.exec():
                    if dialog.success:
                        self.totp_secret = dialog.secret
                        self.controller.update_config("totp_secret", self.totp_secret)
                    else:
                        self.controller.update_config("totp_enabled", "false")
                        self.totp_toggle.setChecked(False)
                        PopupDialog("Error", "TOTP verification failed. Vault not created.").exec()
                        return
                else:
                    self.controller.update_config("totp_enabled", "false")
                    self.totp_toggle.setChecked(False)
                    PopupDialog("Error", "TOTP setup canceled. Vault not created.").exec()
                    return

            if breach_check_prev != new_settings["breach_chk_enabled"]:
                self.controller.update_config("breach_chk_enabled", new_settings["breach_chk_enabled"])

            self.controller.update_config("session_timeout", new_settings["session_timeout"])

            self.controller.update_config("clipboard_timeout", new_settings["clipboard_timeout"])

            PopupDialog("Settings Updated", "Settings have been saved.", "OK", parent=self).exec()
        else:
            PopupDialog("Settings", "No changes found", "OK", parent=self).exec()

    def change_password(self):
        dlg = ChangePasswordDialog(self)
        if dlg.exec():
            old_pwd, new_pwd, confirm_pwd = dlg.get_passwords()

            if new_pwd != confirm_pwd:
                PopupDialog("Mismatch", "New passwords do not match.", "Retry", parent=self).exec()
                return

            if not self.controller.verify_master_password(old_pwd):
                PopupDialog("Incorrect Password", "Current password is incorrect.", "Retry", parent=self).exec()
                return

            try:
                self.controller.change_master_password(new_pwd)
                PopupDialog("Success", "Master password updated successfully.", "OK", parent=self).exec()
            except Exception as e:
                PopupDialog("Error", f"Failed to update password.\n{str(e)}", "OK", parent=self).exec()


    def _create_user_profile_section(self, username:str, user_email: str):
        container = QWidget()
        container.setStyleSheet("""
            QWidget {
                background-color: #121212 !important;
                border-radius: 12px;
            }
        """)
        container.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

        layout = QHBoxLayout()
        # Profile Icon
        icon_label = QLabel()
        pixmap = QPixmap(USER_ICON) 
        if pixmap.isNull():
            pixmap = QPixmap(100, 100)  # Fallback dummy pixmap
            pixmap.fill(Qt.GlobalColor.lightGray)

        pixmap = pixmap.scaled(80, 80, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        icon_label.setPixmap(pixmap)
        icon_label.setFixedSize(80, 80)

        # Text layout
        text_layout = QVBoxLayout()
        title_label = QLabel(f"Hi {username}")
        title_label.setStyleSheet("color: white; font-weight: bold; font-size: 14px;")

        email_label = QLabel(user_email)
        email_label.setStyleSheet("""
            QLabel {
                color: #ccc;
                font-size: 13px;
                padding: 4px 10px;
                border-radius: 8px;
            }
        """)

        text_layout.addWidget(title_label)
        text_layout.addWidget(email_label)

        layout.addWidget(icon_label)
        layout.addLayout(text_layout)
        layout.addStretch()

        container.setLayout(layout)
        return container

    def _on_clip_slider_changed(self, val):
        stepped_val = round(val / 5) * 5
        if val != stepped_val:
            self.clip_slider.blockSignals(True)
            self.clip_slider.setValue(stepped_val)
            self.clip_slider.blockSignals(False)
        self.clip_time.setText(f"{stepped_val}s")

    def _on_session_slider_changed(self, val):
        stepped_val = round(val / 5) * 5
        if val != stepped_val:
            self.session_slider.blockSignals(True)
            self.session_slider.setValue(stepped_val)
            self.session_slider.blockSignals(False)
        self.session_time.setText(f"{stepped_val} m")