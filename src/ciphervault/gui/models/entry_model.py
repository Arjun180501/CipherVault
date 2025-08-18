# src/ciphervault/gui/models/entry_model.py
from PyQt6.QtCore import (
    QAbstractTableModel, Qt, QModelIndex, QVariant
)

COLUMNS = ["Service", "Username", "Password", "Notes"]

class EntryModel(QAbstractTableModel):
    def __init__(self, entries: list[dict] = [], parent=None):
        super().__init__(parent)
        self.all_entries = []
        self._entries = entries

    def update(self, entries: list[dict], store_all=True):
        self.beginResetModel()
        self._entries = entries
        if store_all:
            self.all_entries = entries.copy()
        self.endResetModel()

    def rowCount(self, parent=QModelIndex()):
        return len(self._entries)

    def columnCount(self, parent=QModelIndex()):
        return len(COLUMNS)

    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
        if not index.isValid():
            return QVariant()
        entry = self._entries[index.row()]
        col = COLUMNS[index.column()].lower()
        if role == Qt.ItemDataRole.DisplayRole:
            return entry[col] if col != "password" else "••••••••"
        if role == Qt.ItemDataRole.UserRole:
            return entry
        return QVariant()

    def headerData(self, section, orientation, role=Qt.ItemDataRole.DisplayRole):
        if orientation == Qt.Orientation.Horizontal and role == Qt.ItemDataRole.DisplayRole:
            return COLUMNS[section]
        return super().headerData(section, orientation, role)
    
    def sort(self, column, order=Qt.SortOrder.AscendingOrder):
        if column == 2:  # Password column index
            return  # Skip sorting password
        self.layoutAboutToBeChanged.emit()

        key_map = {
            0: lambda e: e["service"].lower(),
            1: lambda e: e["username"].lower(),
            3: lambda e: e["notes"].lower() if "notes" in e else ""
        }
        key = key_map.get(column, lambda e: "")
        self._entries.sort(key=key, reverse=(order == Qt.SortOrder.DescendingOrder))

        self.layoutChanged.emit()