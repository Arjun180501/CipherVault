from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QTableView, QPushButton,
    QLineEdit, QTextEdit, QLabel, QSizePolicy, QHeaderView,
    QGraphicsDropShadowEffect, QStackedWidget, QButtonGroup, QMenu
)
from PyQt6.QtGui import QIcon, QColor, QFontMetrics, QPalette, QPixmap, QBrush, QAction
from PyQt6.QtCore import Qt, QPoint, QTimer, QEvent

from ciphervault.gui.views.select_window import VaultSelectWindow
from ciphervault.gui.models.entry_model import EntryModel
from ciphervault.gui.views.popup_dialog import PopupDialog
from ciphervault.gui.widgets.strength_meter import PasswordStrengthBar
from ciphervault.gui.views.entry_dialog import EntryDialog
from ciphervault.gui.widgets.blended_logo import BlendedLogo
from ciphervault.gui.utils.settings import LOGO_PATH, BG_PATH
from ciphervault.gui.utils.styles import DASHBOARD, BREACH_TAB

from ciphervault.core.utils import copy_clipboard
from ciphervault.gui.views.password_gen_dialog import PasswordGeneratorDialog
from ciphervault.core.utils import generate_strong_password

from ciphervault.core.utils import is_password_breached, get_last_checked_timestamp, is_connected_to_internet
from ciphervault.gui.models.breach_model import BreachModel

from ciphervault.gui.views.help_window import HelpOverlay, SlideHelpPanel
from ciphervault.gui.views.settings_window import SettingsPage

class MainWindow(QMainWindow):
    def __init__(self, controller, vaultname):
        super().__init__()
        self.controller = controller
        self.vaultname = vaultname
        self._current_password = None
        self._password_visible = False
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
        self.setWindowTitle("CipherVault")
        self.resize(1100, 700)
        self._build_ui()
        self._load_entries()
        auto_breach_chk_enabled = self.controller.get_config("breach_chk_enabled")
        if auto_breach_chk_enabled:
            self._check_all_breaches()

    def _build_ui(self):
        whole_layout = QVBoxLayout()

        # --- Top Section ---
        top_section = QHBoxLayout()
        top_section.setContentsMargins(30, 10, 30, 0)
        blended_logo = BlendedLogo(LOGO_PATH, size=90)
        blended_logo.setObjectName("logoDiv")
        blended_logo.setStyleSheet("""
            #logoDiv {
                margin-right: 40% ;
                margin-left: 10px ;   
            }
        """)
        top_section.addWidget(blended_logo)

        self.search = QLineEdit()
        self.search.setStyleSheet(DASHBOARD['searchbar'])
        self.search.setPlaceholderText("Search…")
        self.search.setToolTip("<b>Filter Entries by Service/Username</b>")
        self.search.textChanged.connect(self._filter_entries)
        top_section.addWidget(self.search)

        self.add_btn = QPushButton("✚ ADD")
        self.add_btn.setStyleSheet(DASHBOARD["add_button"])
        self.add_btn.setToolTip("<b>Add New Entry</b>")
        self.add_btn.clicked.connect(self._add_entry)
        top_section.addStretch()
        top_section.addWidget(self.add_btn)

        whole_layout.addLayout(top_section)

        # --- Main Section ---
        main_page_content = QWidget()
        main_section = QHBoxLayout()

        # --- Center Table ---
        self.model = EntryModel()
        self.table = QTableView()
        self.table.setModel(self.model)
        self.table.setSelectionBehavior(QTableView.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QTableView.SelectionMode.SingleSelection)
        self.table.setFocusPolicy(Qt.FocusPolicy.StrongFocus)   
        self.table.setEditTriggers(QTableView.EditTrigger.NoEditTriggers)
        self.table.setSortingEnabled(True)
        self.table.verticalHeader().hide()
        self.table.clicked.connect(self._on_select_entry)
        self.table.setStyleSheet(DASHBOARD["table"])
        self.table.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.table.horizontalHeader().setStretchLastSection(True)  # allow last column to stretch
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)  # allow all columns to stretch
        
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
        self.toggle_pwd_btn.setStyleSheet(DASHBOARD['button'])
        self.toggle_pwd_btn.setToolTip("<b>Toggle password visibility</b>")
        self.toggle_pwd_btn.clicked.connect(self._toggle_password_visibility)

        self.generate_btn = QPushButton("Auto Generate")
        self.generate_btn.setStyleSheet(DASHBOARD['button'])
        self.generate_btn.setToolTip("<b>Generate secure password</b>")
        self.generate_btn.clicked.connect(self._generate_quick_password)
        
        self.customize_btn = QPushButton("Custom Generate")
        self.customize_btn.setStyleSheet(DASHBOARD['button'])
        self.customize_btn.setToolTip("<b>Customize password generation</b>")
        self.customize_btn.clicked.connect(self._customize_password)
        
        self.pwd_tool_btns = QWidget()
        tool_layout = QHBoxLayout()
        tool_layout.setContentsMargins(0, 0, 0, 0)
        tool_layout.setSpacing(2)
        tool_layout.addWidget(self.generate_btn)
        tool_layout.addWidget(self.customize_btn)
        self.pwd_tool_btns.setLayout(tool_layout)
        self.pwd_tool_btns.hide()
        
        pwd_layout = QHBoxLayout()
        pwd_layout.addWidget(self.password_field)
        pwd_layout.addWidget(self.toggle_pwd_btn)
        pwd_layout.addWidget(self.pwd_tool_btns)
        pwd_widget = QWidget()
        pwd_widget.setLayout(pwd_layout)

        self.strength_bar = PasswordStrengthBar()
        
        self.edit_btn = QPushButton("EDIT")
        self.edit_btn.setStyleSheet(DASHBOARD['button'])
        self.edit_btn.setToolTip("<b>Edit Entry</b>")
        self.edit_btn.clicked.connect(self._toggle_edit_mode)
        
        self.delete_btn = QPushButton("DELETE")
        self.delete_btn.setStyleSheet(DASHBOARD['button'])
        self.delete_btn.setToolTip("<b>Delete Entry</b>")
        self.delete_btn.clicked.connect(self._delete_entry)
        

        self.cancel_btn = QPushButton("CANCEL")
        self.cancel_btn.setStyleSheet(DASHBOARD['button'])
        self.cancel_btn.setToolTip("<b>Cancel Editing</b>")
        self.cancel_btn.hide()
        self.cancel_btn.clicked.connect(self._cancel_edit)

        self.copy_btn = QPushButton("COPY PASSWORD")
        self.copy_btn.setStyleSheet(DASHBOARD['button'])
        self.copy_btn.setToolTip("<b>Copy Password to Clipboard</b>")
        self.copy_btn.clicked.connect(self._copy_password_to_clipboard)

        btn_row = QHBoxLayout()
        btn_row.addStretch()
        btn_row.addWidget(self.copy_btn)
        btn_row.addWidget(self.cancel_btn)
        btn_row.addWidget(self.edit_btn)
        btn_row.addWidget(self.delete_btn)

        self.close_btn = QPushButton("❌")
        self.close_btn.setStyleSheet(DASHBOARD['close_button'])
        self.close_btn.setToolTip("<b>Close Entry Details</b>")
        self.close_btn.clicked.connect(lambda: self.detail_panel.hide())

        # Align it to the right
        close_layout = QHBoxLayout()
        close_layout.addStretch()
        close_layout.addWidget(self.close_btn)

        detail_layout.addLayout(close_layout)
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
        
        main_page_content.setLayout(main_section)
        
        # Breach page content
        
        self.breach_model = BreachModel()
        self.breach_table = QTableView()
        self.breach_table.setModel(self.breach_model)
        self.breach_table.horizontalHeader().setStretchLastSection(True)
        self.breach_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.breach_table.setSelectionBehavior(QTableView.SelectionBehavior.SelectRows)
        self.breach_table.setSelectionMode(QTableView.SelectionMode.SingleSelection)
        self.breach_table.setFocusPolicy(Qt.FocusPolicy.StrongFocus)  
        self.breach_table.setEditTriggers(QTableView.EditTrigger.NoEditTriggers)
        self.breach_table.verticalHeader().hide()
        self.breach_table.setSortingEnabled(True)
        self.breach_table.setStyleSheet(DASHBOARD["table"])
        self.breach_table.setCursor(Qt.CursorShape.PointingHandCursor)
        self.breach_table.clicked.connect(self._on_breach_table_clicked)

        self.last_breach_check = QLabel("Last Checked: Not yet scanned")
        self.last_breach_check.setStyleSheet("color: #ccc; padding: 4px 0; font-size: 14px;")

        self.breach_info = QLabel("Password Breaches checked using Have I Been Pwned Database")
        self.breach_info.setStyleSheet("color: #888; font-size: 14px; font-weight: bold;padding-bottom: 10px;")
        
        self.recheck_btn = QPushButton("Check Breach Status")
        self.recheck_btn.setFixedWidth(180)
        self.recheck_btn.setStyleSheet(BREACH_TAB['button'])
        self.recheck_btn.setToolTip("<b>Manually recheck all passwords against breaches</b>")
        self.recheck_btn.clicked.connect(self._check_all_breaches)

        self.status_filter_mode = None  # None = all, True = breached, False = safe
        self.breach_table.horizontalHeader().sectionClicked.connect(self._on_breach_column_clicked)

        self.breach_placeholder = QLabel("Connect to the internet to check for breaches.")
        self.breach_placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.breach_placeholder.setStyleSheet("color: #888; font-size: 18px; font-style: italic;")
        self.breach_placeholder.hide()  # Hide by default

        self.breach_stack = QStackedWidget()
        self.breach_stack.addWidget(self.breach_table)
        self.breach_stack.addWidget(self.breach_placeholder)
        
        breach_layout = QVBoxLayout()
        breach_layout.addWidget(self.breach_info)
        breach_layout.addWidget(self.last_breach_check)
        breach_layout.addWidget(self.recheck_btn)
        breach_layout.addWidget(self.breach_stack)


        breach_page_content = QWidget()
        breach_page_content.setLayout(breach_layout)
        
        # Profile page
        self.profile_page = SettingsPage(self.controller, self.vaultname)

        # --- Stacked Pages ---
        self.stacked_pages = QStackedWidget()
        self.stacked_pages.addWidget(main_page_content)
        self.stacked_pages.addWidget(breach_page_content)
        self.stacked_pages.addWidget(self.profile_page)
        
        # --- Navigation ---
        nav_tabs = QVBoxLayout()
        #nav_tabs.setContentsMargins(0, 30, 0, 0)  # top spacing under logo
        nav_tabs.setSpacing(20)
        self.vault_btn = QPushButton("Vault")
        self.vault_btn.setStyleSheet(DASHBOARD["nav_tab"])
        self.vault_btn.setToolTip("<b>Password List</b>")
        
        self.breach_btn = QPushButton("Breach Check")
        self.breach_btn.setStyleSheet(DASHBOARD["nav_tab"])
        self.breach_btn.setToolTip("<b>Password Breach Status</b>")
        
        
        self.profile_btn = QPushButton("Settings")
        self.profile_btn.setStyleSheet(DASHBOARD["nav_tab"])
        self.profile_btn.setToolTip("<b>Manage Profile & Settings</b>")
        
        version_label = QLabel("CipherVault v1.0.0")
        version_label.setStyleSheet("color: #777; font-size: 12px;")
        version_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        help_btn = QPushButton("Help")
        help_btn.setStyleSheet(DASHBOARD["nav_tab"])
        help_btn.setToolTip("How to use CipherVault")
        help_btn.clicked.connect(self._show_help)
        
        self.logout_btn = QPushButton("Logout")
        self.logout_btn.setStyleSheet(DASHBOARD["nav_tab"])
        self.logout_btn.setToolTip("Exit to Vault Selection")
        self.logout_btn.clicked.connect(self._logout)
        
        # Make buttons checkable for toggle effect
        self.vault_btn.setCheckable(True)
        self.breach_btn.setCheckable(True)
        self.profile_btn.setCheckable(True)
        
        # Add to button group
        self.nav_group = QButtonGroup(self)
        self.nav_group.setExclusive(True)
        self.nav_group.addButton(self.vault_btn, 0)
        self.nav_group.addButton(self.breach_btn, 1)
        self.nav_group.addButton(self.profile_btn, 2)

        # Connect signal to switch tab
        self.nav_group.idClicked.connect(self._switch_tab)
        
        # Apply initial state
        self.vault_btn.setChecked(True)
        self._switch_tab(0)  # Default page
        
        nav_tabs.addWidget(self.vault_btn)
        nav_tabs.addWidget(self.breach_btn)
        nav_tabs.addWidget(version_label)
        nav_tabs.addWidget(self.profile_btn)
        nav_tabs.addWidget(help_btn)
        nav_tabs.addWidget(self.logout_btn)

        nav_widget = QWidget()
        nav_widget.setObjectName("navbarStyle")
        nav_widget.setFixedHeight(300)
        nav_widget.setFixedWidth(200)
        nav_widget.setLayout(nav_tabs)
        main_section.addWidget(nav_widget)
        
        nav_widget.setStyleSheet("""
            #navbarStyle {
                background-color: #121212;
                border-right: 1px solid #333;
                padding: 10px;
                border-radius:12px;
            }   
        """)
        
        # --- Combine Sidebar and Stacked Pages ---
        nav_wrapper_layout = QVBoxLayout()
        nav_wrapper_layout.addStretch()
        nav_wrapper_layout.addWidget(nav_widget, alignment=Qt.AlignmentFlag.AlignHCenter)
        nav_wrapper_layout.addStretch()

        nav_wrapper = QWidget()
        nav_wrapper.setLayout(nav_wrapper_layout)
        
        body_layout = QHBoxLayout() 
        body_layout.addWidget(nav_wrapper)
        body_layout.addWidget(self.stacked_pages)

        whole_layout.addLayout(body_layout)

        wrapper = QWidget()
        wrapper.setLayout(whole_layout)
        self.setCentralWidget(wrapper)
        
        # Session timeout (in minutes)
        self.session_timeout_minutes = int(self.controller.get_config("session_timeout"))
        self.session_timer = QTimer()
        self.session_timer.setInterval(self.session_timeout_minutes * 60 * 1000)
        self.session_timer.timeout.connect(self._on_session_timeout)
        self.session_timer.start()
        # Capture user events to reset timer
        self.installEventFilter(self)
        
        
    def _switch_tab(self, index: int):
        self.stacked_pages.setCurrentIndex(index)
        self.add_btn.setVisible(index == 0)
        if index == 0:
            self.table.setFocus()
        elif index == 1:
            self.breach_table.setFocus()
        elif index == 2:
            self.profile_page.setFocus()

        for i, btn in enumerate([self.vault_btn, self.breach_btn, self.profile_btn]):
            if i == index:
                btn.setStyleSheet(DASHBOARD["nav_tab_active"])
            else:
                btn.setStyleSheet(DASHBOARD["nav_tab"])

    def _copy_password_to_clipboard(self):
        clipboard_timeout = int(self.controller.get_config("clipboard_timeout"))
        if self._current_password:
            copy_clipboard(self._current_password, clipboard_timeout)
            PopupDialog("Copied", f"Password copied to clipboard. It will disappear in {clipboard_timeout} seconds.").exec()
    
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
        self.model.update(entries, store_all=True)
        self._resize_columns_to_cell_content()
        self.statusBar().showMessage(f"{len(entries)} entries loaded.")

    def _filter_entries(self, text):
        if self.stacked_pages.currentIndex() == 0:
            self._filter_vault_entries(text)
        else:
            self._filter_breach_entries(text)

    def _filter_vault_entries(self, text):
        if not hasattr(self.model, "all_entries"):
            return

        filtered = [
            e for e in self.model.all_entries
            if text.lower() in e["service"].lower() or text.lower() in e["username"].lower()
        ]
        self.model.update(filtered, store_all=False)
        self._resize_columns_to_cell_content()

    def _filter_breach_entries(self, text):
        if not hasattr(self.breach_model, "all_entries"):
            return  # Skip if no breach data

        filtered = []
        for entry in self.breach_model.all_entries:
            if text.lower() in entry["service"].lower() or text.lower() in entry["username"].lower():
                if self.status_filter_mode is None:
                    filtered.append(entry)
                elif self.status_filter_mode is True and entry["breached"]:
                    filtered.append(entry)
                elif self.status_filter_mode is False and not entry["breached"]:
                    filtered.append(entry)

        self.breach_model.update(filtered, store_all=False)

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

    def _toggle_edit_mode(self):
        self._edit_mode = not self._edit_mode

        is_editing = self._edit_mode
        self.service_field.setReadOnly(not is_editing)
        self.username_field.setReadOnly(not is_editing)
        self.password_field.setReadOnly(not is_editing)
        self.notes_field.setReadOnly(not is_editing)
        self.cancel_btn.setVisible(is_editing)
        self.pwd_tool_btns.setVisible(is_editing)

        if is_editing:
            self.edit_btn.setText("Save")
            self._password_visible = True
            self._update_password_field()
            self.password_field.setFocus()
        else:
            eid = self._selected_entry_id()
            if eid:
                password_input = self.password_field.text()
                if password_input == "●●●●●●●●":
                    password_input = self._current_password
                self.controller.update_entry(
                    eid,
                    service=self.service_field.text(),
                    username=self.username_field.text(),
                    password=password_input,
                    notes=self.notes_field.toPlainText()
                )
                PopupDialog("Updated", "Entry updated successfully.")
                self._load_entries()
                index = self.model.index(0, 0)
                for row in range(self.model.rowCount()):
                    entry = self.model.data(self.model.index(row, 0), Qt.ItemDataRole.UserRole)
                    if entry and entry["id"] == eid:
                        index = self.model.index(row, 0)
                        break
                self._on_select_entry(index)
                
                # Breach check for updated password
                auto_breach_chk_enabled = self.controller.get_config("breach_chk_enabled")
                if auto_breach_chk_enabled:
                    breach_status = is_password_breached(password_input)
                    updated_entry = self.controller.get_entry_details(eid)
                    for i, row in enumerate(self.breach_model.entries):
                        if row["service"] == updated_entry["service"] and row["username"] == updated_entry["username"]:
                            self.breach_model.entries[i]["breached"] = breach_status
                            self.breach_model.entries[i]["last_checked"] = get_last_checked_timestamp()
                            self.breach_model.layoutChanged.emit()
                            break
            self.edit_btn.setText("Edit")

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
        self._password_visible = False
        self._update_password_field()
        self.notes_field.setReadOnly(True)
        self.edit_btn.setText("Edit")
        self.cancel_btn.hide()
        self.pwd_tool_btns.setVisible(False)


    def _delete_entry(self):
        eid = self._selected_entry_id()
        if eid is None:
            return
        self.controller.delete_entry(eid)
        self._load_entries()
        self.detail_panel.hide()
        PopupDialog("Deleted", "Entry deleted.")

    def _on_select_entry(self, index):
        if self._edit_mode:
            dialog = PopupDialog(
                "Discard Changes?",
                "You have unsaved changes. Discard them?",
                yes_label="Yes", 
                no_label="No"
            )
            response = dialog.exec()
            if response == PopupDialog.DialogCode.Rejected:
                return
            self._cancel_edit()
        entry_meta = self.model.data(index, Qt.ItemDataRole.UserRole)
        if not entry_meta:
            self.detail_panel.hide()
            return
        full_entry = self.controller.get_entry_details(entry_meta["id"])
        if not full_entry:
            self.detail_panel.hide()
            return

        self._current_password = full_entry.get("password", "")
        self._password_visible = False
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
        self._password_visible = not self._password_visible
        self._update_password_field()

    def _update_password_field(self):
        if self._password_visible:
            self.password_field.setText(self._current_password)
        else:
            self.password_field.setText("●●●●●●●●")

    def _generate_quick_password(self):
        password = generate_strong_password()
        self.password_field.setText(password)
        if hasattr(self, "strength_bar"):
            self.strength_bar.evaluate(password)
    
    def _customize_password(self):
        dlg = PasswordGeneratorDialog(self)
        if dlg.exec():
            password = dlg.get_password()
            self.password_field.setText(password)
            if hasattr(self, "strength_bar"):
                self.strength_bar.evaluate(password)
    
    def _check_all_breaches(self):
        if not is_connected_to_internet():
            self.breach_info.setText("⚠️ No internet connection. Breach status cannot be updated.")
            self.last_breach_check.setText("Last Checked: —")
            self.recheck_btn.setEnabled(False)
            self.breach_stack.setCurrentWidget(self.breach_placeholder)
            return

        entries = self.controller.list_entries()
        results = []

        for e in entries:
            pwd = self.controller.get_entry_details(e["id"]).get("password", "")
            status = is_password_breached(pwd)
            results.append({
                "service": e["service"],
                "username": e["username"],
                "breached": status,
                "last_checked": get_last_checked_timestamp()
            })

        self.breach_model.update(results, store_all=True)
        self.last_breach_check.setText(f"Last Checked: {get_last_checked_timestamp()}")
        self.breach_stack.setCurrentWidget(self.breach_table)

    def _toggle_breach_filter(self):
        breached_only = self.filter_breached_btn.isChecked()
        all_entries = self.controller.list_entries()

        results = []
        for e in all_entries:
            pwd = self.controller.get_entry_details(e["id"]).get("password", "")
            status = is_password_breached(pwd)
            if breached_only and not status:
                continue
            results.append({
                "service": e["service"],
                "username": e["username"],
                "breached": status,
                "last_checked": get_last_checked_timestamp()
            })

        self.breach_model.update(results)

    def _on_breach_table_clicked(self, index):
        if index.column() != 4:
            return  # Only act on Fix button column

        entry = self.breach_model.data(index, Qt.ItemDataRole.UserRole)
        if not entry or not entry["breached"]:
            return

        # Go back to Vault tab
        self.stacked_pages.setCurrentIndex(0)
        self.vault_btn.setChecked(True)
        self._switch_tab(0)

        # Select matching row
        for row in range(self.model.rowCount()):
            vault_entry = self.model.data(self.model.index(row, 0), Qt.ItemDataRole.UserRole)
            if vault_entry and vault_entry["service"] == entry["service"] and vault_entry["username"] == entry["username"]:
                self.table.selectRow(row)
                self._on_select_entry(self.model.index(row, 0))  # Show detail
                self._edit_mode = False  # Reset
                self._toggle_edit_mode()  # Go into edit mode
                break

    def _on_breach_column_clicked(self, col):
        # Toggle filter only if Status column is clicked (index 2)
        if col != 2:
            return

        # Cycle through None → breached → safe → None
        if self.status_filter_mode is None:
            self.status_filter_mode = True
        elif self.status_filter_mode is True:
            self.status_filter_mode = False
        else:
            self.status_filter_mode = None

        self._apply_breach_filter()
        
    def _apply_breach_filter(self):
        if not hasattr(self.breach_model, "all_entries"):
            return  # nothing to filter

        filtered = []

        for entry in self.breach_model.all_entries:
            is_breached = entry["breached"]

            if self.status_filter_mode is None:
                include = True
            elif self.status_filter_mode is True:
                include = is_breached
            else:
                include = not is_breached

            if include:
                filtered.append(entry)

        self.breach_model.update(filtered, store_all=False)

    def _apply_breach_filter_mode(self, mode, icon):
        self.status_filter_mode = mode
        self._apply_breach_filter()

        # Update header label with emoji
        header_label = f"Status {icon}" if icon else "Status"
        self.breach_model.setHeaderData(2, Qt.Orientation.Horizontal, header_label)

    def _on_breach_column_clicked(self, col):
        if col != 2:
            return  # Only show filter for "Status" column

        menu = QMenu(self)
        menu.setStyleSheet(DASHBOARD['menu'])

        filter_options = [
            ("⚪ Show All", None, "⚪"),
            ("🛑 Breached Only", True, "🛑"),
            ("🟢 Safe Only", False, "🟢")
        ]

        for text, mode, icon in filter_options:
            action = QAction(text, self)
            action.triggered.connect(lambda _, m=mode, i=icon: self._apply_breach_filter_mode(m, i))
            menu.addAction(action)

        header = self.breach_table.horizontalHeader()
        x = self.breach_table.mapToGlobal(header.pos()).x() + header.sectionPosition(col)
        y = self.breach_table.mapToGlobal(header.pos()).y() + header.height()
        menu.exec(QPoint(x, y))

    def _logout(self):
        confirm = PopupDialog("Logout", "Are you sure you want to logout?", yes_label="Logout", no_label="Cancel")
        if confirm.exec():
            self.select_window = VaultSelectWindow()
            self.select_window.show()
            self.close()

    def _show_help(self):
        dlg = HelpOverlay(self)
        dlg.exec()

    def _toggle_quick_help(self):
        if not hasattr(self, "quick_help_panel"):
            self.quick_help_panel = SlideHelpPanel(self)
        self.quick_help_panel.show_slide()

    def eventFilter(self, obj, event):
        # Reset timer on any key or mouse event
        if event.type() in (QEvent.Type.MouseButtonPress, 
                            QEvent.Type.KeyPress,
                            QEvent.Type.MouseMove):
            self.session_timer.start()
        return super().eventFilter(obj, event)

    def _on_session_timeout(self):
        popup = PopupDialog(
            "Session Timeout",
            "You have been logged out due to inactivity.",
            yes_label="OK",
            parent=self
        )
        popup.exec()
        self.logout()

    def logout(self):
        self.close()
        from ciphervault.gui.views.login_window import LoginWindow
        self.login_window = LoginWindow()
        self.login_window.show()