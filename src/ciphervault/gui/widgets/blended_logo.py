from PyQt6.QtWidgets import QLabel, QGraphicsOpacityEffect
from PyQt6.QtGui import QPixmap, QRadialGradient, QColor, QPainter
from PyQt6.QtCore import Qt

def BlendedLogo(path, size=200):
    original_pixmap = QPixmap(path).scaled(
        size, size,
        Qt.AspectRatioMode.KeepAspectRatio,
        Qt.TransformationMode.SmoothTransformation
    )

    blended_pixmap = QPixmap(original_pixmap.size())
    blended_pixmap.fill(Qt.GlobalColor.transparent)

    gradient = QRadialGradient(
        blended_pixmap.width() / 2,
        blended_pixmap.height() / 2,
        blended_pixmap.width() / 2
    )
    gradient.setColorAt(0.0, QColor(255, 255, 255, 255))
    gradient.setColorAt(0.8, QColor(255, 255, 255, 100))
    gradient.setColorAt(1.0, QColor(255, 255, 255, 0))

    painter = QPainter(blended_pixmap)
    painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
    painter.drawPixmap(0, 0, original_pixmap)
    painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_DestinationIn)
    painter.fillRect(blended_pixmap.rect(), gradient)
    painter.end()

    label = QLabel()
    label.setPixmap(blended_pixmap)
    label.setAlignment(Qt.AlignmentFlag.AlignCenter)

    opacity = QGraphicsOpacityEffect()
    opacity.setOpacity(0.9)
    label.setGraphicsEffect(opacity)

    return label
