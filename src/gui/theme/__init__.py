from PySide6.QtCore import Qt, QSize, QRect, QRectF
from PySide6.QtGui import QBitmap, QColor, QIcon, QImage, QPainter, QPixmap, QRegion

from src.gui.theme.theme_manager import ColorThemeManager
from src.gui.theme.colors import DARK, LIGHT, ACCENT_PRESETS, LIGHT_ACCENT_PRESETS
from src.gui.theme.styles import STYLES, FONT_FAMILY
from src.gui.theme.accent_picker import AccentPicker


def t(style_key: str) -> str:
    """Render a named stylesheet template with the current theme colors."""
    payload = dict(ColorThemeManager.instance().colors.__dict__)
    payload["font_family"] = FONT_FAMILY
    return STYLES[style_key].format_map(payload)


def themed_stylesheet(style_key: str, **extra) -> str:
    """Render a stylesheet template with the current colors plus runtime
    extras (e.g. a generated caret image path passed as ``caret=...``)."""
    payload = dict(ColorThemeManager.instance().colors.__dict__)
    payload["font_family"] = FONT_FAMILY
    payload.update(extra)
    return STYLES[style_key].format_map(payload)


def theme_icon(resource_path: str, color_hex: str) -> QIcon:
    """Recolor a monochrome (white) SVG icon to *color_hex* using its alpha.
    Raster artwork is returned as it is."""
    if not resource_path.lower().endswith(".svg"):
        return QIcon(resource_path)
    img = QImage(resource_path)
    img = img.convertToFormat(QImage.Format.Format_ARGB32)
    painter = QPainter(img)
    painter.setCompositionMode(
        QPainter.CompositionMode.CompositionMode_SourceIn)
    painter.fillRect(img.rect(), QColor(color_hex))
    painter.end()
    return QIcon(QPixmap.fromImage(img))


def _crop_to_content(image: QImage) -> QImage:
    """*image* without its fully transparent border."""
    bounds = QRegion(QBitmap.fromImage(image.createAlphaMask())).boundingRect()
    return image.copy(bounds) if not bounds.isEmpty() else image


def theme_pixmap(resource_path: str, color_hex: str, size: int,
                 dpr: float = 1.0) -> QPixmap:
    """Rasterize a monochrome SVG at *size* logical pixels, tinted to a color.

    Raster artwork (the feature PNGs) is not tinted: it is cropped to its
    visible pixels and fitted into the square, keeping its aspect ratio.

    Unlike ``theme_icon`` the icon is scaled by the SVG engine *before* the
    tint is applied, so icons with a small viewBox (11x11, 16x16) stay crisp
    when blown up to home-tile size. ``dpr`` renders extra device pixels on
    HiDPI screens and sets the pixmap's device pixel ratio accordingly.
    """
    scale = max(1.0, float(dpr))
    logical = int(round(size))
    phys = int(round(size * scale))
    pm = QPixmap(phys, phys)
    pm.setDevicePixelRatio(scale)
    pm.fill(Qt.GlobalColor.transparent)
    painter = QPainter(pm)
    if not resource_path.lower().endswith(".svg"):
        image = QImage(resource_path)
        if not image.isNull():
            image = _crop_to_content(image)
            factor = logical / max(image.width(), image.height())
            width, height = image.width() * factor, image.height() * factor
            painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
            painter.drawImage(QRectF((logical - width) / 2, (logical - height) / 2, width, height), image)
        painter.end()
        return pm
    src = QIcon(resource_path).pixmap(QSize(logical, logical))
    painter.drawPixmap(QRect(0, 0, logical, logical), src)
    painter.setCompositionMode(
        QPainter.CompositionMode.CompositionMode_SourceIn)
    painter.fillRect(QRect(0, 0, logical, logical), QColor(color_hex))
    painter.end()
    return pm


__all__ = [
    "ColorThemeManager", "DARK", "LIGHT", "ACCENT_PRESETS", "LIGHT_ACCENT_PRESETS", "STYLES", "FONT_FAMILY",
    "AccentPicker", "t", "themed_stylesheet", "theme_icon", "theme_pixmap",
]
