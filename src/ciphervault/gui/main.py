# ciphervault/gui/main.py

import sys
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QTimer
from ciphervault.gui.views.splash_screen import SplashScreen

def main():
    app = QApplication(sys.argv)
    splash = SplashScreen()
    splash.show()
    QTimer.singleShot(2000, splash.show_main)
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
