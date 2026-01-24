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

from enum import Enum, auto
from typing import Any, Dict, List, Optional, Callable, Union, Tuple
import datetime

from PySide6.QtCore import QAbstractTableModel, QModelIndex, Qt, Signal, QObject, QSortFilterProxyModel


class DataType(Enum):
    """Enum representing data types for columns"""

    STRING = auto()
    NUMERIC = auto()
    DATE = auto()
    BOOLEAN = auto()
    PROGRESS = auto()
    CUSTOM = auto()
    PROGRESS_BAR = auto()  # New type for ProgressBarDelegate
    ICON_BOOLEAN = auto()  # New type for IconBooleanDelegate


class SortOrder(Enum):
    """Enum representing sort order"""

    ASCENDING = Qt.AscendingOrder
    DESCENDING = Qt.DescendingOrder
    NONE = -1


class DataTableModel(QAbstractTableModel):
    """Model for the DataTable widget"""

    rowExpandedCollapsed = Signal(int, bool)  # row, is_expanded

    def __init__(self, parent: Optional[QObject] = None):
        super().__init__(parent)
        self._data: List[Dict[str, Any]] = []
        self._headers: List[str] = []
        self._column_keys: List[str] = []
        self._column_types: Dict[str, DataType] = {}
        self._formatting_funcs: Dict[str, Callable] = {}
        self._editable_columns: Dict[str, bool] = {}
        self._visible_columns: List[str] = []
        self._search_funcs: Dict[str, Callable] = {}
        self._sort_funcs: Dict[str, Callable] = {}
        self._aggregation_funcs: Dict[str, Dict[str, Callable]] = {}
        self._expanded_rows: Dict[int, bool] = {}
        self._child_rows: Dict[int, List[Dict[str, Any]]] = {}

        # Flags
        self._row_collapsing_enabled = False
        self._child_row_key = ''  # Key for child rows in parent row

    def rowCount(self, parent=QModelIndex()) -> int:
        """Return the number of rows"""
        if parent.isValid():
            return 0
        return len(self._data)

    def columnCount(self, parent=QModelIndex()) -> int:
        """Return the number of columns"""
        if parent.isValid():
            return 0
        return len(self._visible_columns)

    def data(self, index: QModelIndex, role: int = Qt.DisplayRole) -> Any:
        """Return data for the given index and role"""
        if not index.isValid():
            return None

        row = index.row()
        col = index.column()
        col_key = self._visible_columns[col]

        # Special roles for expansion/collapsing
        if role == Qt.DecorationRole and col == 0 and self._row_collapsing_enabled:
            if row in self._child_rows:
                is_expanded = self._expanded_rows.get(row, False)
                # Return an icon indicating expanded/collapsed state
                # This should be handled by the view
                return is_expanded

        if role in (Qt.DisplayRole, Qt.EditRole):
            value = self._data[row].get(col_key)

            # Luôn áp dụng formatter nếu có, cho bất kỳ role nào
            if col_key in self._formatting_funcs:
                # Chỉ áp dụng formatter cho DisplayRole để giữ nguyên giá trị gốc cho EditRole
                if role == Qt.DisplayRole:
                    return self._formatting_funcs[col_key](value)
            return value

        return None

    def getRowData(self, row: int) -> Optional[Dict[str, Any]]:
        """Get the entire data for a specific row."""
        if 0 <= row < len(self._data):
            return self._data[row]
        return None

    def setData(self, index: QModelIndex, value: Any, role: int = Qt.EditRole) -> bool:
        """Set data for the given index and role"""
        if not index.isValid():
            return False

        row = index.row()
        col = index.column()

        # Handle row expansion/collapsing
        if role == Qt.UserRole and col == 0 and self._row_collapsing_enabled:
            return self.toggleRowExpanded(row)

        # Normal data editing
        if role == Qt.EditRole:
            col_key = self._visible_columns[col]

            if not self._editable_columns.get(col_key, False):
                return False

            self._data[row][col_key] = value
            self.dataChanged.emit(index, index, [role])  # TopLeft, BottomRight, Roles args
            return True

        return False

    def headerData(self, section: int, orientation: Qt.Orientation, role: int = Qt.DisplayRole) -> Any:
        """Return header data for the given section and orientation"""
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            if 0 <= section < len(self._headers):
                return self._headers[section]
        return None

    def flags(self, index: QModelIndex) -> Qt.ItemFlags:
        """Return flags for the given index"""
        if not index.isValid():
            return Qt.NoItemFlags

        flags = Qt.ItemIsEnabled | Qt.ItemIsSelectable
        col_key = self._visible_columns[index.column()]

        if self._editable_columns.get(col_key, False):
            flags |= Qt.ItemIsEditable

        return flags

    # Data Setup Methods
    def setModelData(self, data: List[Dict[str, Any]]) -> None:
        """Set the data for the model

        Args:
            data: List of dictionaries representing rows
        """
        self.beginResetModel()
        
        # Flatten data if row collapsing is enabled
        if self._row_collapsing_enabled and self._child_row_key:
            self._data = self._flattenData(data)
        else:
            self._data = data.copy()
        
        self._expanded_rows = {}
        self._child_rows = {}
        self.endResetModel()
    
    def _flattenData(self, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Flatten hierarchical data structure
        
        Args:
            data: Hierarchical data with child rows
            
        Returns:
            Flattened list with parent and child rows
        """
        flattened = []
        parent_index = 0
        
        for row in data:
            # Add parent row
            parent_row = row.copy()
            parent_row['_is_parent'] = True
            parent_row['_original_index'] = parent_index
            parent_row['_has_children'] = self._child_row_key in row and bool(row[self._child_row_key])
            
            # Remove child key from parent display
            if self._child_row_key in parent_row:
                del parent_row[self._child_row_key]
            
            flattened.append(parent_row)
            
            # *** FIX: Store parent's index BEFORE adding children ***
            parent_flattened_idx = len(flattened) - 1
            
            # Add child rows if they exist
            if self._child_row_key in row and row[self._child_row_key]:
                children = row[self._child_row_key]
                for child_idx, child in enumerate(children):
                    child_row = child.copy()
                    child_row['_is_child'] = True
                    child_row['_parent_index'] = parent_flattened_idx  # Use stored parent index
                    child_row['_child_index'] = child_idx
                    flattened.append(child_row)
            
            parent_index += 1
        
        return flattened

    def setColumns(self, columns: List[Tuple[str, str, DataType]]) -> None:
        """Set the columns for the model

        Args:
            columns: List of tuples (key, header, data_type)
        """
        self.beginResetModel()
        self._headers = []
        self._column_keys = []
        self._column_types = {}
        self._visible_columns = []

        for key, header, data_type in columns:
            self._headers.append(header)
            self._column_keys.append(key)
            self._column_types[key] = data_type
            self._visible_columns.append(key)

            # Set default formatting functions based on type
            if data_type == DataType.DATE:
                self.setFormattingFunction(key, lambda d: d.strftime('%Y-%m-%d') if isinstance(d, datetime.date) else str(d))
            elif data_type == DataType.NUMERIC:
                self.setFormattingFunction(
                    key, lambda n: str(int(n)) if isinstance(n, (int, float)) and float(n).is_integer() else (f'{n:,.2f}' if isinstance(n, (int, float)) else str(n))
                )
            elif data_type == DataType.BOOLEAN:
                self.setFormattingFunction(key, lambda b: 'Yes' if b else 'No')

            # Set default search functions
            self._setupDefaultSearchFunctions(key, data_type)

            # Set default sort functions
            self._setupDefaultSortFunctions(key, data_type)

        self.endResetModel()

    def setFormattingFunction(self, column_key: str, func: Callable) -> None:
        """Set formatting function for a column

        Args:
            column_key: Column key
            func: Formatting function
        """
        if column_key in self._column_keys:
            self._formatting_funcs[column_key] = func
            # Force refresh display of this column
            if column_key in self._visible_columns:
                col_index = self._visible_columns.index(column_key)
                topLeft = self.index(0, col_index)
                bottomRight = self.index(len(self._data) - 1 if self._data else 0, col_index)
                self.dataChanged.emit(topLeft, bottomRight, [Qt.DisplayRole])

    def setEditableColumns(self, editable_columns: Dict[str, bool]) -> None:
        """Set which columns are editable

        Args:
            editable_columns: Dictionary mapping column keys to boolean
        """
        self._editable_columns = editable_columns.copy()

    def setVisibleColumns(self, visible_columns: List[str]) -> None:
        """Set which columns are visible

        Args:
            visible_columns: List of column keys to display
        """
        # Ensure all columns are valid
        for col in visible_columns:
            if col not in self._column_keys:
                raise ValueError(f'Column {col} is not a valid column key')

        self.beginResetModel()
        self._visible_columns = visible_columns.copy()

        # Reorder and rebuild headers to match visible columns
        new_headers = []
        for col in visible_columns:
            try:
                idx = self._column_keys.index(col)
                if idx < len(self._headers):
                    new_headers.append(self._headers[idx])
                else:
                    # Fallback to using the column key as header
                    new_headers.append(col)
            except ValueError:
                # This should not happen due to the validation above
                new_headers.append(col)

        self._headers = new_headers

        self.endResetModel()

    def setSearchFunction(self, column_key: str, func: Callable) -> None:
        """Set search function for a column

        Args:
            column_key: Column key
            func: Search function that takes (value, search_term) and returns boolean
        """
        if column_key in self._column_keys:
            self._search_funcs[column_key] = func

    def setSortFunction(self, column_key: str, func: Callable) -> None:
        """Set sort function for a column

        Args:
            column_key: Column key
            func: Sort function that takes value and returns comparable
        """
        if column_key in self._column_keys:
            self._sort_funcs[column_key] = func

    def setAggregationFunction(self, column_key: str, agg_type: str, func: Callable) -> None:
        """Set aggregation function for a column

        Args:
            column_key: Column key
            agg_type: Aggregation type (sum, avg, count, etc.)
            func: Aggregation function that takes list of values
        """
        if column_key not in self._aggregation_funcs:
            self._aggregation_funcs[column_key] = {}
        self._aggregation_funcs[column_key][agg_type] = func

    def _setupDefaultSearchFunctions(self, key: str, data_type: DataType) -> None:
        """Set up default search functions based on data type"""
        if data_type == DataType.STRING:
            self._search_funcs[key] = lambda val, term: term.lower() in str(val).lower()
        elif data_type == DataType.NUMERIC:
            self._search_funcs[key] = lambda val, term: term in str(val)
        elif data_type == DataType.DATE:
            self._search_funcs[key] = lambda val, term: term in val.strftime('%Y-%m-%d') if isinstance(val, datetime.date) else False
        elif data_type == DataType.BOOLEAN:
            self._search_funcs[key] = lambda val, term: (term.lower() in 'yes' and val) or (term.lower() in 'no' and not val)
        elif data_type == DataType.ICON_BOOLEAN:
            self._search_funcs[key] = lambda val, term: (term.lower() in 'yes' and val) or (term.lower() in 'no' and not val)
        else:
            self._search_funcs[key] = lambda val, term: term.lower() in str(val).lower()

    def _setupDefaultSortFunctions(self, key: str, data_type: DataType) -> None:
        """Set up default sort functions based on data type"""
        if data_type == DataType.STRING:
            self._sort_funcs[key] = lambda val: str(val).lower() if val is not None else ''
        elif data_type == DataType.NUMERIC:
            self._sort_funcs[key] = lambda val: float(val) if val is not None else 0
        elif data_type == DataType.DATE:
            self._sort_funcs[key] = lambda val: val if isinstance(val, datetime.date) else datetime.date.min
        elif data_type == DataType.BOOLEAN or data_type == DataType.ICON_BOOLEAN:
            self._sort_funcs[key] = lambda val: bool(val)
        elif data_type == DataType.PROGRESS or data_type == DataType.PROGRESS_BAR:
            self._sort_funcs[key] = lambda val: float(val) if val is not None else 0
        else:
            self._sort_funcs[key] = lambda val: str(val) if val is not None else ''

    # Row Collapsing Methods
    def enableRowCollapsing(self, enabled: bool = True, child_row_key: str = 'children') -> None:
        """Enable or disable row collapsing

        Args:
            enabled: Whether row collapsing is enabled
            child_row_key: Key in row dict for child rows
        """
        self._row_collapsing_enabled = enabled
        self._child_row_key = child_row_key

    def isRowCollapsable(self, row: int) -> bool:
        """Check if row can be collapsed

        Args:
            row: Row index

        Returns:
            Whether row can be collapsed
        """
        if not self._row_collapsing_enabled:
            return False

        if row < 0 or row >= len(self._data):
            return False

        # Check if row has children flag (set during flattening)
        return self._data[row].get('_has_children', False)

    def isRowExpanded(self, row: int) -> bool:
        """Check if row is expanded

        Args:
            row: Row index

        Returns:
            Whether row is expanded
        """
        # Check row data first, fall back to dict
        if 0 <= row < len(self._data):
            return self._data[row].get('_is_expanded', self._expanded_rows.get(row, False))
        return self._expanded_rows.get(row, False)

    def expandRow(self, row: int) -> bool:
        """Expand a row to show its children

        Args:
            row: Row index in flattened data

        Returns:
            Success
        """
        if not self.isRowCollapsable(row):
            return False

        if self.isRowExpanded(row):
            return True

        # Mark as expanded in both dict and row data
        self._expanded_rows[row] = True
        self._data[row]['_is_expanded'] = True

        # Notify view of change (view will handle showing child rows)
        self.rowExpandedCollapsed.emit(row, True)
        return True

    def collapseRow(self, row: int) -> bool:
        """Collapse a row to hide its children

        Args:
            row: Row index in flattened data

        Returns:
            Success
        """
        if not self.isRowCollapsable(row):
            return False

        if not self.isRowExpanded(row):
            return True

        # Mark as collapsed in both dict and row data
        self._expanded_rows[row] = False
        self._data[row]['_is_expanded'] = False

        # Notify view of change (view will handle hiding child rows)
        self.rowExpandedCollapsed.emit(row, False)
        return True

    def toggleRowExpanded(self, row: int) -> bool:
        """Toggle row expanded/collapsed

        Args:
            row: Row index

        Returns:
            Success
        """
        if self.isRowExpanded(row):
            return self.collapseRow(row)
        else:
            return self.expandRow(row)

    def getChildRows(self, row: int) -> List[Dict[str, Any]]:
        """Get child rows for a parent row

        Args:
            row: Parent row index

        Returns:
            List of child rows
        """
        if not self.isRowCollapsable(row):
            return []

        return self._child_rows.get(row, [])
    
    def _getChildRowIndices(self, parent_row: int) -> List[int]:
        """Get indices of child rows for a parent
        
        Args:
            parent_row: Parent row index
            
        Returns:
            List of child row indices
        """
        child_indices = []
        
        # Start from next row
        for i in range(parent_row + 1, len(self._data)):
            row_data = self._data[i]
            
            # Check if this is a child of our parent
            if row_data.get('_is_child') and row_data.get('_parent_index') == parent_row:
                child_indices.append(i)
            # Stop when we hit another parent or non-child
            elif not row_data.get('_is_child'):
                break
        
        return child_indices

    # Search and Filter Methods
    def search(self, term: str) -> List[int]:
        """Search all rows for term

        Args:
            term: Search term

        Returns:
            List of matching row indices
        """
        if not term:
            return list(range(len(self._data)))

        results = []
        for i, row in enumerate(self._data):
            for col_key in self._visible_columns:
                if col_key in self._search_funcs:
                    value = row.get(col_key)
                    if self._search_funcs[col_key](value, term):
                        results.append(i)
                        break

        return results

    def searchColumn(self, column_key: str, term: str) -> List[int]:
        """Search a specific column for term

        Args:
            column_key: Column key
            term: Search term

        Returns:
            List of matching row indices
        """
        if not term or column_key not in self._visible_columns or column_key not in self._search_funcs:
            return list(range(len(self._data)))

        results = []
        for i, row in enumerate(self._data):
            value = row.get(column_key)
            if self._search_funcs[column_key](value, term):
                results.append(i)

        return results

    # Aggregation Methods
    def aggregate(self, column_key: str, agg_type: str) -> Any:
        """Aggregate values in a column

        Args:
            column_key: Column key
            agg_type: Aggregation type

        Returns:
            Aggregated value
        """
        if column_key not in self._column_keys:
            return None

        if column_key in self._aggregation_funcs and agg_type in self._aggregation_funcs[column_key]:
            # Use custom aggregation function
            values = [row.get(column_key) for row in self._data]
            return self._aggregation_funcs[column_key][agg_type](values)

        # Default aggregations
        values = [row.get(column_key) for row in self._data]
        values = [v for v in values if v is not None]

        if not values:
            return None

        if agg_type == 'sum':
            if all(isinstance(v, (int, float)) for v in values):
                return sum(values)
        elif agg_type == 'avg':
            if all(isinstance(v, (int, float)) for v in values):
                return sum(values) / len(values)
        elif agg_type == 'min':
            try:
                return min(values)
            except TypeError:
                pass
        elif agg_type == 'max':
            try:
                return max(values)
            except TypeError:
                pass
        elif agg_type == 'count':
            return len(values)

        return None

    def calculateRowPercentage(self, row_index: int, column_key: str) -> float:
        """Calculate percentage of a row value against column total

        Args:
            row_index: Row index
            column_key: Column key

        Returns:
            Percentage value
        """
        if row_index < 0 or row_index >= len(self._data):
            return 0.0

        value = self._data[row_index].get(column_key, 0)
        if not isinstance(value, (int, float)):
            return 0.0

        total = self.aggregate(column_key, 'sum')
        if total == 0:
            return 0.0

        return (value / total) * 100.0

    def _insertRow(self, row_index: int, row_data: Dict[str, Any]) -> bool:
        """Insert a new row at the specified index

        Args:
            row_index: Index where to insert the row (0-based)
            row_data: Dictionary containing the row data

        Returns:
            Success status
        """
        # Validate row index
        if row_index < 0 or row_index > len(self._data):
            return False

        # Insert the row at the specified index
        self.beginInsertRows(QModelIndex(), row_index, row_index)
        self._data.insert(row_index, row_data)
        self.endInsertRows()

        # Emit signals with proper parameters
        # Create model indexes for the entire row that was inserted
        if len(self._visible_columns) > 0:
            topLeft = self.index(row_index, 0)
            bottomRight = self.index(row_index, len(self._visible_columns) - 1)
            self.dataChanged.emit(topLeft, bottomRight, [Qt.DisplayRole])

        return True

    def appendRow(self, row_data: Dict[str, Any]) -> bool:
        """Append a row at the end of the table

        Args:
            row_data: Dictionary containing the row data

        Returns:
            Success status
        """
        # Just use insertRow with the length of data as index
        return self._insertRow(len(self._data), row_data)
