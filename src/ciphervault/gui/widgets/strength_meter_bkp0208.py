from PyQt6.QtWidgets import QWidget, QProgressBar, QLabel, QVBoxLayout
from PyQt6.QtCore import Qt, QPropertyAnimation, QEasingCurve
import zxcvbn


class PasswordStrengthBar(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.label = QLabel("Weak")
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label.setStyleSheet("color: orange; font-weight: bold;")

        self.bar = QProgressBar()
        self.bar.setRange(0, 5)
        self.bar.setValue(0)
        self.bar.setTextVisible(False)
        self.bar.setFixedHeight(4)

        self.bar.setStyleSheet("""
            QProgressBar {
                border: none;
                border-radius: 2px;
                background-color: #222;
            }
            QProgressBar::chunk {
                border-radius: 2px;
                background-color: #cc3300;
            }
        """)

        layout = QVBoxLayout()
        layout.setSpacing(2)
        layout.addWidget(self.label)
        layout.addWidget(self.bar)
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)

        # Animation object
        self.animation = QPropertyAnimation(self.bar, b"value")
        self.animation.setDuration(300)
        self.animation.setEasingCurve(QEasingCurve.Type.InOutCubic)

    def evaluate(self, password: str):
        if not password:
            self._animate_to_value(0)
            self.label.setText("Too Short")
            self.bar.setStyleSheet(self._bar_style("#cc3300"))
            return

        result = zxcvbn.zxcvbn(password)
        score = result.get("score", 0)
        self._animate_to_value(score+1)

        if score == 0:
            self.label.setText("Very Weak")
            color = "#cc3300"
        elif score == 1:
            self.label.setText("Weak")
            color = "#ff6600"
        elif score == 2:
            self.label.setText("Moderate")
            color = "#ffcc00"
        elif score == 3:
            self.label.setText("Strong")
            color = "#99cc00"
        else:
            self.label.setText("Very Strong")
            color = "#33cc33"

        self.bar.setStyleSheet(self._bar_style(color))

    def _animate_to_value(self, target_value: int):
        self.animation.stop()
        self.animation.setStartValue(self.bar.value())
        self.animation.setEndValue(target_value)
        self.animation.start()

    def _bar_style(self, chunk_color):
        return f"""
        QProgressBar {{
            border: none;
            border-radius: 2px;
            background-color: #222;
        }}
        QProgressBar::chunk {{
            border-radius: 2px;
            background-color: {chunk_color};
        }}
        """