# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'dark-table.ui'
##
## Created by: Qt User Interface Compiler version 6.7.3
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import QCoreApplication, QDate, QDateTime, QLocale, QMetaObject, QObject, QPoint, QRect, QSize, QTime, QUrl, Qt
from PySide6.QtGui import (
    QBrush,
    QColor,
    QConicalGradient,
    QCursor,
    QFont,
    QFontDatabase,
    QGradient,
    QIcon,
    QImage,
    QKeySequence,
    QLinearGradient,
    QPainter,
    QPalette,
    QPixmap,
    QRadialGradient,
    QTransform,
)
from PySide6.QtWidgets import (
    QAbstractItemView,
    QApplication,
    QComboBox,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QMainWindow,
    QPushButton,
    QSizePolicy,
    QSpacerItem,
    QStatusBar,
    QTableView,
    QVBoxLayout,
    QWidget,
)


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName('MainWindow')
        MainWindow.resize(800, 600)
        MainWindow.setMinimumSize(QSize(0, 0))
        MainWindow.setStyleSheet(
            'QWidget {\n'
            '    background-color: #1e1e1e;\n'
            '    color: #ffffff;\n'
            '}\n'
            '\n'
            'QTableView {\n'
            '    background-color: #1e1e1e;\n'
            '    alternate-background-color: #2d2d30;\n'
            '    gridline-color: #3f3f46;\n'
            '    color: #ffffff;\n'
            '    border: 1px solid #3f3f46;\n'
            '}\n'
            '\n'
            'QTableView::item:selected {\n'
            '    background-color: #264f78;\n'
            '}\n'
            '\n'
            'QHeaderView::section {\n'
            '    background-color: #333333;\n'
            '    color: #ffffff;\n'
            '    padding: 4px;\n'
            '    border: 1px solid #3f3f46;\n'
            '}\n'
            '\n'
            'QComboBox, QLineEdit {\n'
            '    background-color: #333333;\n'
            '    color: #ffffff;\n'
            '    border: 1px solid #3f3f46;\n'
            '    padding: 2px;\n'
            '}\n'
            '\n'
            'QPushButton {\n'
            '    background-color: #333333;\n'
            '    color: #ffffff;\n'
            '    border: 1px solid #3f3f46;\n'
            '    padding: 4px 8px;\n'
            '}\n'
            '\n'
            'QPushButton:hover {\n'
            '    background-color: #3e3e42;\n'
            '}\n'
            '\n'
            'QPushButton:pressed {\n'
            '    background-color: #007acc;\n'
            '}'
        )
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName('centralwidget')
        self.verticalLayout = QVBoxLayout(self.centralwidget)
        self.verticalLayout.setObjectName('verticalLayout')
        self.top_toolbar = QHBoxLayout()
        self.top_toolbar.setObjectName('top_toolbar')
        self.columnVisibilityButton = QPushButton(self.centralwidget)
        self.columnVisibilityButton.setObjectName('columnVisibilityButton')
        icon = QIcon(QIcon.fromTheme(QIcon.ThemeIcon.FormatJustifyCenter))
        self.columnVisibilityButton.setIcon(icon)

        self.top_toolbar.addWidget(self.columnVisibilityButton)

        self.entriesPerPageComboBox = QComboBox(self.centralwidget)
        self.entriesPerPageComboBox.addItem('')
        self.entriesPerPageComboBox.addItem('')
        self.entriesPerPageComboBox.addItem('')
        self.entriesPerPageComboBox.addItem('')
        self.entriesPerPageComboBox.setObjectName('entriesPerPageComboBox')
        self.entriesPerPageComboBox.setMinimumSize(QSize(50, 0))

        self.top_toolbar.addWidget(self.entriesPerPageComboBox)

        self.entriesLabel = QLabel(self.centralwidget)
        self.entriesLabel.setObjectName('entriesLabel')

        self.top_toolbar.addWidget(self.entriesLabel)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.top_toolbar.addItem(self.horizontalSpacer)

        self.searchLabel = QLabel(self.centralwidget)
        self.searchLabel.setObjectName('searchLabel')

        self.top_toolbar.addWidget(self.searchLabel)

        self.searchInput = QLineEdit(self.centralwidget)
        self.searchInput.setObjectName('searchInput')
        self.searchInput.setMinimumSize(QSize(200, 0))

        self.top_toolbar.addWidget(self.searchInput)

        self.typeComboBox = QComboBox(self.centralwidget)
        self.typeComboBox.addItem('')
        self.typeComboBox.addItem('')
        self.typeComboBox.addItem('')
        self.typeComboBox.addItem('')
        self.typeComboBox.addItem('')
        self.typeComboBox.addItem('')
        self.typeComboBox.setObjectName('typeComboBox')

        self.top_toolbar.addWidget(self.typeComboBox)

        self.verticalLayout.addLayout(self.top_toolbar)

        self.tableView = QTableView(self.centralwidget)
        self.tableView.setObjectName('tableView')
        self.tableView.setAlternatingRowColors(True)
        self.tableView.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.tableView.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.tableView.setSortingEnabled(True)
        self.tableView.horizontalHeader().setStretchLastSection(True)
        self.tableView.verticalHeader().setVisible(False)

        self.verticalLayout.addWidget(self.tableView)

        self.bottom_toolbar = QHBoxLayout()
        self.bottom_toolbar.setObjectName('bottom_toolbar')
        self.infoLabel = QLabel(self.centralwidget)
        self.infoLabel.setObjectName('infoLabel')

        self.bottom_toolbar.addWidget(self.infoLabel)

        self.horizontalSpacer_2 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.bottom_toolbar.addItem(self.horizontalSpacer_2)

        self.backwardLayout = QHBoxLayout()
        self.backwardLayout.setSpacing(3)
        self.backwardLayout.setObjectName('backwardLayout')
        self.backwardLayout.setContentsMargins(0, 0, 0, 0)
        self.firstPageButton = QPushButton(self.centralwidget)
        self.firstPageButton.setObjectName('firstPageButton')
        self.firstPageButton.setMaximumSize(QSize(30, 16777215))
        icon1 = QIcon(QIcon.fromTheme(QIcon.ThemeIcon.MediaSeekBackward))
        self.firstPageButton.setIcon(icon1)

        self.backwardLayout.addWidget(self.firstPageButton)

        self.prevPageButton = QPushButton(self.centralwidget)
        self.prevPageButton.setObjectName('prevPageButton')
        self.prevPageButton.setMaximumSize(QSize(30, 16777215))
        icon2 = QIcon(QIcon.fromTheme(QIcon.ThemeIcon.MediaSkipBackward))
        self.prevPageButton.setIcon(icon2)

        self.backwardLayout.addWidget(self.prevPageButton)

        self.bottom_toolbar.addLayout(self.backwardLayout)

        self.pagesLayout = QHBoxLayout()
        self.pagesLayout.setSpacing(3)
        self.pagesLayout.setObjectName('pagesLayout')
        self.pagesLayout.setContentsMargins(0, 0, 0, 0)
        self.page1Button = QPushButton(self.centralwidget)
        self.page1Button.setObjectName('page1Button')
        self.page1Button.setMaximumSize(QSize(30, 16777215))
        self.page1Button.setStyleSheet('background-color: #007acc;')

        self.pagesLayout.addWidget(self.page1Button)

        self.page2Button = QPushButton(self.centralwidget)
        self.page2Button.setObjectName('page2Button')
        self.page2Button.setMaximumSize(QSize(30, 16777215))

        self.pagesLayout.addWidget(self.page2Button)

        self.pushButton = QPushButton(self.centralwidget)
        self.pushButton.setObjectName('pushButton')

        self.pagesLayout.addWidget(self.pushButton)

        self.bottom_toolbar.addLayout(self.pagesLayout)

        self.fowardLayout = QHBoxLayout()
        self.fowardLayout.setSpacing(3)
        self.fowardLayout.setObjectName('fowardLayout')
        self.fowardLayout.setContentsMargins(0, 0, 0, 0)
        self.nextPageButton = QPushButton(self.centralwidget)
        self.nextPageButton.setObjectName('nextPageButton')
        self.nextPageButton.setMaximumSize(QSize(30, 16777215))
        icon3 = QIcon(QIcon.fromTheme(QIcon.ThemeIcon.MediaSkipForward))
        self.nextPageButton.setIcon(icon3)

        self.fowardLayout.addWidget(self.nextPageButton)

        self.lastPageButton = QPushButton(self.centralwidget)
        self.lastPageButton.setObjectName('lastPageButton')
        self.lastPageButton.setMaximumSize(QSize(30, 16777215))
        icon4 = QIcon(QIcon.fromTheme(QIcon.ThemeIcon.MediaSeekForward))
        self.lastPageButton.setIcon(icon4)

        self.fowardLayout.addWidget(self.lastPageButton)

        self.bottom_toolbar.addLayout(self.fowardLayout)

        self.verticalLayout.addLayout(self.bottom_toolbar)

        MainWindow.setCentralWidget(self.centralwidget)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName('statusbar')
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)

        QMetaObject.connectSlotsByName(MainWindow)

    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate('MainWindow', 'Employee Management', None))
        self.columnVisibilityButton.setText('')
        self.entriesPerPageComboBox.setItemText(0, QCoreApplication.translate('MainWindow', '10', None))
        self.entriesPerPageComboBox.setItemText(1, QCoreApplication.translate('MainWindow', '25', None))
        self.entriesPerPageComboBox.setItemText(2, QCoreApplication.translate('MainWindow', '50', None))
        self.entriesPerPageComboBox.setItemText(3, QCoreApplication.translate('MainWindow', '100', None))

        # if QT_CONFIG(tooltip)
        self.entriesPerPageComboBox.setToolTip(QCoreApplication.translate('MainWindow', 'Items per page', None))
        # endif // QT_CONFIG(tooltip)
        self.entriesLabel.setText(QCoreApplication.translate('MainWindow', '/ page', None))
        self.searchLabel.setText(QCoreApplication.translate('MainWindow', 'Search:', None))
        self.typeComboBox.setItemText(0, QCoreApplication.translate('MainWindow', 'All Types', None))
        self.typeComboBox.setItemText(1, QCoreApplication.translate('MainWindow', 'Number', None))
        self.typeComboBox.setItemText(2, QCoreApplication.translate('MainWindow', 'One Line Text', None))
        self.typeComboBox.setItemText(3, QCoreApplication.translate('MainWindow', 'Text', None))
        self.typeComboBox.setItemText(4, QCoreApplication.translate('MainWindow', 'DateTime', None))
        self.typeComboBox.setItemText(5, QCoreApplication.translate('MainWindow', 'Boolean', None))

        self.infoLabel.setText(QCoreApplication.translate('MainWindow', '1 - 10 of 57 entries', None))
        self.firstPageButton.setText('')
        self.prevPageButton.setText('')
        self.page1Button.setText(QCoreApplication.translate('MainWindow', '1', None))
        self.page2Button.setText(QCoreApplication.translate('MainWindow', '2', None))
        self.pushButton.setText(QCoreApplication.translate('MainWindow', '...', None))
        self.nextPageButton.setText('')
        self.lastPageButton.setText('')

    # retranslateUi
