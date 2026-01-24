#                      M""""""""`M            dP
#                      Mmmmmm   .M            88
#                      MMMMP  .MMM  dP    dP  88  .dP   .d8888b.
#                      MMP  .MMMMM  88    88  88888"    88'  `88
#                      M' .MMMMMMM  88.  .88  88  `8b.  88.  .88
#                      M         M  `88888P'  dP   `YP  `88888P'
#                      MMMMMMMMMMM    -*-  Created by Zuko  -*-
#
#                      * * * * * * * * * * * * * * * * * * * * *
#                      * -    - -   F.R.E.E.M.I.N.D   - -    - *
#                      * -  Copyright © 2026 (Z) Programing  - *
#                      *    -  -  All Rights Reserved  -  -    *
#                      * * * * * * * * * * * * * * * * * * * * *

#              M""""""""`M            dP
#              Mmmmmm   .M            88
#              MMMMP  .MMM  dP    dP  88  .dP   .d8888b.
#              MMP  .MMMMM  88    88  88888"    88'  `88
#              M' .MMMMMMM  88.  .88  88  `8b.  88.  .88
#              M         M  `88888P'  dP   `YP  `88888P'
#              MMMMMMMMMMM    -*-  Created by Zuko  -*-
#
#              * * * * * * * * * * * * * * * * * * * * *
#              * -    - -   F.R.E.E.M.I.N.D   - -    - *
#              * -  Copyright © 2025 (Z) Programing  - *
#              *    -  -  All Rights Reserved  -  -    *
#              * * * * * * * * * * * * * * * * * * * * *

#
from typing import Any, Optional

from PySide6.QtCore import QModelIndex, Qt, QDateTime, QSize, QRectF, QByteArray, QPoint
from PySide6.QtGui import QColor, QLinearGradient, QPainter, QBrush, QPen, QPixmap, QPainterPath, QPalette
from PySide6.QtSvg import QSvgRenderer
from PySide6.QtWidgets import QStyledItemDelegate, QWidget, QStyleOptionViewItem, QDoubleSpinBox, QDateEdit, QCheckBox, QLineEdit, QTextEdit, QProgressBar, QStyle, QApplication


class CellDelegate(QStyledItemDelegate):
    """Base delegate for table cells"""

    def __init__(self, parent=None):
        super().__init__(parent)


class NumericDelegate(CellDelegate):
    """Delegate for numeric values"""

    def __init__(self, parent=None, min_value=-1000000, max_value=1000000, decimals=2, step=0.1, suffix='', prefix=''):
        super().__init__(parent)
        self.min_value = min_value
        self.max_value = max_value
        self.decimals = decimals
        self.step = step
        self.suffix = suffix
        self.prefix = prefix

    def createEditor(self, parent: QWidget, option: QStyleOptionViewItem, index: QModelIndex) -> QWidget:
        """Create a spin box for editing numeric values"""
        editor = QDoubleSpinBox(parent)
        editor.setMinimum(self.min_value)
        editor.setMaximum(self.max_value)
        editor.setDecimals(self.decimals)
        editor.setSingleStep(self.step)
        editor.setSuffix(self.suffix)
        editor.setPrefix(self.prefix)
        return editor

    def setEditorData(self, editor: QWidget, index: QModelIndex) -> None:
        """Set the editor data"""
        value = index.model().data(index, Qt.EditRole)
        try:
            editor.setValue(float(value) if value is not None else 0.0)
        except (ValueError, TypeError):
            editor.setValue(0.0)

    def setModelData(self, editor: QWidget, model: Any, index: QModelIndex) -> None:
        """Set the model data"""
        model.setData(index, editor.value(), Qt.EditRole)

    def displayText(self, value: Any, locale: Any) -> str:
        """Format the display text"""
        try:
            num_value = float(value) if value is not None else 0.0
            # Kiểm tra số nguyên và loại bỏ phần thập phân nếu là số nguyên
            if num_value.is_integer():
                formatted = f'{self.prefix}{int(num_value)}{self.suffix}'
            else:
                formatted = f'{self.prefix}{num_value:.{self.decimals}f}{self.suffix}'
            return formatted
        except (ValueError, TypeError):
            return super().displayText(value, locale)


class DateDelegate(CellDelegate):
    """Delegate for date values"""

    def __init__(self, parent=None, format='yyyy-MM-dd'):
        super().__init__(parent)
        self.format = format

    def createEditor(self, parent: QWidget, option: QStyleOptionViewItem, index: QModelIndex) -> QWidget:
        """Create a date edit for editing date values"""
        editor = QDateEdit(parent)
        editor.setCalendarPopup(True)
        editor.setDisplayFormat(self.format)
        return editor

    def setEditorData(self, editor: QWidget, index: QModelIndex) -> None:
        """Set the editor data"""
        value = index.model().data(index, Qt.EditRole)
        if value is None:
            editor.setDate(QDateTime.currentDateTime().date())
        elif isinstance(value, QDateTime):
            editor.setDate(value.date())
        else:
            try:
                dt = QDateTime.fromString(str(value), self.format)
                editor.setDate(dt.date())
            except (ValueError, TypeError):
                editor.setDate(QDateTime.currentDateTime().date())

    def setModelData(self, editor: QWidget, model: Any, index: QModelIndex) -> None:
        """Set the model data"""
        model.setData(index, editor.date().toString(self.format), Qt.EditRole)

    def displayText(self, value: Any, locale: Any) -> str:
        """Format the display text"""
        if value is None:
            return ''
        elif isinstance(value, QDateTime):
            return value.toString(self.format)
        else:
            return str(value)


class BooleanDelegate(CellDelegate):
    """Delegate for boolean values"""

    def __init__(self, parent=None, true_text='Yes', false_text='No'):
        super().__init__(parent)
        self.true_text = true_text
        self.false_text = false_text

    def createEditor(self, parent: QWidget, option: QStyleOptionViewItem, index: QModelIndex) -> QWidget:
        """Create a checkbox for editing boolean values"""
        editor = QCheckBox(parent)
        editor.setAutoFillBackground(True)
        return editor

    def setEditorData(self, editor: QWidget, index: QModelIndex) -> None:
        """Set the editor data"""
        value = index.model().data(index, Qt.EditRole)
        editor.setChecked(bool(value))

    def setModelData(self, editor: QWidget, model: Any, index: QModelIndex) -> None:
        """Set the model data"""
        model.setData(index, editor.isChecked(), Qt.EditRole)

    def displayText(self, value: Any, locale: Any) -> str:
        """Format the display text"""
        if value is None:
            return self.false_text
        return self.true_text if bool(value) else self.false_text

    def paint(self, painter: Any, option: QStyleOptionViewItem, index: QModelIndex) -> None:
        """Custom paint method to draw checkbox"""
        # For custom checkbox rendering, uncomment and implement
        # self.drawCheck(painter, option, option.rect,
        #               Qt.Checked if bool(index.data(Qt.EditRole)) else Qt.Unchecked)
        super().paint(painter, option, index)


class LineDelegate(CellDelegate):
    """Delegate for single-line text values"""

    def __init__(self, parent=None, max_length=None, placeholder=''):
        super().__init__(parent)
        self.max_length = max_length
        self.placeholder = placeholder

    def createEditor(self, parent, option, index):
        editor = QLineEdit(parent)
        if self.max_length:
            editor.setMaxLength(self.max_length)
        editor.setPlaceholderText(self.placeholder)
        return editor

    def setEditorData(self, editor, index):
        value = index.model().data(index, Qt.EditRole) or ''
        editor.setText(str(value))

    def setModelData(self, editor, model, index):
        model.setData(index, editor.text(), Qt.EditRole)


class TextDelegate(CellDelegate):
    """Delegate for multi-line text values"""

    def __init__(self, parent=None, placeholder=''):
        super().__init__(parent)
        self.placeholder = placeholder

    def createEditor(self, parent, option, index):
        editor = QTextEdit(parent)
        editor.setPlaceholderText(self.placeholder)
        return editor

    def setEditorData(self, editor, index):
        value = index.model().data(index, Qt.EditRole) or ''
        editor.setPlainText(str(value))

    def setModelData(self, editor, model, index):
        model.setData(index, editor.toPlainText(), Qt.EditRole)

    def sizeHint(self, option, index):
        # Đảm bảo đủ không gian cho text dài
        size = super().sizeHint(option, index)
        size.setHeight(max(size.height(), 80))
        return size


class ProgressDelegate(CellDelegate):
    """Delegate for progress bar values"""

    def __init__(self, parent=None):
        super().__init__(parent)

    def paint(self, painter: Any, option: QStyleOptionViewItem, index: QModelIndex) -> None:
        """Paint the progress bar"""
        progress = index.model().data(index, Qt.DisplayRole)
        if not isinstance(progress, (int, float)):
            super().paint(painter, option, index)
            return

        progress_bar_option = QStyleOptionViewItem(option)
        progress_bar_option.rect = option.rect
        progress_bar_option.state = option.state | QStyle.State_Active
        progress_bar_option.progress = int(progress)
        progress_bar_option.text = f'{int(progress)}%'
        progress_bar_option.displayAlignment = Qt.AlignCenter

        progress_bar = QProgressBar()
        progress_bar.setRange(0, 100)
        progress_bar.setValue(int(progress))

        painter.save()
        painter.translate(option.rect.topLeft())
        progress_bar.resize(option.rect.size())
        progress_bar.render(painter, QPoint(0, 0))
        painter.restore()

    def createEditor(self, parent: QWidget, option: QStyleOptionViewItem, index: QModelIndex) -> QWidget:
        """Create a spin box for editing progress values"""
        editor = QDoubleSpinBox(parent)
        editor.setMinimum(0)
        editor.setMaximum(100)
        editor.setDecimals(0)
        return editor

    def setEditorData(self, editor: QWidget, index: QModelIndex) -> None:
        """Set the editor data"""
        value = index.model().data(index, Qt.EditRole)
        try:
            editor.setValue(int(value) if value is not None else 0)
        except (ValueError, TypeError):
            editor.setValue(0)

    def setModelData(self, editor: QWidget, model: Any, index: QModelIndex) -> None:
        """Set the model data"""
        model.setData(index, int(editor.value()), Qt.EditRole)


class ProgressBarDelegate(CellDelegate):
    """
    Advanced Delegate for progress bar with custom colors and gradients.
    """

    def __init__(self, parent=None, color=None, use_gradient=False):
        super().__init__(parent)
        self.base_color = color
        self.use_gradient = use_gradient
        self.ranges = []  # List of (min_pct, max_pct, color)

    def get_color(self) -> QColor:
        if self.base_color:
            return QColor(self.base_color)
        # Default to theme primary color
        app = QApplication.instance()
        if app:
            return app.palette().color(QPalette.Highlight)
        return QColor('#3b82f6')  # Fallback

    def set_base_color(self, color: QColor):
        self.base_color = color

    def set_gradient(self, enabled: bool):
        self.use_gradient = enabled

    def add_range(self, min_pct: float, max_pct: float, color: QColor):
        # Validate overlap
        for start, end, _ in self.ranges:
            # Check if new range overlaps with existing
            if max_pct > start and min_pct < end:
                raise ValueError(f'Range ({min_pct}, {max_pct}) overlaps with existing range ({start}, {end})')
        self.ranges.append((min_pct, max_pct, QColor(color)))
        self.ranges.sort(key=lambda x: x[0])

    def paint(self, painter: QPainter, option: QStyleOptionViewItem, index: QModelIndex) -> None:
        progress = index.data(Qt.DisplayRole)
        if progress is None:
            return

        try:
            progress = float(progress)
        except (ValueError, TypeError):
            return

        progress = max(0, min(100, progress))

        painter.save()
        painter.setRenderHint(QPainter.Antialiasing)

        # Draw background
        rect = QRectF(option.rect)
        rect.adjust(4, 4, -4, -4)  # Padding

        # Track
        track_color = QColor(200, 200, 200, 50)
        painter.setPen(Qt.NoPen)
        painter.setBrush(track_color)
        painter.drawRoundedRect(rect, 4, 4)

        # Determine bar color
        bar_color = self.get_color()

        # Check ranges
        for start, end, color in self.ranges:
            if start <= progress <= end:
                bar_color = color
                break

        # Draw bar
        if progress > 0:
            width = rect.width() * (progress / 100.0)
            bar_rect = QRectF(rect.x(), rect.y(), width, rect.height())

            if self.use_gradient:
                gradient = QLinearGradient(bar_rect.topLeft(), bar_rect.topRight())
                c1 = QColor(bar_color)
                c1.setAlpha(0)  # Fade from transparent (0% opacity)
                c2 = QColor(bar_color)
                c2.setAlpha(255)  # To full color (100% opacity)
                gradient.setColorAt(0, c1)
                gradient.setColorAt(1, c2)
                painter.setBrush(gradient)
            else:
                painter.setBrush(bar_color)

            painter.drawRoundedRect(bar_rect, 4, 4)

        # Draw text
        text = f'{int(progress)}%'
        painter.setPen(option.palette.text().color())
        painter.drawText(rect, Qt.AlignCenter, text)

        painter.restore()

    def createEditor(self, parent: QWidget, option: QStyleOptionViewItem, index: QModelIndex) -> QWidget:
        editor = QDoubleSpinBox(parent)
        editor.setMinimum(0)
        editor.setMaximum(100)
        editor.setDecimals(0)
        return editor

    def setEditorData(self, editor: QWidget, index: QModelIndex) -> None:
        value = index.model().data(index, Qt.EditRole)
        try:
            editor.setValue(int(value) if value is not None else 0)
        except (ValueError, TypeError):
            editor.setValue(0)

    def setModelData(self, editor: QWidget, model: Any, index: QModelIndex) -> None:
        model.setData(index, int(editor.value()), Qt.EditRole)


class IconBooleanDelegate(BooleanDelegate):
    """
    Delegate for boolean values using SVG icons.
    """

    YES_SVG = """<svg width="100%" height="100%" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
 <path d="M7.5 12L10.5 15L16.5 9M22 12C22 17.5228 17.5228 22 12 22C6.47715 22 2 17.5228 2 12C2 6.47715 6.47715 2 12 2C17.5228 2 22 6.47715 22 12Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
 </svg>"""

    NO_SVG = """<svg width="100%" height="100%" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
 <path d="M15 9L9 15M9 9L15 15M22 12C22 17.5228 17.5228 22 12 22C6.47715 22 2 17.5228 2 12C2 6.47715 6.47715 2 12 2C17.5228 2 22 6.47715 22 12Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
 </svg>"""

    def __init__(self, parent=None, yes_color=None, no_color=None):
        super().__init__(parent)
        self.yes_color = yes_color if yes_color else QColor('#22c55e')  # Green
        self.no_color = no_color if no_color else QColor('#ef4444')  # Red
        self.renderer = QSvgRenderer()

    def set_yes_color(self, color: QColor):
        self.yes_color = color

    def set_no_color(self, color: QColor):
        self.no_color = color

    def paint(self, painter: QPainter, option: QStyleOptionViewItem, index: QModelIndex) -> None:
        value = index.data(Qt.EditRole)

        painter.save()
        painter.setRenderHint(QPainter.Antialiasing)

        # Determine state
        is_yes = bool(value)

        # Set color
        color = self.yes_color if is_yes else self.no_color
        svg_content = self.YES_SVG if is_yes else self.NO_SVG

        # Replace currentColor with actual color
        color_hex = color.name()
        svg_content = svg_content.replace('currentColor', color_hex)

        self.renderer.load(QByteArray(svg_content.encode('utf-8')))

        # Calculate rect to center the icon
        # Keep aspect ratio 1:1
        size = min(option.rect.width(), option.rect.height()) - 8  # Padding
        if size < 0:
            size = 0

        x = option.rect.x() + (option.rect.width() - size) / 2
        y = option.rect.y() + (option.rect.height() - size) / 2
        target_rect = QRectF(x, y, size, size)

        self.renderer.render(painter, target_rect)

        painter.restore()
