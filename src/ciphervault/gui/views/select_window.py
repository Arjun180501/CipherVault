import zipfile
import os, shutil
from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QLabel, QPushButton, QFileDialog, QDialog, QListWidget,
                             QHBoxLayout, QInputDialog)
from PyQt6.QtGui import QPixmap, QPalette, QBrush, QIcon, QPainter, QColor, QKeyEvent
from PyQt6.QtSvg import QSvgRenderer
from PyQt6.QtCore import Qt, QSize
from ciphervault.gui.utils.settings import BG_PATH, LOGO_PATH, PLUS_ICON, MINUS_ICON, EXIT_ICON, EXPORT_ICON, IMPORT_ICON
from ciphervault.gui.utils.styles import SELECT
from ciphervault.gui.widgets.blended_logo import BlendedLogo
from ciphervault.core.utils import get_vaults_dir

from ciphervault.gui.views.init_window import InitWindow
from ciphervault.gui.views.login_window import LoginWindow
from ciphervault.gui.views.popup_dialog import PopupDialog
from ciphervault.gui.views.selectexport_dialog import VaultExportDialog

class VaultSelectWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("CipherVault")
        self.resize(1100, 750)

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

        # Layout
        central_widget = QWidget()
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(25)

        logo = BlendedLogo(LOGO_PATH, size=300)
        layout.addWidget(logo)

        title = QLabel("Select Vault")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("""
            color: #FFFFFF;
            font-size: 32px;
            font-weight: bold;
        """)
        layout.addWidget(title)
        
        existing_create_layout = QHBoxLayout()
        existing_create_layout.setSpacing(16)
        existing_create_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.existing_btn = QPushButton("  Existing Vault")
        self.create_btn = QPushButton("  Create New Vault")
        self.exit_btn = QPushButton(" Exit")

        self.existing_btn.setIcon(QIcon(self.svg_to_pixmap(MINUS_ICON, 24)))
        self.create_btn.setIcon(QIcon(self.svg_to_pixmap(PLUS_ICON, 24)))
        self.exit_btn.setIcon(QIcon(self.svg_to_pixmap(EXIT_ICON, 24)))
        self.existing_btn.setIconSize(QSize(24, 24))
        self.create_btn.setIconSize(QSize(24, 24))
        self.exit_btn.setIconSize(QSize(24, 24))

        self.existing_btn.setStyleSheet(SELECT["button"])
        self.create_btn.setStyleSheet(SELECT["button"])
        self.exit_btn.setStyleSheet(SELECT["button"])

        self.existing_btn.setFixedWidth(300)
        self.create_btn.setFixedWidth(300)
        self.exit_btn.setFixedWidth(300)
        
        self.existing_btn.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.create_btn.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.exit_btn.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        
        self.existing_btn.setDefault(True)
        self.create_btn.setAutoDefault(True)
        self.exit_btn.setAutoDefault(True)

        self.existing_btn.clicked.connect(self.on_existing_clicked)
        self.create_btn.clicked.connect(self.on_create_clicked)
        self.exit_btn.clicked.connect(self.on_exit_clicked)
        
        existing_create_layout.addWidget(self.existing_btn)
        existing_create_layout.addWidget(self.create_btn)
        
        export_import_layout = QHBoxLayout()
        export_import_layout.setSpacing(16)
        export_import_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.export_selected_btn = QPushButton("  Export Vaults")
        self.import_btn = QPushButton("  Import Vaults")

        for b in [self.export_selected_btn, self.import_btn]:
            b.setStyleSheet(SELECT["button"])
            b.setFixedWidth(300)
            b.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

        self.export_selected_btn.setIcon(QIcon(self.svg_to_pixmap(EXPORT_ICON, 24)))
        self.import_btn.setIcon(QIcon(self.svg_to_pixmap(IMPORT_ICON, 24)))
        self.export_selected_btn.setIconSize(QSize(24, 24))
        self.import_btn.setIconSize(QSize(24, 24))

        self.export_selected_btn.clicked.connect(self.export_selected_vaults)
        self.import_btn.clicked.connect(self.import_vaults)
        
        export_import_layout.addWidget(self.export_selected_btn)
        export_import_layout.addWidget(self.import_btn)
        

        # layout.addWidget(self.existing_btn, alignment=Qt.AlignmentFlag.AlignCenter)
        # layout.addWidget(self.create_btn, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addLayout(existing_create_layout)
        layout.addLayout(export_import_layout)
        layout.addWidget(self.exit_btn, alignment=Qt.AlignmentFlag.AlignCenter)

        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)
        
        self.existing_btn.setFocus()
        

    def svg_to_pixmap(self, svg_path, size):
        renderer = QSvgRenderer(svg_path)
        pixmap = QPixmap(size, size)
        pixmap.fill(Qt.GlobalColor.transparent)
        painter = QPainter(pixmap)
        renderer.render(painter)
        painter.end()

        # Make SVG white
        image = pixmap.toImage()
        for y in range(image.height()):
            for x in range(image.width()):
                color = image.pixelColor(x, y)
                if color.alpha() > 0:
                    image.setPixelColor(x, y, QColor(255, 255, 255, color.alpha()))
        return QPixmap.fromImage(image)

    def on_existing_clicked(self):
        from ciphervault.gui.views.vault_check import vault_check
        chk_status = vault_check.check_vault_exists(parent_window=self)
        if chk_status == 0:
            self.init_window = InitWindow()
            self.init_window.show()
            self.close()
        elif chk_status == 2:
            self.login_window = LoginWindow()
            self.login_window.show()
            self.close()

    def on_create_clicked(self):
        self.init_window = InitWindow()
        self.init_window.show()
        self.close()
    
    def on_exit_clicked(self):
        self.close()

    def keyPressEvent(self, event: QKeyEvent):
        # Optional arrow key support for selection
        if event.key() in (Qt.Key.Key_Up, Qt.Key.Key_Down):
            if self.existing_btn.hasFocus():
                self.create_btn.setFocus()
            else:
                self.existing_btn.setFocus()
        else:
            super().keyPressEvent(event)


    def export_selected_vaults(self):
        vaults_dir = get_vaults_dir()
        vault_files = [f for f in os.listdir(vaults_dir) if f.endswith('.db')]
        if not vault_files:
            PopupDialog("No Vaults", "No vaults are available for export.", parent=self).exec()
            return

        dlg = VaultExportDialog(vault_files, parent=self)
        if dlg.exec() != QDialog.DialogCode.Accepted:
            return

        selected = dlg.get_selected_vaults()
        if not selected:
            PopupDialog("No Selection", "No vaults selected.", parent=self).exec()
            return

        dest_folder = QFileDialog.getExistingDirectory(self, "Select Destination Folder")
        if not dest_folder:
            return

        zip_name, ok = QInputDialog.getText(self, "Export as ZIP", "Enter a name for the backup archive (without .zip):")
        if not ok or not zip_name.strip():
            PopupDialog("Cancelled", "Export cancelled by user.", parent=self).exec()
            return

        zip_path = os.path.join(dest_folder, zip_name.strip() + ".zip")

        try:
            exported = 0
            with zipfile.ZipFile(zip_path, 'w', compression=zipfile.ZIP_DEFLATED) as zipf:
                for vault_filename in selected:
                    source_db_path = os.path.join(vaults_dir, vault_filename)
                    source_salt_path = os.path.join(vaults_dir, vault_filename + ".salt")
                    if not os.path.exists(source_db_path):
                        PopupDialog("Error", f"Vault file not found: {source_db_path}", parent=self).exec()
                        continue
                    if not os.path.exists(source_salt_path):
                        PopupDialog("Error", f"Salt file not found: {source_salt_path}", parent=self).exec()
                        continue
                    zipf.write(source_db_path, arcname=vault_filename)
                    zipf.write(source_salt_path, arcname=vault_filename + ".salt")
                    exported += 1
            PopupDialog("Success", f"Exported {exported} vault(s) to ZIP archive:\n{zip_path}", parent=self).exec()
        except Exception as e:
            PopupDialog("Error", f"Export failed:\n{str(e)}", parent=self).exec()


    def import_vaults(self):
        from zipfile import ZipFile
        zip_path, _ = QFileDialog.getOpenFileName(self, "Select Vaults ZIP Archive", "", "Zip files (*.zip)")
        if not zip_path:
            return
    
        try:
            vaults_dir = get_vaults_dir()
            imported = 0
            with ZipFile(zip_path, 'r') as zipf:
                files_in_zip = zipf.namelist()
                db_files = [f for f in files_in_zip if f.endswith('.db')]
                salt_files = [f for f in files_in_zip if f.endswith('.salt')]
    
                if not db_files:
                    PopupDialog("No Vaults", "No vaults found in ZIP archive.", parent=self).exec()
                    return
    
                for db_file in db_files:
                    base_name = os.path.splitext(db_file)[0]
                    salt_file = base_name + ".salt"
                    if salt_file not in files_in_zip:
                        PopupDialog("Warning", f"No salt file for vault '{db_file}' in archive. Skipped.", parent=self).exec()
                        continue
                    
                    dest_db = os.path.join(vaults_dir, db_file)
                    dest_salt = os.path.join(vaults_dir, salt_file)
    
                    if os.path.exists(dest_db) or os.path.exists(dest_salt):
                        rename, ok = QInputDialog.getText(self, "File Exists",
                            f"Vault or salt file '{db_file}' exists.\nType new name to rename, or leave blank to overwrite:")
                        if ok and rename:
                            dest_db = os.path.join(vaults_dir, rename + os.path.splitext(db_file)[1])
                            dest_salt = os.path.join(vaults_dir, rename + ".salt")
                        # else: proceed to overwrite
    
                    with zipf.open(db_file) as src_db, open(dest_db, 'wb') as dst_db:
                        dst_db.write(src_db.read())
                    with zipf.open(salt_file) as src_salt, open(dest_salt, 'wb') as dst_salt:
                        dst_salt.write(src_salt.read())
                    imported += 1
    
            PopupDialog("Success", f"Imported {imported} vault(s) from ZIP archive.", parent=self).exec()
        except Exception as e:
            PopupDialog("Error", f"Import failed:\n{str(e)}", parent=self).exec()
