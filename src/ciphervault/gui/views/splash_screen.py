from PyQt6.QtWidgets import QSplashScreen
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt, QTimer
from ciphervault.gui.utils.settings import LOGO_PATH
from ciphervault.gui.views.select_window import VaultSelectWindow

class SplashScreen(QSplashScreen):
    def __init__(self):
        original_pixmap = QPixmap(LOGO_PATH)

        # Scale it down to e.g. 300px width for the splash
        scaled_pixmap = original_pixmap.scaled(
            300,
            300,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )

        super().__init__(scaled_pixmap)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)

    def show_main(self):
        self.main_window = VaultSelectWindow()
        self.main_window.show()
        self.close()
