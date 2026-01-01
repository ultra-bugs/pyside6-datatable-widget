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

from PySide6.QtCore import QModelIndex, Qt, QDateTime, QSize
from PySide6.QtWidgets import QStyledItemDelegate, QWidget, QStyleOptionViewItem, QDoubleSpinBox, QDateEdit, QCheckBox, QLineEdit, QTextEdit


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
