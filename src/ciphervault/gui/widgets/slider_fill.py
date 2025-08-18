from PyQt6.QtWidgets import QSlider, QStyleOptionSlider, QStyle
from PyQt6.QtGui import QPainter, QColor
from PyQt6.QtCore import Qt

class FilledSlider(QSlider):
    def __init__(self, orientation, parent=None):
        super().__init__(orientation, parent)
        self.setSingleStep(5)
        self.setPageStep(5)

    def paintEvent(self, event):
        super().paintEvent(event)

        opt = QStyleOptionSlider()
        self.initStyleOption(opt)
        handle_rect = self.style().subControlRect(
            QStyle.ComplexControl.CC_Slider, opt, QStyle.SubControl.SC_SliderHandle, self
        )

        groove_rect = self.style().subControlRect(
            QStyle.ComplexControl.CC_Slider, opt, QStyle.SubControl.SC_SliderGroove, self
        )

        fill_rect = groove_rect.adjusted(0, 0, 0, 0)
        fill_rect.setRight(handle_rect.center().x())

        p = QPainter(self)
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(QColor("#FF6D00"))
        p.drawRect(fill_rect)
        p.end()
