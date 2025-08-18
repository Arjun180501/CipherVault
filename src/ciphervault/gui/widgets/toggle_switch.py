from PyQt6.QtWidgets import QCheckBox
from PyQt6.QtGui import QPainter, QColor
from PyQt6.QtCore import Qt, QPropertyAnimation, QRect, pyqtProperty


class ToggleSwitch(QCheckBox):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setChecked(False)

        # --- Dimensions ---
        self._thumb_radius = 14
        self._track_height = 18
        self._track_margin = 2
        self._offset = self._track_margin

        # --- Animation ---
        self._animation = QPropertyAnimation(self, b"offset", self)
        self._animation.setDuration(200)

        # --- Init UI ---
        self.setFixedSize(36, self._track_height + self._track_margin * 2)
        self.stateChanged.connect(self.start_animation)

    def sizeHint(self):
        return self.size()

    # --- Qt Property ---
    def get_offset(self):
        return self._offset

    def set_offset(self, value):
        self._offset = value
        self.update()

    offset = pyqtProperty(float, fget=get_offset, fset=set_offset)

    # --- Animation ---
    def start_animation(self):
        end = self.width() - self._thumb_radius - self._track_margin if self.isChecked() else self._track_margin
        self._animation.stop()
        self._animation.setStartValue(self._offset)
        self._animation.setEndValue(end)
        self._animation.start()

    # ✅ Respond to clicks anywhere inside the widget (override logic)
    def hitButton(self, pos):
        return self.rect().contains(pos)

    # --- Paint ---
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Draw Track
        track_rect = QRect(0, 0, self.width(), self.height())
        track_color = QColor("#FF6D00") if self.isChecked() else QColor("#444")
        painter.setBrush(track_color)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(track_rect, self._track_height / 2, self._track_height / 2)

        # Draw Thumb
        thumb_rect = QRect(int(self._offset), self._track_margin, self._thumb_radius, self._thumb_radius)
        painter.setBrush(QColor("white"))
        painter.drawEllipse(thumb_rect)
