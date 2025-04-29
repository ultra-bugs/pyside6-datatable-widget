# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'untitled.ui'
##
## Created by: Qt User Interface Compiler version 6.9.0
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QAbstractItemView, QApplication, QComboBox, QHBoxLayout,
    QHeaderView, QLabel, QLineEdit, QPushButton,
    QSizePolicy, QSpacerItem, QSpinBox, QVBoxLayout,
    QWidget)

from ..widgets.utils import (DataTableView, DatatableContainer)

class Ui_DataTable(object):
    def setupUi(self, DataTable):
        if not DataTable.objectName():
            DataTable.setObjectName(u"DataTable")
        DataTable.resize(830, 545)
        DataTable.setMinimumSize(QSize(640, 480))
        DataTable.setStyleSheet(u"QWidget {\n"
"    background-color: #1e1e1e;\n"
"    color: #ffffff;\n"
"}\n"
"\n"
"QTableView {\n"
"    background-color: #1e1e1e;\n"
"    alternate-background-color: #2d2d30;\n"
"    gridline-color: #3f3f46;\n"
"    color: #ffffff;\n"
"    border: 1px solid #3f3f46;\n"
"}\n"
"\n"
"QTableView::item:selected {\n"
"    background-color: #264f78;\n"
"}\n"
"\n"
"QHeaderView::section {\n"
"    background-color: #333333;\n"
"    color: #ffffff;\n"
"    padding: 4px;\n"
"    border: 1px solid #3f3f46;\n"
"}\n"
"\n"
"QComboBox, QLineEdit, QSpinBox {\n"
"    background-color: #333333;\n"
"    color: #ffffff;\n"
"    border: 1px solid #3f3f46;\n"
"    padding: 2px;\n"
"}\n"
"\n"
"QPushButton {\n"
"    background-color: #333333;\n"
"    color: #ffffff;\n"
"    border: 1px solid #3f3f46;\n"
"    padding: 4px 8px;\n"
"}\n"
"\n"
"QPushButton:hover {\n"
"    background-color: #3e3e42;\n"
"}\n"
"\n"
"QPushButton:pressed {\n"
"    background-color: #007acc;\n"
"}\n"
"/* \u0110\u1ea3m b\u1ea3o c\u00e1c container widgets c\u00f3"
                        " background \u0111\u00fang */\n"
"QWidget#backwardLayout, QWidget#pagesLayout, QWidget#fowardLayout {\n"
"    background-color: transparent;\n"
"}\n"
"\n"
"/* Fixes cho DataTableView v\u00e0 container c\u1ee7a n\u00f3 */\n"
"DataTableView, DatatableContainer {\n"
"    background-color: #1e1e1e;\n"
"    color: #ffffff;\n"
"}\n"
"\n"
"WidgetSwitcher {\n"
"    background-color: transparent;\n"
"}")
        self.verticalLayout = QVBoxLayout(DataTable)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.top_toolbar = QHBoxLayout()
        self.top_toolbar.setObjectName(u"top_toolbar")
        self.columnVisibilityButton = QPushButton(DataTable)
        self.columnVisibilityButton.setObjectName(u"columnVisibilityButton")
        icon = QIcon(QIcon.fromTheme(QIcon.ThemeIcon.FormatJustifyCenter))
        self.columnVisibilityButton.setIcon(icon)

        self.top_toolbar.addWidget(self.columnVisibilityButton)

        self.rowsPerPageCombo = QComboBox(DataTable)
        self.rowsPerPageCombo.addItem("")
        self.rowsPerPageCombo.addItem("")
        self.rowsPerPageCombo.addItem("")
        self.rowsPerPageCombo.addItem("")
        self.rowsPerPageCombo.setObjectName(u"rowsPerPageCombo")
        self.rowsPerPageCombo.setMinimumSize(QSize(50, 0))

        self.top_toolbar.addWidget(self.rowsPerPageCombo)

        self.rowsPerPageLabel = QLabel(DataTable)
        self.rowsPerPageLabel.setObjectName(u"rowsPerPageLabel")

        self.top_toolbar.addWidget(self.rowsPerPageLabel)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.top_toolbar.addItem(self.horizontalSpacer)

        self.searchLabel = QLabel(DataTable)
        self.searchLabel.setObjectName(u"searchLabel")

        self.top_toolbar.addWidget(self.searchLabel)

        self.searchLineEdit = QLineEdit(DataTable)
        self.searchLineEdit.setObjectName(u"searchLineEdit")
        self.searchLineEdit.setMinimumSize(QSize(200, 0))

        self.top_toolbar.addWidget(self.searchLineEdit)

        self.typeComboBox = QComboBox(DataTable)
        self.typeComboBox.addItem("")
        self.typeComboBox.addItem("")
        self.typeComboBox.addItem("")
        self.typeComboBox.addItem("")
        self.typeComboBox.addItem("")
        self.typeComboBox.addItem("")
        self.typeComboBox.setObjectName(u"typeComboBox")

        self.top_toolbar.addWidget(self.typeComboBox)


        self.verticalLayout.addLayout(self.top_toolbar)

        self.tableView = DataTableView(DataTable)
        self.tableView.setObjectName(u"tableView")
        self.tableView.setAlternatingRowColors(True)
        self.tableView.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.tableView.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.tableView.setSortingEnabled(True)
        self.tableView.horizontalHeader().setStretchLastSection(True)
        self.tableView.verticalHeader().setVisible(False)

        self.verticalLayout.addWidget(self.tableView)

        self.bottom_toolbar = QHBoxLayout()
        self.bottom_toolbar.setObjectName(u"bottom_toolbar")
        self.totalEntriesLabel = QLabel(DataTable)
        self.totalEntriesLabel.setObjectName(u"totalEntriesLabel")

        self.bottom_toolbar.addWidget(self.totalEntriesLabel)

        self.horizontalSpacer_2 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.bottom_toolbar.addItem(self.horizontalSpacer_2)

        self.backwardLayout = QWidget(DataTable)
        self.backwardLayout.setObjectName(u"backwardLayout")
        self._backwardLayout = QHBoxLayout(self.backwardLayout)
        self._backwardLayout.setSpacing(3)
        self._backwardLayout.setObjectName(u"_backwardLayout")
        self._backwardLayout.setContentsMargins(0, 0, 0, 0)
        self.firstPageButton = QPushButton(self.backwardLayout)
        self.firstPageButton.setObjectName(u"firstPageButton")
        self.firstPageButton.setMaximumSize(QSize(30, 16777215))
        icon1 = QIcon(QIcon.fromTheme(QIcon.ThemeIcon.MediaSeekBackward))
        self.firstPageButton.setIcon(icon1)

        self._backwardLayout.addWidget(self.firstPageButton)

        self.prevPageButton = QPushButton(self.backwardLayout)
        self.prevPageButton.setObjectName(u"prevPageButton")
        self.prevPageButton.setMaximumSize(QSize(30, 16777215))
        icon2 = QIcon(QIcon.fromTheme(QIcon.ThemeIcon.MediaSkipBackward))
        self.prevPageButton.setIcon(icon2)

        self._backwardLayout.addWidget(self.prevPageButton)


        self.bottom_toolbar.addWidget(self.backwardLayout)

        self.pageSpinBox = QSpinBox(DataTable)
        self.pageSpinBox.setObjectName(u"pageSpinBox")
        self.pageSpinBox.setFrame(False)

        self.bottom_toolbar.addWidget(self.pageSpinBox)

        self.pagesLayout = QWidget(DataTable)
        self.pagesLayout.setObjectName(u"pagesLayout")
        self._pagesLayout = QHBoxLayout(self.pagesLayout)
        self._pagesLayout.setSpacing(3)
        self._pagesLayout.setObjectName(u"_pagesLayout")
        self._pagesLayout.setContentsMargins(0, 0, 0, 0)
        self.page1Button = QPushButton(self.pagesLayout)
        self.page1Button.setObjectName(u"page1Button")
        self.page1Button.setMaximumSize(QSize(30, 16777215))
        self.page1Button.setStyleSheet(u"background-color: #007acc;")

        self._pagesLayout.addWidget(self.page1Button)

        self.page2Button = QPushButton(self.pagesLayout)
        self.page2Button.setObjectName(u"page2Button")
        self.page2Button.setMaximumSize(QSize(30, 16777215))

        self._pagesLayout.addWidget(self.page2Button)

        self.pushButton = QPushButton(self.pagesLayout)
        self.pushButton.setObjectName(u"pushButton")
        self.pushButton.setGeometry(QRect(80, 60, 27, 27))

        self._pagesLayout.addWidget(self.pushButton)


        self.bottom_toolbar.addWidget(self.pagesLayout)

        self.fowardLayout = QWidget(DataTable)
        self.fowardLayout.setObjectName(u"fowardLayout")
        self._fowardLayout = QHBoxLayout(self.fowardLayout)
        self._fowardLayout.setSpacing(3)
        self._fowardLayout.setObjectName(u"_fowardLayout")
        self._fowardLayout.setContentsMargins(0, 0, 0, 0)
        self.nextPageButton = QPushButton(self.fowardLayout)
        self.nextPageButton.setObjectName(u"nextPageButton")
        self.nextPageButton.setMaximumSize(QSize(30, 16777215))
        icon3 = QIcon(QIcon.fromTheme(QIcon.ThemeIcon.MediaSkipForward))
        self.nextPageButton.setIcon(icon3)

        self._fowardLayout.addWidget(self.nextPageButton)

        self.lastPageButton = QPushButton(self.fowardLayout)
        self.lastPageButton.setObjectName(u"lastPageButton")
        self.lastPageButton.setMaximumSize(QSize(30, 16777215))
        icon4 = QIcon(QIcon.fromTheme(QIcon.ThemeIcon.MediaSeekForward))
        self.lastPageButton.setIcon(icon4)

        self._fowardLayout.addWidget(self.lastPageButton)


        self.bottom_toolbar.addWidget(self.fowardLayout)


        self.verticalLayout.addLayout(self.bottom_toolbar)


        self.retranslateUi(DataTable)

        QMetaObject.connectSlotsByName(DataTable)
    # setupUi

    def retranslateUi(self, DataTable):
        DataTable.setWindowTitle(QCoreApplication.translate("DataTable", u"Form", None))
        self.columnVisibilityButton.setText("")
        self.rowsPerPageCombo.setItemText(0, QCoreApplication.translate("DataTable", u"10", None))
        self.rowsPerPageCombo.setItemText(1, QCoreApplication.translate("DataTable", u"25", None))
        self.rowsPerPageCombo.setItemText(2, QCoreApplication.translate("DataTable", u"50", None))
        self.rowsPerPageCombo.setItemText(3, QCoreApplication.translate("DataTable", u"100", None))

        self.rowsPerPageLabel.setText(QCoreApplication.translate("DataTable", u"/ page", None))
        self.searchLabel.setText(QCoreApplication.translate("DataTable", u"Search:", None))
        self.typeComboBox.setItemText(0, QCoreApplication.translate("DataTable", u"All Types", None))
        self.typeComboBox.setItemText(1, QCoreApplication.translate("DataTable", u"Number", None))
        self.typeComboBox.setItemText(2, QCoreApplication.translate("DataTable", u"One Line Text", None))
        self.typeComboBox.setItemText(3, QCoreApplication.translate("DataTable", u"Text", None))
        self.typeComboBox.setItemText(4, QCoreApplication.translate("DataTable", u"DateTime", None))
        self.typeComboBox.setItemText(5, QCoreApplication.translate("DataTable", u"Boolean", None))

        self.totalEntriesLabel.setText(QCoreApplication.translate("DataTable", u"1 - 10", None))
        self.firstPageButton.setText("")
        self.prevPageButton.setText("")
        self.page1Button.setText(QCoreApplication.translate("DataTable", u"1", None))
        self.page2Button.setText(QCoreApplication.translate("DataTable", u"2", None))
        self.pushButton.setText(QCoreApplication.translate("DataTable", u"...", None))
        self.nextPageButton.setText("")
        self.lastPageButton.setText("")
    # retranslateUi

