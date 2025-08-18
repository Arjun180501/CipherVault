from PyQt6.QtWidgets import QMainWindow, QTableView, QToolBar, QLineEdit, QStatusBar
from PyQt6.QtGui     import QAction, QIcon
from PyQt6.QtCore    import Qt, QSize

from ciphervault.gui.models.entry_model import EntryModel
from ciphervault.gui.views.entry_dialog import EntryDialog

class MainWindow(QMainWindow):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.setWindowTitle("CipherVault")
        self.resize(800, 600)
        self._build_ui()
        self._load_entries()

    def _build_ui(self):
        self.table = QTableView()
        self.model = EntryModel()
        self.table.setModel(self.model)
        self.table.setSelectionBehavior(self.table.SelectionBehavior.SelectRows)
        self.table.doubleClicked.connect(self._edit_entry)
        self.setCentralWidget(self.table)

        tb = QToolBar("Main")
        tb.setIconSize(QSize(24, 24))
        self.addToolBar(tb)
        tb.addAction(QAction(QIcon("assets/icons/add.svg"),
                             "Add", self, triggered=self._add_entry))
        tb.addAction(QAction(QIcon("assets/icons/edit.svg"),
                             "Edit", self, triggered=self._edit_entry))
        tb.addAction(QAction(QIcon("assets/icons/delete.svg"),
                             "Delete", self, triggered=self._delete_entry))
        tb.addSeparator()
        search = QLineEdit(placeholderText="Search…")
        search.setObjectName("search")
        search.textChanged.connect(self._filter_entries)
        tb.addWidget(search)

        self.setStatusBar(QStatusBar())

    def _load_entries(self):
        data = self.controller.list_entries()
        self.model.update(data)
        self.statusBar().showMessage(f"{len(data)} entries loaded.")

    def _filter_entries(self, text):
        filtered = [
            e for e in self.controller.list_entries()
            if text.lower() in e["service"].lower()
               or text.lower() in e["username"].lower()
        ]
        self.model.update(filtered)

    def _selected_id(self):
        sel = self.table.selectionModel().selectedRows()
        if not sel:
            return None
        entry = self.model.data(sel[0], Qt.ItemDataRole.UserRole)
        return entry["id"]

    def _add_entry(self):
        dlg = EntryDialog(self)
        if dlg.exec():
            self.controller.add_entry(**dlg.get_data())
            self._load_entries()
            EntryDialog(self, "Added", "Entry added successfully.")

    def _edit_entry(self, _=None):
        eid = self._selected_id()
        if eid is None:
            return
        raw = next(e for e in self.controller.list_entries() if e["id"] == eid)
        dlg = EntryDialog(self, existing=raw)
        if dlg.exec():
            self.controller.update_entry(eid, **dlg.get_data())
            self._load_entries()
            EntryDialog(self, "Updated", "Entry updated successfully.")

    def _delete_entry(self):
        eid = self._selected_id()
        if eid is None:
            return
        self.controller.delete_entry(eid)
        self._load_entries()
        EntryDialog(self, "Deleted", "Entry deleted.")
