from PyQt6.QtCore import Qt, QAbstractTableModel, QModelIndex
from PyQt6.QtGui import QBrush,QFont

class BreachModel(QAbstractTableModel):
    def __init__(self):
        super().__init__()
        self.all_entries = []
        self.entries = []
        self.sorted_column = 0
        self.sort_order = Qt.SortOrder.AscendingOrder

    def update(self, entries, store_all=True):
        self.beginResetModel()
        self.entries = entries
        if store_all:
            self.all_entries = entries.copy()
        self.sort(self.sorted_column, self.sort_order)
        self.endResetModel()

    def rowCount(self, parent=QModelIndex()):
        return len(self.entries)

    def columnCount(self, parent=QModelIndex()):
        return 5  # Service, Username, Status, Last Checked, Fix

    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
        if not index.isValid():
            return None

        entry = self.entries[index.row()]
        col = index.column()

        if role == Qt.ItemDataRole.DisplayRole:
            if col == 0:
                return entry["service"]
            elif col == 1:
                return entry["username"]
            elif col == 2:
                return "🔴 Breached" if entry["breached"] else "🟢 Safe"
            elif col == 3:
                return entry["last_checked"]
            elif col == 4:
                return "🔧 Fix" if entry["breached"] else ""

        elif role == Qt.ItemDataRole.FontRole and col == 4:
            font = QFont()
            font.setBold(True)
            return font

        elif role == Qt.ItemDataRole.ForegroundRole and col == 2:
            return QBrush(Qt.GlobalColor.red if entry["breached"] else Qt.GlobalColor.green)
        
        elif role == Qt.ItemDataRole.UserRole:
            return entry

        return None

    def headerData(self, section, orientation, role=Qt.ItemDataRole.DisplayRole):
        if orientation == Qt.Orientation.Horizontal and role == Qt.ItemDataRole.DisplayRole:
            return ["Service", "Username", "Status", "Last Checked", ""][section]
        return None

    def sort(self, column, order=Qt.SortOrder.AscendingOrder):
        self.layoutAboutToBeChanged.emit()
        key_map = {
            0: lambda e: e["service"].lower(),
            1: lambda e: e["username"].lower(),
            2: lambda e: e["breached"],  # bool: False < True
            3: lambda e: e["last_checked"]
        }

        key_func = key_map.get(column, lambda e: "")
        self.entries.sort(key=key_func, reverse=(order == Qt.SortOrder.DescendingOrder))

        self.sorted_column = column
        self.sort_order = order
        self.layoutChanged.emit()