# styles.py

# -----------------------------
# Splash Screen styles
# -----------------------------
SPLASH = {
    "window": """
        QDialog {
            background-color: rgba(0, 0, 0, 0.8);
        }
    """,
}

# -----------------------------
# Select Window styles
# -----------------------------
SELECT = {
    "title": """
        color: #FFFFFF;
        font-size: 32px;
        font-weight: bold;
    """,
    "button": """
        QPushButton {
            background-color: rgba(0, 0, 0, 0.4);
            color: #ffffff;
            border: 2px solid rgba(255, 255, 255, 0.2);
            border-radius: 10px;
            font-size: 18px;
            font-weight: bold;
            padding: 10px 20px;
        }
        QPushButton:hover {
            border: 2px solid #FF6D00;
        }
        QPushButton:pressed {
            background-color: rgba(255, 109, 0, 0.2);
            border: 2px solid #FF6D00;
        }
    """
}

# -----------------------------
# Login Window styles
# -----------------------------
LOGIN = {
    "button": """
        QPushButton {
            background-color: rgba(0, 0, 0, 0.4);
            color: #ffffff;
            border: 2px solid rgba(255, 255, 255, 0.2);
            border-radius: 10px;
            font-size: 18px;
            font-weight: bold;
            padding: 10px 20px;
            min-width: 250px;
        }
        QPushButton:hover {
            border: 2px solid #FF6D00;
        }
        QPushButton:pressed {
            background-color: rgba(255, 109, 0, 0.2);
            border: 2px solid #FF6D00;
        }
    """,
    "input": """
        QLineEdit {
            background-color: rgba(0, 0, 0, 0.5);
            color: #ffffff;
            border: 2px solid rgba(255, 255, 255, 0.3);
            border-radius: 8px;
            font-size: 16px;
            padding: 6px 12px;
            min-width: 300px;
        }
    """,
    "combobox": """
        QComboBox {
            background-color: rgba(0, 0, 0, 0.5);
            color: #ffffff;
            border: 2px solid rgba(255, 255, 255, 0.3);
            border-radius: 8px;
            font-size: 16px;
            padding: 6px 12px;
            min-width: 300px;
        }
        QComboBox QAbstractItemView {
            background-color: #222222;
            color: #ffffff;
            selection-background-color: #FF6D00;
            selection-color: #ffffff;
        }
    """,
}

# -----------------------------
# Dialog styles
# -----------------------------
ENTRY_DIALOG = {
    "dialog": """
        QDialog {
            background-color: rgba(0, 0, 0, 0.7);
            border-radius: 12px;
        }
    """,
    "button": """
        QPushButton {
            background-color: rgba(0, 0, 0, 0.5);
            color: #FFFFFF;
            border: 2px solid rgba(255, 255, 255, 0.2);
            border-radius: 8px;
            font-size: 14px;
            padding: 6px 12px;
        }
        QPushButton:hover {
            border: 2px solid #FF6D00;
        }
    """,
    "title_label": """
        color: #FF6D00;
        font-size: 20px;
        font-weight: bold;
    """,
    "message_label": """
        color: #FFFFFF;
        font-size: 15px;
        font-weight: bold;
    """,
    "checkbox": """
    QCheckBox {
        color: #FFFFFF;
        font-size: 15px;
    }""",
}

# -----------------------------
# Init Window styles
# -----------------------------
# styles.py

INIT = {
    "title_label": """
        QLabel {
            color: #FF6D00;
            font-size: 28px;
            font-weight: bold;
        }
    """,
    "input": """
        QLineEdit {
            background-color: rgba(0, 0, 0, 0.4);
            color: #FFFFFF;
            border: 2px solid rgba(255, 255, 255, 0.3);
            border-radius: 8px;
            font-size: 14px;
            padding: 6px 12px;            
        }
        QLineEdit:focus {
            border: 2px solid #FF6D00;
            background-color: #222222;
        }
    """,
    "combobox": """
        QComboBox {
            background-color: rgba(0, 0, 0, 0.4);
            color: #FFFFFF;
            border: 2px solid rgba(255, 255, 255, 0.3);
            border-radius: 8px;
            font-size: 16px;
            padding: 6px 12px;
            min-height: 32px;
        }
        QComboBox QAbstractItemView {
            background-color: #222222;
            color: #ffffff;
            selection-background-color: #FF6D00;
            selection-color: #ffffff;
        }
        QComboBox:focus {
            border: 2px solid #FF6D00;
            background-color: #222222;
        }
    """,
    "button": """
        QPushButton {
            background-color: transparent;
            color: #FFFFFF;
            border: 2px solid #FFFFFF;
            border-radius: 10px;
            font-size: 14px;
            font-weight: bold;
            padding: 5px 10px;
        }
        QPushButton:hover {
            border: 2px solid #FF6D00;
        }
        QPushButton:pressed {
            border: 2px solid #FF6D00;
            background-color: rgba(255, 109, 0, 0.15);
        }
        QPushButton:focus {
            border: 2px solid #FF6D00;
            background-color: #222222;
        }
    """,
    "checkbox": """
        QCheckBox {
            color: #FFFFFF;
            font-size: 15px;
        }
    """,
}



DASHBOARD = {
    "main": """
        QWidget {
            background-color: transparent;
            color: white;
            font-family: 'Segoe UI';
        }
    """,
    "nav_tab": """
        QPushButton {
            background: transparent;
            color:#CCCCCC;
            font-weight: bold;
            font-size: 14px;
            padding: 6px 10px;
            border: none;
        }
        QPushButton:hover {
            border: 2px solid #FF6D00;
        }
        QPushButton:pressed {
            border: 2px solid #FF6D00;
            background-color: #222;
            border-radius: 25px;
        }
    """,
    "button": """
        QPushButton {
            background-color: transparent;
            color: #CCCCCC;
            border: 2px solid #CCCCCC;
            border-radius: 10px;
            font-size: 12px;
            font-weight: bold;
            padding: 5px 10px;
        }
        QPushButton:hover {
            border: 2px solid #FF6D00;
        }
        QPushButton:pressed {
            border: 2px solid #FF6D00;
            background-color: rgba(255, 109, 0, 0.15);
        }
    """,
    "add_button": """
        QPushButton {
            background-color: transparent;
            color: #CCCCCC;
            border: 2px solid #CCCCCC;
            border-radius: 10px;
            font-size: 14px;
            font-weight: bold;
            padding: 5px 10px;
        }
        QPushButton:hover {
            border: 2px solid #FF6D00;
        }
        QPushButton:pressed {
            border: 2px solid #FF6D00;
            background-color: rgba(255, 109, 0, 0.15);
        }
    """,
    "close_button": """
        QPushButton {
            background-color: transparent;
            font-size: 14px;
            padding: 5px 10px;
        }
        QPushButton:hover {
            border: 2px solid #FF6D00;
        }
        QPushButton:pressed {
            border: 2px solid #FF6D00;
            background-color: rgba(255, 109, 0, 0.15);
        }
    """,
    "nav_tab_active": """
        QPushButton {
            background-color: transparent;
            color: #FFFFFF;
            font-weight: bold;
            font-size: 18px;
            border: none;
            border-radius: 25px;
            padding: 6px 10px;
            border-left: 4px solid #ff8c00;
            border-right: none;
        }
        QPushButton:hover {
            border: 2px solid #FF6D00;
        }
        QPushButton:pressed {
            border: 2px solid #FF6D00;
        }
    """,
    "table": """
        QTableView {
            background-color: #121212 !important;
            color: white;
            gridline-color: transparent;
            width: 100%;
            border-radius:12px;
            border: 1px solid #333;
            padding: 10px;
            font-size: 14px;
            font-family: 'Segoe UI', sans-serif;


        }
        QTableView::item {
            width:fit-content;
            text-align: center;
        }
        
        QTableCornerButton::section {
            background-color: #121212;
            border: 1px solid #333;
        }
        QHeaderView::section {
            background-color: #121212;
            color: orange;
            font-weight: bold;
            padding: 4px;
            border:none;
            gridline-color: transparent;
            width:100%;
            font-size: 14px;
        }
    """,
    "detail_panel": """
        background-color: transparent;
        border: none;
        padding: 0px 10px 0px 10px;
        color: white;
        font-size: 14px;
        margin:0px;
        
    """,
    "searchbar": """
        QLineEdit {
            background-color: #121212;
            border-radius: 50px;
            border: 1px solid gray;
            padding 5px 10px;
            font-size: 14px;
        }
        QLineEdit:hover {
            border: 2px solid #FF6D00;
        }
    """,
    "flat_input": """
        QLineEdit, QTextEdit {
            background-color: transparent;
            border: none;
            padding: 5px;
            font-size: 14px;
        }
        QLineEdit:focus, QTextEdit:focus {
            border: 1px solid orange;
        }
    """,
    "label": "color: orange; font-weight: bold; font-size: 13px;",
    "dialog": """
    
        QDialog {
            background-color: transparent;
            border-radius: 12px;
        }
    """,
    "menu": """
        QMenu {
            background-color: #2c2c2c;
            color: white;
            border: 1px solid #444;
            padding: 6px;
            border-radius: 6px;
        }
        QMenu::item {
            padding: 8px 20px;
            background-color: transparent;
        }
        QMenu::item:selected {
            background-color: #444;
            border-radius: 4px;
            border: 2px solid #FF6D00;
        }
    """,
}

BREACH_TAB = {
    "button": """
        QPushButton {
            background-color: transparent;
            color: #CCCCCC;
            border: 2px solid #CCCCCC;
            border-radius: 10px;
            font-size: 12px;
            font-weight: bold;
            padding: 8px 16px;
            min-width: 180px;
        }
        QPushButton:hover {
            border: 2px solid #FF6D00;
        }
        QPushButton:pressed {
            border: 2px solid #FF6D00;
            background-color: rgba(255, 109, 0, 0.15);
        }
    """,
}

PROFILE = {
    "title": """
        color: #FFA500;
        font-size: 24px;
        font-weight: bold;
    """,
    "label": "color: #DDDDDD; font-size: 14px;",
    "readonly": """
        background-color: #222;
        color: white;
        border: 1px solid #555;
        padding: 4px;
    """,
    "checkbox": """
        color: #CCCCCC;
        font-size: 14px;
    """
}

HELP = {
    "button": """
        QPushButton {
            background-color: transparent;
            color: #CCCCCC;
            border: 2px solid #CCCCCC;
            border-radius: 14px;
            font-size: 14px;
            font-weight: bold;
            padding: 5px 10px;
        }
        QPushButton:hover {
            border: 2px solid #FF6D00;
        }
        QPushButton:pressed {
            border: 2px solid #FF6D00;
            background-color: rgba(255, 109, 0, 0.15);
        }
    """
}