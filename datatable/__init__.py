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
from .widgets.datatable import DataTable
from .widgets.utils import DataTableView
from .models.datatable_model import DataTableModel, DataType, SortOrder
from .models.delegates import CellDelegate, NumericDelegate, DateDelegate, BooleanDelegate

__version__ = '1.0.0'

__all__ = [
    'DataTable',
    'DataTableModel',
    'DataType',
    'SortOrder',
    'CellDelegate',
    'NumericDelegate',
    'DateDelegate',
    'BooleanDelegate',
    'DataTableView',
]
