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


#
#
from typing import Any, Callable, Dict, List, Optional, Tuple, Union

from PySide6.QtCore import QPoint, Qt, Signal, QTimer, QItemSelectionModel, QEvent
from PySide6.QtGui import QAction, QColor, QCursor
from PySide6.QtWidgets import QComboBox, QFrame, QHBoxLayout, QHeaderView, QLabel, QLineEdit, QMenu, QPushButton, QSpinBox, QStyle, QTableView, QVBoxLayout

from ..core.BaseController import BaseController
from ..models.datatable_model import DataTableModel, DataType, SortOrder
from ..models.delegates import BooleanDelegate, DateDelegate, NumericDelegate, ProgressDelegate, ProgressBarDelegate, IconBooleanDelegate
from ..ui.untitled import Ui_DataTable
from ..widgets.handlers.DataTableHandler import DataTableProxyModel


class DataTable(Ui_DataTable, BaseController):
    """Main DataTable widget with jQuery DataTable-like functionality"""

    # Signals
    pageChanged = Signal(int)
    rowSelected = Signal(int, dict)
    rowExpanded = Signal(int, dict)
    rowCollapsed = Signal(int, dict)
    dataFiltered = Signal(list)
    sortChanged = Signal(str, SortOrder)
    selectionChanged = Signal(QItemSelectionModel, QItemSelectionModel)
    # Slot map
    slot_map = {
        'search_text_changed': ['searchInput', 'textChanged'],
        'page_changed': ['pageSpinBox', 'valueChanged'],
        'rows_per_page_changed': ['rowsPerPageCombo', 'currentIndexChanged'],
        'next_page_clicked': ['nextPageButton', 'clicked'],
        'prev_page_clicked': ['prevPageButton', 'clicked'],
        'first_page_clicked': ['firstPageButton', 'clicked'],
        'last_page_clicked': ['lastPageButton', 'clicked'],
        'table_header_clicked': ['tableView.horizontalHeader', 'sectionClicked'],
        'table_row_clicked': ['tableView', 'clicked'],
        'column_visibility_changed': ['columnVisibilityButton', 'clicked'],
        'selection_changed': ['tableView.selectionModel', 'selectionChanged']
        # 'select_all': ['selectAllButton', 'clicked'],
        # 'deselect_all': ['deselectAllButton', 'clicked'],
        # 'select_inverse': ['selectInverseButton', 'clicked']
    }

    def __init__(self, parent=None):
        super().__init__(parent)
        self._model = DataTableModel(self)
        self._proxyModel = DataTableProxyModel(self)
        self._proxyModel.setSourceModel(self._model)
        self._proxyModel.setFilterCaseSensitivity(Qt.CaseInsensitive)
        self._proxyModel.setDynamicSortFilter(False)  # Disable auto-sort to preserve grouping

        self.tableView.setModel(self._proxyModel)

        # Pagination state
        self._page = 1
        self._rows_per_page = 10
        self._total_pages = 1

        # Column configurations for delegates
        self._column_configurations: Dict[str, Dict[str, Any]] = {}

        self._connectModelSignals()._uiBehaviorSetup()
        # Initialize pagination
        self.rowsPerPageCombo.clear()
        self.rowsPerPageCombo.addItems(['10', '25', '50', '100'])
        self.rowsPerPageCombo.setCurrentText('25')
        self._updatePagination()
        self.pageSpinBox.setVisible(False)

        # Preferences
        self._show_integers_without_decimals = True

    def _connectModelSignals(self):
        self._model.modelReset.connect(self._onModelReset)
        self._model.rowExpandedCollapsed.connect(self._onRowExpandedCollapsed)
        return self

    def _uiBehaviorSetup(self):
        # Setup UI elements right after initializing self._model
        self._setupHeaderContextMenu()
        self._setupRowContextMenu()
        # Configure the view
        self.tableView.setSortingEnabled(True)
        self.tableView.setSelectionBehavior(QTableView.SelectRows)
        self.tableView.setSelectionMode(QTableView.ExtendedSelection)  # Enable multi-selection
        self.tableView.verticalHeader().setVisible(False)
        self.tableView.horizontalHeader().setSectionsMovable(True)
        self.tableView.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive)
        self.tableView.horizontalHeader().setContextMenuPolicy(Qt.CustomContextMenu)
        self.tableView.horizontalHeader().customContextMenuRequested.connect(self._showHeaderContextMenu)
        
        # Enable mouse tracking for cursor feedback on expandable rows
        self.tableView.setMouseTracking(True)
        self.tableView.viewport().setMouseTracking(True)
        self.tableView.viewport().installEventFilter(self)
        
        return self

    def selectAll(self) -> 'DataTable':
        self.tableView.selectAll()
        return self

    def selectNone(self) -> 'DataTable':
        self.tableView.clearSelection()
        return self

    def clearSelection(self) -> 'DataTable':
        return self.selectNone()

    def selectInverse(self):
        """Invert current selection"""
        rows = self._paginationModel.rowCount()
        selection_model = self.tableView.selectionModel()

        for row in range(rows):
            index = self._paginationModel.index(row, 0)
            selection_model.select(index, QItemSelectionModel.Toggle | QItemSelectionModel.Rows)
        return self

    def _save_state(self):
        """Save the current UI state of the table."""
        selected_ids = {row.get('id') for row in self.getSelectedRows()}
        state = {'v_scroll': self.tableView.verticalScrollBar().value(), 'h_scroll': self.tableView.horizontalScrollBar().value(), 'selected_ids': selected_ids}
        return state

    def _restore_state(self, state):
        """Restore the UI state of the table."""
        if not state:
            return

        # Restore selection
        selectedIds = state.get('selected_ids', set())
        if selectedIds:
            selectionModel: QItemSelectionModel = self.tableView.selectionModel()
            selectionModel.clearSelection()

            # Iterate through visible rows in proxy
            for row in range(self._proxyModel.rowCount()):
                # Map view index to source model
                proxyIndex = self._proxyModel.index(row, 0)
                sourceIndex = self._proxyModel.mapToSource(proxyIndex)

                # Get unique ID from source model
                rowData = self._model.getRowData(sourceIndex.row())
                if rowData and rowData.get('id') in selectedIds:
                    # Select row in view
                    selectionModel.select(proxyIndex, QItemSelectionModel.Select | QItemSelectionModel.Rows)

        # Restore scroll positions
        QTimer.singleShot(0, lambda: self.tableView.verticalScrollBar().setValue(state.get('v_scroll', 0)))
        QTimer.singleShot(0, lambda: self.tableView.horizontalScrollBar().setValue(state.get('h_scroll', 0)))

    # Public API
    def setModel(self, model: DataTableModel) -> 'DataTable':
        """Set the data model

        Args:
            model: DataTableModel instance
        """
        self._model = model
        self._proxyModel.setSourceModel(model)
        # Connect model signals
        self._model.modelReset.connect(self._onModelReset)
        self._model.rowExpandedCollapsed.connect(self._onRowExpandedCollapsed)
        # Apply delegates
        self._applyDelegates()
        # Update UI
        self._updatePagination()
        return self

    def setUiSelectionType(
        self, mode: Union[QTableView.SelectionMode, int] = QTableView.ExtendedSelection, behavior: Union[QTableView.SelectionBehavior, int] = QTableView.SelectRows
    ) -> 'DataTable':
        """Set the selection mode and behavior for the table view.

        Args:
            mode: The selection mode (e.g., QTableView.SingleSelection, QTableView.MultiSelection).
            behavior: The selection behavior (e.g., QTableView.SelectRows, QTableView.SelectItems).
        """
        try:
            if isinstance(mode, int):
                # Validate integer mode against enum values
                if not any(mode == item.value for item in QTableView.SelectionMode):
                    raise ValueError(f'Invalid selection mode integer: {mode}')
                self.tableView.setSelectionMode(QTableView.SelectionMode(mode))
            elif isinstance(mode, QTableView.SelectionMode):
                self.tableView.setSelectionMode(mode)
            else:
                raise TypeError(f'Invalid type for mode: {type(mode)}')

            if isinstance(behavior, int):
                # Validate integer behavior against enum values
                if not any(behavior == item.value for item in QTableView.SelectionBehavior):
                    raise ValueError(f'Invalid selection behavior integer: {behavior}')
                self.tableView.setSelectionBehavior(QTableView.SelectionBehavior(behavior))
            elif isinstance(behavior, QTableView.SelectionBehavior):
                self.tableView.setSelectionBehavior(behavior)
            else:
                raise TypeError(f'Invalid type for behavior: {type(behavior)}')
            return self
        except (ValueError, TypeError) as e:
            raise

    def setData(self, data: List[Dict[str, Any]]) -> 'DataTable':
        """Set the table data while preserving UI state.

        Args:
            data: List of row data dictionaries
        """
        state = self._save_state()
        self._model.setModelData(data)
        
        # Hide all child rows initially if row collapsing is enabled
        if self._model._row_collapsing_enabled:
            self._hideAllChildRows()
        
        self._restore_state(state)
        return self

    def setColumns(self, columns: List[Tuple[str, str, DataType]]) -> 'DataTable':
        """Set the table columns

        Args:
            columns: List of column definitions (key, header, type)
        """
        self._model.setColumns(columns)
        self._applyDelegates()
        return self

    def setVisibleColumns(self, columns: List[str]) -> 'DataTable':
        """Set which columns are visible

        Args:
            columns: List of column keys to display
        """
        self._model.setVisibleColumns(columns)
        return self

    def enableRowCollapsing(self, enabled: bool = True, child_row_key: str = 'children') -> 'DataTable':
        """Enable or disable row collapsing

        Args:
            enabled: Whether row collapsing is enabled
            child_row_key: Key in row data for child rows
        """
        self._model.enableRowCollapsing(enabled, child_row_key)
        return self

    def search(self, term: str) -> 'DataTable':
        """Search the table

        Args:
            term: Search term
        """
        # Update the search input if it doesn't match
        if self.searchInput.text() != term:
            self.searchInput.setText(term)
        else:
            self.applyFilters(search_term=term)
        return self

    def applyFilters(self, search_term: Optional[str] = None, data_type: Optional[DataType] = None) -> 'DataTable':
        """Apply search and data type filters to the table."""
        current_search = self._proxyModel._search_term
        current_type = self._proxyModel._data_type_filter

        new_search = search_term if search_term is not None else current_search
        new_type = data_type if data_type is not None else current_type
        self.setPage(1)
        self._proxyModel.setSearchTerm(new_search)
        self._proxyModel.setDataTypeFilter(new_type)

        # Reset pagination to the first page
        self._updatePagination()
        return self

    def sort(self, column_key: str, order: SortOrder = SortOrder.ASCENDING) -> 'DataTable':
        """Sort the table

        Args:
            column_key: Column key to sort by
            order: Sort order
        """
        if column_key not in self._model._visible_columns:
            return self

        col_index = self._model._visible_columns.index(column_key)
        self.tableView.sortByColumn(col_index, order.value)
        return self

    def setPage(self, page: int) -> 'DataTable':
        """Set the current page

        Args:
            page: Page number (1-based)
        """
        if page < 1 or page > self._total_pages:
            # TODO: OutOfIndexException should i ?
            return self

        self._page = page
        self.pageSpinBox.setValue(page)
        self._updateVisibleRows()
        self._updateCurrentPageButton()
        self.pageChanged.emit(page)
        return self

    def setRowsPerPage(self, rows: int) -> 'DataTable':
        """Set rows per page

        Args:
            rows: Number of rows per page
        """
        if rows not in [10, 25, 50, 100]:
            rows = 25

        self._rows_per_page = rows
        index = self.rowsPerPageCombo.findText(str(rows))
        if index != -1:
            self.rowsPerPageCombo.setCurrentIndex(index)

        self._updatePagination()
        return self

    def getData(self) -> List[Dict[str, Any]]:
        """Get current table data

        Returns:
            List of row data dictionaries
        """
        return self._model._data

    def getSelectedRow(self) -> Optional[Dict[str, Any]]:
        """Get selected row data (first selected if multiple)

        Returns:
            Selected row data or None
        """
        rows = self.getSelectedRows()
        return rows[0] if rows else None

    def getSelectedRows(self) -> List[Dict[str, Any]]:
        """Get all selected rows data

        Returns:
            List of selected row data dictionaries
        """
        indexes = self.tableView.selectionModel().selectedIndexes()
        if not indexes:
            return []

        selectedData = []
        for index in indexes:
            # Map view (proxy) index to source model
            sourceIndex = self._proxyModel.mapToSource(index)
            modelRow = sourceIndex.row()
            selectedData.append(self._model._data[modelRow])

        return selectedData

    def getAggregateValue(self, column_key: str, agg_type: str) -> Any:
        """Get aggregate value for column

        Args:
            column_key: Column key
            agg_type: Aggregation type (sum, avg, min, max, count)

        Returns:
            Aggregated value
        """
        return self._model.aggregate(column_key, agg_type)

    def insertRow(self, row_index: int, row_data: Dict[str, Any]) -> bool:
        """Insert a new row at the specified index

        Args:
            row_index: Index where to insert the row (0-based)
            row_data: Dictionary containing the row data

        Returns:
            Success status
        """
        success = self._model._insertRow(row_index, row_data)
        if success:
            self._updatePagination()
        return success

    def appendRow(self, row_data: Dict[str, Any]) -> bool:
        """Append a row at the end of the table

        Args:
            row_data: Dictionary containing the row data

        Returns:
            Success status
        """
        success = self._model.appendRow(row_data)
        if success:
            self._updatePagination()
        return success

    def setIntegerDisplay(self, show_without_decimals: bool) -> 'DataTable':
        """Set whether to display integers without decimal places

        Args:
            show_without_decimals: If True, integers will be displayed without decimal places
        """
        self._show_integers_without_decimals = show_without_decimals

        # Update numeric formatting functions
        for col_key, data_type in self._model._column_types.items():
            if data_type == DataType.NUMERIC:
                if show_without_decimals:
                    self._model.setFormattingFunction(
                        col_key, lambda n: str(int(n)) if isinstance(n, (int, float)) and float(n).is_integer() else (f'{n:,.2f}' if isinstance(n, (int, float)) else str(n))
                    )
                else:
                    self._model.setFormattingFunction(col_key, lambda n: f'{n:,.2f}' if isinstance(n, (int, float)) else str(n))
        return self

    def setFormattingFunction(self, column_key: str, func: Callable) -> 'DataTable':
        """Set the formatting function for a column

        Args:
            column_key: Column key
            func: Formatting function
        """
        self._model.setFormattingFunction(column_key, func)
        return self

    # Delegate Configuration Methods
    def setProgressBarColor(self, column_key: str, color: Union[str, Any]) -> 'DataTable':
        """Set base color for a progress bar column"""
        if column_key not in self._column_configurations:
            self._column_configurations[column_key] = {}
        self._column_configurations[column_key]['base_color'] = color

        # Update existing delegate if visible
        if column_key in self._model._visible_columns:
            col_index = self._model._visible_columns.index(column_key)
            delegate = self.tableView.itemDelegateForColumn(col_index)
            if isinstance(delegate, ProgressBarDelegate):
                delegate.set_base_color(color)
        return self

    def setProgressBarGradient(self, column_key: str, enabled: bool) -> 'DataTable':
        """Enable/disable gradient for a progress bar column"""
        if column_key not in self._column_configurations:
            self._column_configurations[column_key] = {}
        self._column_configurations[column_key]['gradient'] = enabled

        if column_key in self._model._visible_columns:
            col_index = self._model._visible_columns.index(column_key)
            delegate = self.tableView.itemDelegateForColumn(col_index)
            if isinstance(delegate, ProgressBarDelegate):
                delegate.set_gradient(enabled)
        return self

    def addProgressBarRange(self, column_key: str, min_pct: float, max_pct: float, color: Union[str, Any]) -> 'DataTable':
        """Add a color range for a progress bar column"""
        if column_key not in self._column_configurations:
            self._column_configurations[column_key] = {}
        if 'ranges' not in self._column_configurations[column_key]:
            self._column_configurations[column_key]['ranges'] = []
        self._column_configurations[column_key]['ranges'].append((min_pct, max_pct, color))

        if column_key in self._model._visible_columns:
            col_index = self._model._visible_columns.index(column_key)
            delegate = self.tableView.itemDelegateForColumn(col_index)
            if isinstance(delegate, ProgressBarDelegate):
                delegate.add_range(min_pct, max_pct, color)
        return self

    def setIconBooleanColors(self, column_key: str, yes_color: Union[str, Any], no_color: Union[str, Any]) -> 'DataTable':
        """Set colors for an icon boolean column"""
        if column_key not in self._column_configurations:
            self._column_configurations[column_key] = {}
        self._column_configurations[column_key]['yes_color'] = yes_color
        self._column_configurations[column_key]['no_color'] = no_color

        if column_key in self._model._visible_columns:
            col_index = self._model._visible_columns.index(column_key)
            delegate = self.tableView.itemDelegateForColumn(col_index)
            if isinstance(delegate, IconBooleanDelegate):
                delegate.set_yes_color(QColor(yes_color))
                delegate.set_no_color(QColor(no_color))
        return self

    # Private methods
    def _onModelReset(self) -> None:
        """Handle model reset"""
        self._applyDelegates()
        self._updatePagination()
        # self.statusLabel.setText(f'Total entries: {len(self._model._data)}')

    def _onRowExpandedCollapsed(self, row: int, isExpanded: bool) -> None:
        """Handle row expanded/collapsed

        Args:
            row: Row index
            isExpanded: Whether row is expanded
        """
        # Get child row indices from model
        childIndices = self._model._getChildRowIndices(row)
        
        # Show/hide child rows in view
        for childIdx in childIndices:
            # Get row in current view (after filtering/pagination)
            sourceIndex = self._model.index(childIdx, 0)
            proxyIndex = self._proxyModel.mapFromSource(sourceIndex)
            
            if proxyIndex.isValid():
                # Hide/show the row
                self.tableView.setRowHidden(proxyIndex.row(), not isExpanded)
        
        # Emit signals
        if isExpanded:
            self.rowExpanded.emit(row, self._model._data[row])
        else:
            self.rowCollapsed.emit(row, self._model._data[row])
        
        # Update pagination (visible row count may have changed)
        self._updatePagination()
    
    def _hideAllChildRows(self) -> None:
        """Hide all child rows initially"""
        for row in range(len(self._model._data)):
            if self._model._data[row].get('_is_child'):
                # Get row in current view
                sourceIndex = self._model.index(row, 0)
                proxyIndex = self._proxyModel.mapFromSource(sourceIndex)
                
                if proxyIndex.isValid():
                    self.tableView.setRowHidden(proxyIndex.row(), True)

    def _applyDelegates(self) -> None:
        """Apply delegates based on column types"""
        for i, col_key in enumerate(self._model._visible_columns):
            data_type = self._model._column_types.get(col_key)
            config = self._column_configurations.get(col_key, {})

            if data_type == DataType.NUMERIC:
                delegate = NumericDelegate(self.tableView)
                if self._show_integers_without_decimals:
                    pass
                self.tableView.setItemDelegateForColumn(i, delegate)
            elif data_type == DataType.DATE:
                delegate = DateDelegate(self.tableView)
                self.tableView.setItemDelegateForColumn(i, delegate)
            elif data_type == DataType.BOOLEAN:
                delegate = BooleanDelegate(self.tableView)
                self.tableView.setItemDelegateForColumn(i, delegate)
            elif data_type == DataType.PROGRESS:
                delegate = ProgressDelegate(self.tableView)
                self.tableView.setItemDelegateForColumn(i, delegate)
            elif data_type == DataType.PROGRESS_BAR:
                delegate = ProgressBarDelegate(self.tableView)
                if 'base_color' in config:
                    delegate.set_base_color(config['base_color'])
                if 'gradient' in config:
                    delegate.set_gradient(config['gradient'])
                if 'ranges' in config:
                    for r in config['ranges']:
                        delegate.add_range(*r)
                self.tableView.setItemDelegateForColumn(i, delegate)
            elif data_type == DataType.ICON_BOOLEAN:
                delegate = IconBooleanDelegate(self.tableView)
                if 'yes_color' in config:
                    delegate.set_yes_color(QColor(config['yes_color']))
                if 'no_color' in config:
                    delegate.set_no_color(QColor(config['no_color']))
                self.tableView.setItemDelegateForColumn(i, delegate)

    def clearLayout(self, layout):
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()
            else:
                # If the item is a layout, recursively clear it
                sub_layout = item.layout()
                if sub_layout is not None:
                    self.clearLayout(sub_layout)

    def _updatePagination(self) -> None:
        """Update pagination controls"""
        # Use filtered row count
        total_rows = self._proxyModel.rowCount()

        if total_rows == 0:
            self._total_pages = 1
        else:
            self._total_pages = (total_rows + self._rows_per_page - 1) // self._rows_per_page

        self.pageSpinBox.setMaximum(self._total_pages)
        # self.totalPagesLabel.setText(f'of {self._total_pages}')

        # Ensure current page is valid
        if self._page > self._total_pages:
            self._page = self._total_pages

            # self.pageSpinBox.setValue(self._page)
        self.clearLayout(self._pagesLayout)

        for range_ in range(self._page - 3, self._total_pages + self._page + 3):
            if range_ < 1 or range_ > self._total_pages:
                continue

            self.__setattr__(f'page{range_}Button', QPushButton(str(range_)))
            self._pagesLayout.addWidget(self.__getattribute__(f'page{range_}Button'))
            if range_ == self._page:
                self.__getattribute__(f'page{range_}Button').setEnabled(False)
            if range_ == self._page + 3 and range_ < self._total_pages:
                self._pagesLayout.addWidget(QPushButton('...'))
        # Update visible rows
        self._updateVisibleRows()
        self._updateFirstLastVisible()
        self._updateCurrentPageButton()

    def _updateCurrentPageButton(self):
        """Update current page button"""
        for i in range(1, self._total_pages + 1):
            if self.__getattribute__(f'page{i}Button') is None:
                continue
            button = self.__getattribute__(f'page{i}Button')
            if button:
                if not button.property('isChangePageConnected'):
                    button.setProperty('isChangePageConnected', True)
                    button.clicked.connect(lambda _, page=i: self.setPage(page))
                button.setEnabled(i != self._page)
                if i == self._page:
                    button.setStyleSheet('background-color: #007acc;')
                    button.setEnabled(False)
                else:
                    button.setStyleSheet('')
                    button.setEnabled(True)

    def _updateFirstLastVisible(self):
        if self._page == 1:
            self.backwardLayout.setVisible(False)
        else:
            if self._page == self._total_pages or self._total_pages == 1:
                self.fowardLayout.setVisible(False)

    def _updateVisibleRows(self) -> None:
        """Update which rows are visible based on pagination"""
        totalFiltered = self._proxyModel.rowCount()

        if totalFiltered == 0:
            self.displayingEntriesLbl.setText('0')
            self.totalEntriesLbl.setText('0')
            self._proxyModel.disablePagination()
            return

        start = (self._page - 1) * self._rows_per_page
        end = min(start + self._rows_per_page, totalFiltered)

        self.displayingEntriesLbl.setText(f'{start + 1} - {end}')
        self.totalEntriesLbl.setText(str(totalFiltered))
        self._proxyModel.setPaginationRange(start, end)

    def _setupHeaderContextMenu(self) -> None:
        """Setup context menu for header"""
        self._header_menu = QMenu(self)

    def _setupRowContextMenu(self) -> None:
        """Setup context menu for rows"""
        self._row_menu = QMenu(self)

    def _showHeaderContextMenu(self, pos: QPoint) -> None:
        """Show context menu for header

        Args:
            pos: Position
        """
        self._header_menu.clear()

        # Sort actions
        header = self.tableView.horizontalHeader()
        logical_index = header.logicalIndexAt(pos)
        if logical_index >= 0:
            column_key = self._model._visible_columns[logical_index]
            column_name = self._model._headers[logical_index]

            # Sort actions
            sort_asc_action = QAction(f'Sort {column_name} Ascending', self._header_menu)
            sort_asc_action.triggered.connect(lambda: self.sort(column_key, SortOrder.ASCENDING))
            self._header_menu.addAction(sort_asc_action)

            sort_desc_action = QAction(f'Sort {column_name} Descending', self._header_menu)
            sort_desc_action.triggered.connect(lambda: self.sort(column_key, SortOrder.DESCENDING))
            self._header_menu.addAction(sort_desc_action)

            self._header_menu.addSeparator()

        # Column visibility actions
        vis_menu = self._header_menu.addMenu('Column Visibility')
        # Create mapping from column_keys to headers to avoid index issues
        headers_dict = dict(zip(self._model._column_keys, self._model._headers))
        for key in self._model._column_keys:
            header_text = headers_dict.get(key, key)  # Fallback to key if not found
            action = QAction(header_text, vis_menu)
            action.setCheckable(True)
            action.setChecked(key in self._model._visible_columns)
            action.triggered.connect(lambda checked, k=key: self._toggleColumnVisibility(k, checked))
            vis_menu.addAction(action)

        global_pos = header.mapToGlobal(pos)
        self._header_menu.popup(global_pos)
    
    def eventFilter(self, obj, event):
        """Event filter for handling mouse hover tooltips"""
        if obj == self.tableView.viewport() and event.type() == QEvent.Type.ToolTip:
            # Get the index at the cursor position
            viewportPos = event.pos()
            index = self.tableView.indexAt(viewportPos)

            if index.isValid() and hasattr(self._model, '_column_help'):
                # Map view (proxy) index to source model
                sourceIndex = self._proxyModel.mapToSource(index)
                column = sourceIndex.column()

                # Check if the column has associated help text
                if column < len(self._model._visible_columns):
                    columnKey = self._model._visible_columns[column]
                    helpText = self._model._column_help.get(columnKey)

                    if helpText:
                        # Show the tooltip
                        from PySide6.QtWidgets import QToolTip
                        QToolTip.showText(event.globalPos(), helpText, self.tableView)
                        return True

        return super().eventFilter(obj, event)

    def _toggleColumnVisibility(self, column_key: str, checked: bool = None) -> None:
        """Toggle column visibility

        Args:
            column_key: Column key
            checked: Whether column should be visible
        """
        # When used with partial, checked will be passed as the second parameter
        # When used with lambda, column_key and checked are explicitly provided
        # Handle both cases
        visible = checked
        if checked is None and isinstance(column_key, bool):
            # This happens when partial passes the check state as first param
            visible = column_key
            # Get the actual column key from the sender
            sender = self.sender()
            if sender and hasattr(sender, 'data'):
                column_key = sender.data()
            else:
                return

        visible_columns = self._model._visible_columns.copy()

        if visible and column_key not in visible_columns:
            # Add column - preserve original order
            all_columns = self._model._column_keys
            new_columns = []
            for col in all_columns:
                if col == column_key or col in visible_columns:
                    new_columns.append(col)
            visible_columns = new_columns
        elif not visible and column_key in visible_columns:
            # Remove column
            visible_columns.remove(column_key)

        if visible_columns:  # Ensure at least one column remains visible
            self._model.setVisibleColumns(visible_columns)
