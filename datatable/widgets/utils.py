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
from PySide6.QtCore import QSize
from PySide6.QtWidgets import QApplication, QTableView, QWidget


class DatatableContainer(QWidget):
    """Container for DataTable widgets
    This class serves as a base class for creating containers that hold
    DataTable widgets.
    """

    pass


class DataTableView(QTableView):
    """QTableView subclass that caps sizeHint to available screen size.

    Prevents row-count-driven size from propagating up and forcing the
    parent window to resize when data changes.
    """

    def sizeHint(self) -> QSize:
        screen = QApplication.primaryScreen()
        if screen:
            avail = screen.availableGeometry()
            return QSize(avail.width(), avail.height())
        return super().sizeHint()
