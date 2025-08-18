from PyQt6.QtWidgets import QWidget, QProgressBar, QLabel, QVBoxLayout, QToolButton, QHBoxLayout, QToolTip
from PyQt6.QtCore import Qt, QPropertyAnimation, QEasingCurve, QPoint, QEvent
import zxcvbn


class PasswordStrengthBar(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self._zxcvbn_result = {}

        # Label above bar
        self.label = QLabel("Weak")
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label.setStyleSheet("color: orange; font-weight: bold;")

        # Progress bar
        self.bar = QProgressBar()
        self.bar.setRange(0, 5)
        self.bar.setValue(0)
        self.bar.setTextVisible(False)
        self.bar.setFixedHeight(4)
        self.bar.setStyleSheet(self._bar_style("#cc3300"))

        # Info icon
        self.info_btn = QToolButton()
        self.info_btn.setText("💡")
        self.info_btn.setStyleSheet("font-size: 14px; font-weight: bold; background: transparent;")
        self.info_btn.setCursor(Qt.CursorShape.ArrowCursor)
        self.info_btn.installEventFilter(self)

        # Layout for bar + icon
        bar_row = QHBoxLayout()
        bar_row.setContentsMargins(0, 0, 0, 0)
        bar_row.addWidget(self.bar)
        bar_row.addWidget(self.info_btn, alignment=Qt.AlignmentFlag.AlignRight)

        layout = QVBoxLayout()
        layout.setSpacing(2)
        layout.addWidget(self.label)
        layout.addLayout(bar_row)
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)

        # Animation for smooth bar transitions
        self.animation = QPropertyAnimation(self.bar, b"value")
        self.animation.setDuration(300)
        self.animation.setEasingCurve(QEasingCurve.Type.InOutCubic)

    def evaluate(self, password: str):
        if not password:
            self._animate_to_value(0)
            self.label.setText("Too Short")
            self.bar.setStyleSheet(self._bar_style("#cc3300"))
            self._zxcvbn_result = {}
            return

        result = zxcvbn.zxcvbn(password)
        self._zxcvbn_result = result
        score = result.get("score", 0)

        self._animate_to_value(score + 1)

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

    def eventFilter(self, source, event):
        if source == self.info_btn and event.type() == QEvent.Type.Enter:
            self._show_details_tooltip()
        return super().eventFilter(source, event)

    def _show_details_tooltip(self):
        if not self._zxcvbn_result:
            return

        score = self._zxcvbn_result.get("score", 0)
        feedback = self._zxcvbn_result.get("feedback", {})
        suggestions = feedback.get("suggestions", [])
        warning = feedback.get("warning", "")

        # Score-based message
        strength_labels = [
            ("Very Weak", "This password is too short or very easy to guess."),
            ("Weak", "This password could be cracked quickly. Add length and complexity."),
            ("Moderate", "Not bad, but could be stronger. Add symbols or uncommon words."),
            ("Strong", "Good job! This password is hard to guess."),
            ("Very Strong", "Excellent. No improvements needed.")
        ]
        label, description = strength_labels[min(score, 4)]

        tooltip_text = f"""
            <b>Strength:</b> {label}<br>
            {description}
        """

        # Add suggestions only if present
        if suggestions:
            suggestions_text = "<ul>" + "".join(f"<li>{s}</li>" for s in suggestions) + "</ul>"
            tooltip_text += f"<br><b>Suggestions:</b>{suggestions_text}"

        # Add warning only if present
        if warning:
            tooltip_text += f"<b>Warning:</b> {warning}"

        QToolTip.showText(self.info_btn.mapToGlobal(QPoint(0, self.info_btn.height())), tooltip_text.strip(), self.info_btn)