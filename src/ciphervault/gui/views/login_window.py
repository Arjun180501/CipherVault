import pyotp

from PyQt6.QtWidgets import (QMainWindow, QWidget,QVBoxLayout, QComboBox, QLineEdit, QPushButton)
from PyQt6.QtGui import QPixmap, QPalette, QBrush
from PyQt6.QtCore import Qt, QTimer

from ciphervault.gui.utils.styles import LOGIN
from ciphervault.gui.widgets.blended_logo import BlendedLogo
from ciphervault.gui.views.popup_dialog import PopupDialog
from ciphervault.gui.controllers.auth import AuthController
from ciphervault.gui.utils.settings import BG_PATH, LOGO_PATH
from ciphervault.gui.utils.utils import load_vaults
from ciphervault.gui.views.totp_verify import TotpVerify

class LoginWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Login - CipherVault")
        self.resize(900, 600)

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

        # Central widget layout
        central_widget = QWidget()
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(20)
        layout.setContentsMargins(50, 20, 50, 20)

        # Logo
        blended_logo = BlendedLogo(LOGO_PATH, size=200)
        layout.addWidget(blended_logo, alignment=Qt.AlignmentFlag.AlignCenter)

        # Vault dropdown
        self.vault_combo = QComboBox()
        self.vault_combo.setStyleSheet(LOGIN["combobox"])
        self.vault_combo.setFixedWidth(300)
        self.vault_combo.addItem("Select a vault...")
        layout.addWidget(self.vault_combo, alignment=Qt.AlignmentFlag.AlignCenter)

        # Master password field
        self.password_field = QLineEdit()
        self.password_field.setPlaceholderText("Master Password")
        self.password_field.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_field.setDisabled(True)
        self.password_field.setStyleSheet(LOGIN["input"])
        self.password_field.setFixedWidth(300)
        layout.addWidget(self.password_field, alignment=Qt.AlignmentFlag.AlignCenter)

        # Login button
        login_btn = QPushButton("Login")
        login_btn.setStyleSheet(LOGIN["button"])
        login_btn.setFixedWidth(150)
        login_btn.setDefault(True)
        login_btn.clicked.connect(self.handle_login)
        self.password_field.returnPressed.connect(self.handle_login)
        layout.addWidget(login_btn, alignment=Qt.AlignmentFlag.AlignCenter)
        
        back_btn = QPushButton("Back")
        back_btn.setStyleSheet(LOGIN["button"])
        back_btn.setFixedWidth(150)
        back_btn.setDefault(True)
        back_btn.setShortcut("Escape")
        back_btn.clicked.connect(self.back_to_select)
        layout.addWidget(back_btn, alignment=Qt.AlignmentFlag.AlignCenter)
        

        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

        self.vaults_data = load_vaults()
        for vault in self.vaults_data:
            self.vault_combo.addItem(vault["name"])
        self.vault_combo.currentIndexChanged.connect(self.on_vault_selected)

        self.auth_controller = AuthController(self)
        self.active_vault = None

    def on_vault_selected(self, index):
        if index <= 0:
            self.password_field.setDisabled(True)
        else:
            self.password_field.setDisabled(False)

    def handle_login(self):
        index = self.vault_combo.currentIndex()
        if index <= 0:
            PopupDialog(
                title="Login Error",
                message="Please select a vault.",
                yes_label="OK",
                parent=self
            ).exec()
            return
        

        self.selected_vault = self.vaults_data[index - 1]
        master_password = self.password_field.text()

        success, message, vault_obj = self.auth_controller.authenticate_user(
            self.selected_vault,
            master_password
        )

        if success:
            self.active_vault = vault_obj
            
            totp_flag = self.auth_controller.check_mfa_status(self.active_vault)
            if totp_flag:
                dialog = TotpVerify(parent=self)
                if dialog.exec():
                    totp_code = dialog.get_code()
                    totp = pyotp.TOTP(self.active_vault.get_config("totp_secret"))
                    if not totp.verify(totp_code.strip()):
                        PopupDialog(
                            title="Login Failed",
                            message="Invalid TOTP code. Access denied.",
                            yes_label="OK",
                            parent=self,
                        ).exec()
                        return
                else:
                    PopupDialog(
                        title="Login Failed",
                        message="TOTP code is required.",
                        yes_label="OK",
                        parent=self,
                    ).exec()
                    return

            PopupDialog(
                title="Vault Unlocked",
                message=f"Vault '{self.selected_vault['name']}' unlocked!",
                yes_label="Continue",
                parent=self
            ).exec()

            self.close()
            self.go_to_dashboard()
        else:
            PopupDialog(
                title="Login Failed",
                message=message,
                yes_label="OK",
                parent=self
            ).exec()

    def back_to_select(self):
        from ciphervault.gui.views.select_window import VaultSelectWindow
        self.select_window = VaultSelectWindow()
        self.select_window.show()
        self.close()

    def go_to_dashboard(self):
        from ciphervault.gui.views.main_window import MainWindow
        self.main_window = MainWindow(controller=self.active_vault, vaultname = self.selected_vault['name'])
        self.main_window.show()

    def show_no_vaults_dialog(self):
        dialog = PopupDialog(
            title="No Vaults Found",
            message="No vaults configured yet.\n\nWould you like to create one?",
            yes_label="Yes",
            no_label="No",
            parent=self
        )
        result = dialog.exec()
        if result == PopupDialog.DialogCode.Accepted:
            QTimer.singleShot(0, self.go_to_init)
        else:
            QTimer.singleShot(0, self.back_to_select)
    
    def go_to_init(self):
        from ciphervault.gui.views.init_window import InitWindow
        self.init_window = InitWindow()
        self.init_window.show()
