from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QTableView, QPushButton,
    QLineEdit, QTextEdit, QLabel, QToolBar, QSpacerItem, QSizePolicy, QHeaderView,
    QGraphicsDropShadowEffect
)
from PyQt6.QtGui import QIcon, QAction, QColor, QFontMetrics
from PyQt6.QtCore import QSize, Qt

from ciphervault.gui.models.entry_model import EntryModel
from ciphervault.gui.views.popup_dialog import PopupDialog
from ciphervault.gui.utils.qt_helpers import show_info
from ciphervault.gui.widgets.strength_meter import PasswordStrengthBar
from ciphervault.gui.views.entry_dialog import EntryDialog
from ciphervault.gui.widgets.blended_logo import BlendedLogo
from ciphervault.gui.utils.settings import PLUS_ICON, EDIT_ICON, DELETE_ICON, LOGO_PATH
from ciphervault.gui.utils.styles import DASHBOARD



class MainWindow(QMainWindow):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self._current_password = None
        self.setWindowTitle("CipherVault")
        self.resize(1100, 700)
        self._build_ui()
        self._load_entries()

    def _build_ui(self):
        whole_layout = QVBoxLayout()

        # --- Top Section ---
        top_section = QHBoxLayout()
        
        blended_logo = BlendedLogo(LOGO_PATH, size=57)
        blended_logo.setObjectName("logoDiv")
        top_section.addWidget(blended_logo)

        # logo = QLabel("🔒 CipherVault")
        blended_logo.setStyleSheet("""
            #logoDiv {
                margin-right: 50% ;
                margin-left: 30px ;   
            }
        """)
        # top_section.addWidget(logo)

        self.search = QLineEdit()
        self.search.setStyleSheet(DASHBOARD['flat_input'])
        self.search.setPlaceholderText("Search…")
        self.search.textChanged.connect(self._filter_entries)
        top_section.addWidget(self.search)

        add_btn = QPushButton("+ ADD")
        add_btn.clicked.connect(self._add_entry)
        # edit_btn = QPushButton(QIcon(EDIT_ICON), "")
        # edit_btn.clicked.connect(self._edit_entry)
        # delete_btn = QPushButton(QIcon(DELETE_ICON), "")
        # delete_btn.clicked.connect(self._delete_entry)

        # top_section.addWidget(add_btn)
        # top_section.addWidget(edit_btn)
        # top_section.addWidget(delete_btn)
        top_section.addStretch()

        whole_layout.addLayout(top_section)

        # --- Main Section ---
        main_section = QHBoxLayout()

        # --- Navigation ---
        nav_tabs = QVBoxLayout()
        nav_tabs.setSpacing(15)
        self.vault_btn = QPushButton("🔐 Vault")
        self.vault_btn.setStyleSheet(DASHBOARD["nav_tab"])
        self.vault_btn.clicked.connect(self._toggle_password_visibility)
        #vault_btn.setFlat(True)
        self.breach_btn = QPushButton("🛡️ Breach Check")
        self.breach_btn.setStyleSheet(DASHBOARD["nav_tab"])
        self.breach_btn.clicked.connect(self._toggle_password_visibility)
        #breach_btn.setFlat(True)
        nav_tabs.addWidget(self.vault_btn)
        nav_tabs.addWidget(self.breach_btn)
        nav_tabs.addStretch()

        nav_widget = QWidget()
        nav_widget.setObjectName("navbarStyle")
        nav_widget.setLayout(nav_tabs)
        nav_widget.setFixedWidth(120)
        main_section.addWidget(nav_widget)
        
        nav_widget.setStyleSheet("""
            #navbarStyle {
                background-color: #121212;
                border-right: 1px solid #333;
                padding: 10px;
                border-radius:12px;
                
            }   
        """)

        # --- Center Table ---
        self.model = EntryModel()
        self.table = QTableView()
        self.table.setModel(self.model)
        self.table.setSelectionBehavior(QTableView.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QTableView.EditTrigger.NoEditTriggers)
        self.table.verticalHeader().hide()
        self.table.clicked.connect(self._on_select_entry)
        self.table.setStyleSheet(DASHBOARD["table"])
        self.table.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        
        self.table.horizontalHeader().setStretchLastSection(True)  # ✅ allow last column to stretch
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)  # ✅ allow all columns to stretch
        
        shadow = QGraphicsDropShadowEffect(self.table)
        shadow.setBlurRadius(30)
        shadow.setXOffset(0)
        shadow.setYOffset(4)
        shadow.setColor(QColor(0, 0, 0, 160))
        self.table.setGraphicsEffect(shadow)

        table_widget = QWidget()
        table_layout = QVBoxLayout()
        table_layout.addWidget(self.table)
        table_widget.setLayout(table_layout)
        table_widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        table_layout.setContentsMargins(0, 0, 0, 0)
        table_layout.setSpacing(0)        
        
        main_section.addWidget(table_widget)

        # --- Detail Panel ---
        self.detail_panel = QWidget()
        self.detail_panel.setObjectName("detailPanel")
        detail_layout = QVBoxLayout()

        def create_row(label_text, widget):
            row = QVBoxLayout()
            row.addWidget(QLabel(label_text))
            row.addWidget(widget)
            container = QWidget()
            container.setLayout(row)
            return container

        self._edit_mode = False

        self.service_field = QLineEdit()
        self.service_field.setReadOnly(True)
        self.service_field.setStyleSheet(DASHBOARD['flat_input'])
        
        self.username_field = QLineEdit()
        self.username_field.setReadOnly(True)
        self.username_field.setStyleSheet(DASHBOARD['flat_input'])
        
        self.password_field = QLineEdit()
        self.password_field.setReadOnly(True)
        self.password_field.setStyleSheet(DASHBOARD['flat_input'])
        
        self.notes_field = QTextEdit()
        self.notes_field.setReadOnly(True)
        self.notes_field.setStyleSheet(DASHBOARD['flat_input'])

        self.toggle_pwd_btn = QPushButton("👁️")
        self.toggle_pwd_btn.setCheckable(True)
        self.toggle_pwd_btn.clicked.connect(self._toggle_password_visibility)
        self.toggle_pwd_btn.setFixedWidth(32)

        pwd_layout = QHBoxLayout()
        pwd_layout.addWidget(self.password_field)
        pwd_layout.addWidget(self.toggle_pwd_btn)
        pwd_widget = QWidget()
        pwd_widget.setLayout(pwd_layout)

        self.strength_bar = PasswordStrengthBar()
        
        self.edit_btn = QPushButton(QIcon(EDIT_ICON), "")
        self.edit_btn.clicked.connect(self._toggle_edit_mode)
        
        delete_btn = QPushButton(QIcon(DELETE_ICON), "")
        delete_btn.clicked.connect(self._delete_entry)
        

        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.hide()
        self.cancel_btn.clicked.connect(self._cancel_edit)

        btn_row = QHBoxLayout()
        btn_row.addStretch()
        btn_row.addWidget(self.cancel_btn)
        btn_row.addWidget(self.edit_btn)
        btn_row.addWidget(delete_btn)

        detail_layout.addWidget(create_row("Service", self.service_field))
        detail_layout.addWidget(create_row("Username", self.username_field))
        detail_layout.addWidget(create_row("Password", pwd_widget))
        detail_layout.addWidget(create_row("Strength", self.strength_bar))
        detail_layout.addWidget(create_row("Notes", self.notes_field))
        detail_layout.addLayout(btn_row)

        self.detail_panel.setLayout(detail_layout)
        self.detail_panel.setStyleSheet("""
            #detailPanel {
                background-color: #121212;
                border: 1px solid #333;
                border-radius: 12px;
                padding: 12px;
            }
            QLabel {
                color: #aaa;
                font-weight: 500;
            }
            QTextEdit {
                background-color: transparent;
                border: none;
                font-size: 14px;
                color: #eee;
            }
        """)

        shadow = QGraphicsDropShadowEffect(self.detail_panel)
        shadow.setBlurRadius(30)
        shadow.setXOffset(0)
        shadow.setYOffset(4)
        shadow.setColor(QColor(0, 0, 0, 160))
        self.detail_panel.setGraphicsEffect(shadow)
        self.detail_panel.hide()
        main_section.addWidget(self.detail_panel)
        
        main_section.setStretchFactor(table_widget, 1)
        main_section.setStretchFactor(self.detail_panel, 0)

        whole_layout.addLayout(main_section)

        wrapper = QWidget()
        wrapper.setLayout(whole_layout)
        self.setCentralWidget(wrapper)
        
        

    def _resize_columns_to_cell_content(self):
        font = self.table.font()
        fm = QFontMetrics(font)
        padding = 20
        for col in range(self.model.columnCount()):
            max_width = 0
            for row in range(self.model.rowCount()):
                index = self.model.index(row, col)
                text = str(self.model.data(index, Qt.ItemDataRole.DisplayRole))
                width = fm.horizontalAdvance(text)
                max_width = max(max_width, width)
            self.table.setColumnWidth(col, max_width + padding)

    def _load_entries(self):
        entries = self.controller.list_entries()
        self.model.update(entries)
        self._resize_columns_to_cell_content()
        self.statusBar().showMessage(f"{len(entries)} entries loaded.")

    def _filter_entries(self, text):
        filtered = [
            e for e in self.controller.list_entries()
            if text.lower() in e["service"].lower() or text.lower() in e["username"].lower()
        ]
        self.model.update(filtered)
        self._resize_columns_to_cell_content()

    def _selected_entry_id(self):
        sel = self.table.selectionModel().selectedRows()
        if not sel:
            return None
        entry = self.model.data(sel[0], Qt.ItemDataRole.UserRole)
        return entry["id"]

    def _add_entry(self):
        dlg = EntryDialog(title="Add Entry", message="Enter new entry details")
        if dlg.exec():
            self.controller.add_password_entry(**dlg.get_data())
            self._load_entries()
            PopupDialog("New Entry Added", "Entry added successfully.")

    def _edit_entry(self):
        eid = self._selected_entry_id()
        if eid is None:
            return
        raw = self.controller.get_entry_details(eid)
        dlg = EntryDialog(title="Edit Entry", message="Update entry", existing=raw)
        if dlg.exec():
            self.controller.update_entry(eid, **dlg.get_data())
            self._load_entries()
            show_info(self, "Updated", "Entry updated successfully.")

    def _toggle_edit_mode(self):
        self._edit_mode = not self._edit_mode

        is_editing = self._edit_mode
        self.service_field.setReadOnly(not is_editing)
        self.username_field.setReadOnly(not is_editing)
        self.password_field.setReadOnly(not is_editing)
        self.notes_field.setReadOnly(not is_editing)
        self.cancel_btn.setVisible(is_editing)

        if is_editing:
            self.edit_btn.setText("💾 Save")
        else:
            eid = self._selected_entry_id()
            if eid:
                self.controller.update_entry(
                    eid,
                    service=self.service_field.text(),
                    username=self.username_field.text(),
                    password=self.password_field.text(),
                    notes=self.notes_field.toPlainText()
                )
                show_info(self, "Updated", "Entry updated successfully.")
            self.edit_btn.setText("✏️ Edit")

    def _cancel_edit(self):
        # Restore original values
        eid = self._selected_entry_id()
        if eid:
            full_entry = self.controller.get_entry_details(eid)
            if full_entry:
                self.service_field.setText(full_entry.get("service", ""))
                self.username_field.setText(full_entry.get("username", ""))
                self.password_field.setText(full_entry.get("password", ""))
                self.notes_field.setText(full_entry.get("notes", ""))
                self.strength_bar.evaluate(full_entry.get("password", ""))

        self._edit_mode = False
        self.service_field.setReadOnly(True)
        self.username_field.setReadOnly(True)
        self.password_field.setReadOnly(True)
        self.notes_field.setReadOnly(True)
        self.edit_btn.setText("✏️ Edit")
        self.cancel_btn.hide()


    def _delete_entry(self):
        eid = self._selected_entry_id()
        if eid is None:
            return
        self.controller.delete_entry(eid)
        self._load_entries()
        self.detail_panel.hide()
        PopupDialog("Deleted", "Entry deleted.")

    def _on_select_entry(self, index):
        entry_meta = self.model.data(index, Qt.ItemDataRole.UserRole)
        if not entry_meta:
            self.detail_panel.hide()
            return
        full_entry = self.controller.get_entry_details(entry_meta["id"])
        if not full_entry:
            self.detail_panel.hide()
            return

        self._current_password = full_entry.get("password", "")
        self.service_field.setText(full_entry.get("service", ""))
        self.username_field.setText(full_entry.get("username", ""))
        self.password_field.setText("●●●●●●●●")
        self.notes_field.setText(full_entry.get("notes", ""))
        self.strength_bar.evaluate(self._current_password)
        self.toggle_pwd_btn.setChecked(False)
        self.detail_panel.show()

    def _toggle_password_visibility(self):
        if not self._current_password:
            return
        if self.toggle_pwd_btn.isChecked():
            self.password_field.setText(self._current_password)
        else:
            self.password_field.setText("●●●●●●●●")
