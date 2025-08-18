import os
import string
import secrets

from PyQt6.QtWidgets import (QWidget, QLabel, QVBoxLayout, QLineEdit, QPushButton, QHBoxLayout, QComboBox, QCheckBox, QFileDialog, QScrollArea)
from PyQt6.QtGui import QPixmap, QGuiApplication, QPalette, QBrush
from PyQt6.QtCore import Qt

from zxcvbn import zxcvbn

from ciphervault.gui.utils.settings import LOGO_PATH, BG_PATH
from ciphervault.gui.utils.styles import INIT
from ciphervault.gui.views.popup_dialog import PopupDialog
from ciphervault.gui.views.totp_dialog import TOTPDialog
from ciphervault.gui.views.login_window import LoginWindow
from ciphervault.core.vault import PasswordVault
from ciphervault.core.utils import get_vaults_dir

class InitWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("CipherVault - Initialize New Vault")
        self.resize(900, 700)
        self.setMinimumWidth(600)

        if os.path.exists(BG_PATH):
            self.setAutoFillBackground(True)
            palette = QPalette()
            bg_pixmap = QPixmap(BG_PATH).scaled(
                self.size(),
                Qt.AspectRatioMode.IgnoreAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            palette.setBrush(QPalette.ColorRole.Window, QBrush(bg_pixmap))
            self.setPalette(palette)
        else:
            self.setStyleSheet("background-color: #000000;")

        # Create a main layout
        main_layout = QVBoxLayout()
        main_layout.setSpacing(12)
        main_layout.setContentsMargins(50, 30, 50, 30)

        # Logo
        logo_label = QLabel()
        logo_pixmap = QPixmap(LOGO_PATH).scaled(
            150, 150,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )
        logo_label.setPixmap(logo_pixmap)
        logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(logo_label)

        # Title label
        title_label = QLabel("INITIALIZE NEW VAULT")
        title_label.setStyleSheet(INIT["title_label"])
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(title_label)

        # Vault name
        self.vault_name_edit = QLineEdit()
        self.vault_name_edit.setPlaceholderText("Vault Name")
        self.vault_name_edit.setStyleSheet(INIT["input"])
        self.vault_name_edit.setFocus()
        self.vault_name_edit.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        main_layout.addWidget(self.vault_name_edit)
        

        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("Username")
        self.name_edit.setStyleSheet(INIT["input"])
        self.name_edit.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        main_layout.addWidget(self.name_edit)

        # User Email
        self.email_edit = QLineEdit()
        self.email_edit.setPlaceholderText("Email Address")
        self.email_edit.setStyleSheet(INIT["input"])
        self.email_edit.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        main_layout.addWidget(self.email_edit)

        # Password + Generate button
        pw_layout = QHBoxLayout()
        self.password_edit = QLineEdit()
        self.password_edit.setPlaceholderText("Set Master Password")
        self.password_edit.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_edit.setStyleSheet(INIT["input"])
        self.password_edit.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        pw_layout.addWidget(self.password_edit)

        self.generate_button = QPushButton("Generate Password")
        self.generate_button.setStyleSheet(INIT["button"])
        self.generate_button.clicked.connect(self.generate_password)
        pw_layout.addWidget(self.generate_button)
        main_layout.addLayout(pw_layout)

        # Dynamic guidelines or strength
        self.dynamic_area_layout = QVBoxLayout()
        self.dynamic_area_widget = QWidget()
        self.dynamic_area_widget.setLayout(self.dynamic_area_layout)
        main_layout.addWidget(self.dynamic_area_widget)
        self.current_dynamic_widget = None

        # Create both pages
        self.guidelines_page = self.create_guidelines_page()
        self.strength_page = self.create_strength_page()

        self.show_dynamic_widget(None)

        # Confirm password
        self.confirm_edit = QLineEdit()
        self.confirm_edit.setPlaceholderText("Confirm Password")
        self.confirm_edit.setEchoMode(QLineEdit.EchoMode.Password)
        self.confirm_edit.setStyleSheet(INIT["input"])
        self.confirm_edit.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        main_layout.addWidget(self.confirm_edit)

        algo_label = QLabel(
            "<b>Encryption algorithms:</b><br>"
            "• Hybrid (recommended): Automatically selects the most secure algorithm [AES/CHACHA20] for your device.<br>"
            "• <a href='https://en.wikipedia.org/wiki/Advanced_Encryption_Standard'>AES</a>: Standard, fast, hardware supported.<br>"
            "• <a href='https://en.wikipedia.org/wiki/ChaCha20-Poly1305'>ChaCha</a>: Faster in software, no hardware dependency.<br>"
            "<br>Click on Links to learn more about the encryption algorithms.<br>"
            "<br><i>Hybrid is recommended for maximum security and compatibility.</i>"
        )
        algo_label.setOpenExternalLinks(True)
        algo_label.setStyleSheet("color: #FF6D00; font-size: 14px; margin-bottom:8px;")
        main_layout.addWidget(algo_label)

        # Encryption combo box
        self.encryption_combo = QComboBox()
        self.encryption_combo.addItems(["hybrid", "aes", "chacha"])
        self.encryption_combo.setStyleSheet(INIT["combobox"])
        self.encryption_combo.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.encryption_combo.setToolTip(    
            "<b>Encryption algorithms:</b>\n"
            "<b>AES: Standard, fast, hardware supported</b>\n"
            "<b>ChaCha: Faster, no hardware dependency</b>\n"
            "<b>Hybrid: Auto Selects depending on device capabilities</b>"
        )
        self.encryption_combo.setPlaceholderText("Encryption Algorithm")
        main_layout.addWidget(self.encryption_combo)

        # TOTP checkbox
        self.totp_checkbox = QCheckBox("Enable Two-Factor Authentication (TOTP)")
        self.totp_checkbox.setStyleSheet(INIT["checkbox"])
        self.totp_checkbox.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        main_layout.addWidget(self.totp_checkbox)

        # Create vault button
        self.create_button = QPushButton("Create Vault")
        self.create_button.setStyleSheet(INIT["button"])
        self.create_button.setFixedWidth(200)
        self.create_button.clicked.connect(self.create_vault)
        self.create_button.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        main_layout.addWidget(self.create_button, alignment=Qt.AlignmentFlag.AlignCenter)
        
        # Go back to select window
        back_btn = QPushButton("Back")
        back_btn.setStyleSheet(INIT["button"])
        back_btn.setFixedWidth(150)
        back_btn.setDefault(True)
        back_btn.setShortcut("Escape")
        back_btn.clicked.connect(self.back_to_select)
        main_layout.addWidget(back_btn, alignment=Qt.AlignmentFlag.AlignCenter)

        main_layout.addStretch()
        
        # Keyboard supported to move around
        self.vault_name_edit.returnPressed.connect(self.name_edit.setFocus)
        self.name_edit.returnPressed.connect(self.email_edit.setFocus)
        self.email_edit.returnPressed.connect(self.password_edit.setFocus)
        self.password_edit.returnPressed.connect(self.confirm_edit.setFocus)
        self.confirm_edit.returnPressed.connect(self.encryption_combo.setFocus)

        # Wrap the entire UI in a scroll area
        container = QWidget()
        container.setLayout(main_layout)
        container.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        container.setStyleSheet("background: transparent;")

        scroll = QScrollArea()
        scroll.setWidget(container)
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QScrollArea.Shape.NoFrame)
        scroll.setStyleSheet("background: transparent;")

        window_layout = QVBoxLayout(self)
        window_layout.addWidget(scroll)

        # Connect password changes
        self.password_edit.textChanged.connect(self.validate_password)

    def create_guidelines_page(self):
        page = QWidget()
        layout = QVBoxLayout()
        layout.setSpacing(4)

        header = QLabel("Password Guidelines:")
        header.setStyleSheet("""
            color: #FF6D00;
            font-weight: bold;
            font-size: 15px;
        """)
        layout.addWidget(header)

        self.guideline_texts = [
            "at least 8 characters",
            "at least one uppercase letter",
            "at least one lowercase letter",
            "at least one numeral character",
            "at least one special character",
            "not a common password",
        ]

        self.guideline_labels = []
        for text in self.guideline_texts:
            label = QLabel(f"❌ {text}")
            label.setStyleSheet("""
                color: #FF4C4C;
                font-size: 13px;
            """)
            layout.addWidget(label)
            self.guideline_labels.append((text, label))

        page.setLayout(layout)
        return page

    def create_strength_page(self):
        page = QWidget()
        layout = QVBoxLayout()
        self.strength_label = QLabel("")
        self.strength_label.setStyleSheet("""
            color: #FF6D00;
            font-weight: bold;
            font-size: 15px;
        """)
        layout.addWidget(self.strength_label)
        page.setLayout(layout)
        return page

    def show_dynamic_widget(self, widget):
        if self.current_dynamic_widget:
            self.dynamic_area_layout.removeWidget(self.current_dynamic_widget)
            self.current_dynamic_widget.setParent(None)
            self.current_dynamic_widget.hide()
            self.current_dynamic_widget = None

        if widget:
            self.dynamic_area_layout.addWidget(widget)
            widget.show()
            self.current_dynamic_widget = widget

    def validate_password(self):
        pwd = self.password_edit.text()

        if not pwd:
            self.show_dynamic_widget(None)
            return

        result = zxcvbn(pwd) if pwd else None
        is_not_common = result and result["score"] >= 2

        rules = [
            (lambda s: len(s) >= 8, "at least 8 characters"),
            (lambda s: any(c.isupper() for c in s), "at least one uppercase letter"),
            (lambda s: any(c.islower() for c in s), "at least one lowercase letter"),
            (lambda s: any(c.isdigit() for c in s), "at least one numeral character"),
            (lambda s: any(c in string.punctuation for c in s), "at least one special character"),
            (lambda s: is_not_common if s else False, "not a common password"),
        ]

        all_good = True
        for (rule_fn, text), (_, label) in zip(rules, self.guideline_labels):
            passed = rule_fn(pwd)
            label.setText(("✅ " if passed else "❌ ") + text)
            label.setStyleSheet(
                f"color: {'#00FF62' if passed else '#FF4C4C'}; font-size: 13px;"
            )
            if not passed:
                all_good = False

        if all_good:
            score = result["score"] if result else 0
            levels = ["Very Weak", "Weak", "Fair", "Good", "Strong"]
            self.strength_label.setText(f"Password Strength: {levels[score]}")
            self.show_dynamic_widget(self.strength_page)
        else:
            self.show_dynamic_widget(self.guidelines_page)

    def generate_password(self):
        alphabet = string.ascii_letters + string.digits + string.punctuation
        pwd = "".join(secrets.choice(alphabet) for _ in range(16))
        self.password_edit.setText(pwd)
        self.confirm_edit.setText(pwd)
        clipboard = QGuiApplication.clipboard()
        clipboard.setText(pwd)

    def create_vault(self):
        vault_name = self.vault_name_edit.text().strip()
        username = self.name_edit.text().strip()
        email = self.email_edit.text().strip()
        password = self.password_edit.text()
        confirm = self.confirm_edit.text()
        encryption_mode = self.encryption_combo.currentText().lower()

        if not vault_name:
            PopupDialog("Error", "Vault name cannot be empty.").exec()
            return

        if not username:
            PopupDialog("Error", "Username cannot be empty.").exec()
            return
        
        if not email:
            PopupDialog("Error", "Email ID cannot be empty").exec()
            return

        if password != confirm:
            PopupDialog("Error", "Passwords do not match.").exec()
            return

        if len(password) < 8:
            PopupDialog("Error", "Password should be at least 8 characters.").exec()
            return

        db_path = os.path.join(get_vaults_dir(), f"{vault_name}.db")

        # TOTP handling
        self.totp_secret = None
        if self.totp_checkbox.isChecked():
            dialog = TOTPDialog(vault_name, parent=self)
            if dialog.exec():
                if dialog.success:
                    self.totp_secret = dialog.secret
                else:
                    PopupDialog("Error", "TOTP verification failed. Vault not created.").exec()
                    return
            else:
                PopupDialog("Error", "TOTP setup canceled. Vault not created.").exec()
                return

        try:
            vault = PasswordVault(password, db_path=db_path)
            vault.db.set_config("vault_name", vault_name)
            vault.db.set_config("encryption_mode", encryption_mode)
            vault.db.set_config("username", username)
            vault.db.set_config("email", email)
            vault.db.set_config("clipboard_timeout", "30")
            vault.db.set_config("session_timeout", "5")
            vault.db.set_config("breach_chk_enabled", "true")
            if self.totp_secret:
                vault.db.set_config("totp_secret", self.totp_secret)
                vault.db.set_config("totp_enabled", "true")
            else:
                vault.db.set_config("totp_enabled", "false")

            PopupDialog("Success", f"Vault '{vault_name}' created successfully!").exec()
            self.create_button.setFocus()

            # Navigate to login window
            self.login_window = LoginWindow()
            self.login_window.show()
            self.close()

        except Exception as e:
            PopupDialog("Error", f"Vault creation failed:\n{str(e)}").exec()

    def back_to_select(self):
        self.close()
        from ciphervault.gui.views.select_window import VaultSelectWindow
        self.select_window = VaultSelectWindow()
        self.select_window.show()