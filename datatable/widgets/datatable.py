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
#
from typing import Any, Dict, List, Optional, Tuple

from PySide6.QtCore import QPoint, Qt, Signal
from PySide6.QtGui import QAction
from PySide6.QtWidgets import (QComboBox, QFrame, QHBoxLayout, QHeaderView, QLabel, QLineEdit, QMenu, QPushButton,
                               QSpinBox, QStyle, QTableView, QVBoxLayout)

from ..core.BaseController import BaseController
from ..models.datatable_model import DataTableModel, DataType, SortOrder
from ..models.delegates import BooleanDelegate, DateDelegate, NumericDelegate
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
    
    # Slot map
    slot_map = {
        'search_text_changed': ['searchInput', 'textChanged'],
        'page_changed': ['pageSpinBox', 'valueChanged'],
        'rows_per_page_changed': ['rowsPerPageCombo', 'currentIndexChanged'],
        'next_page_clicked': ['nextPageButton', 'clicked'],
        'prev_page_clicked': ['prevPageButton', 'clicked'],
        'first_page_clicked': ['firstPageButton', 'clicked'],
        'last_page_clicked': ['lastPageButton', 'clicked'],
        'table_header_clicked': ['tableView', 'sectionClicked'],
        'table_row_clicked': ['tableView', 'clicked'],
        'column_visibility_changed': ['columnVisibilityButton', 'clicked'],
    }
    
    def __init__(self, parent = None):
        super().__init__(parent)
        self._model = DataTableModel(self)
        self._proxy_model = DataTableProxyModel(self)
        self._proxy_model.setSourceModel(self._model)
        self._proxy_model.setFilterCaseSensitivity(Qt.CaseInsensitive)
        self._proxy_model.setDynamicSortFilter(True)
        
        # Pagination state
        self._page = 1
        self._rows_per_page = 10
        self._total_pages = 1
        
        # Connect model signals
        self._model.modelReset.connect(self._onModelReset)
        self._model.rowExpandedCollapsed.connect(self._onRowExpandedCollapsed)
        
        # Setup UI elements right after initializing self._model
        self._setupHeaderContextMenu()
        self._setupRowContextMenu()
        
        # Configure the view
        self.tableView.setModel(self._proxy_model)
        self.tableView.setSortingEnabled(True)
        self.tableView.setSelectionBehavior(QTableView.SelectRows)
        self.tableView.setSelectionMode(QTableView.SingleSelection)
        self.tableView.verticalHeader().setVisible(False)
        self.tableView.horizontalHeader().setSectionsMovable(True)
        self.tableView.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive)
        self.tableView.horizontalHeader().setContextMenuPolicy(Qt.CustomContextMenu)
        self.tableView.horizontalHeader().customContextMenuRequested.connect(
                self._showHeaderContextMenu
        )
        
        # Initialize pagination
        self.rowsPerPageCombo.clear()
        self.rowsPerPageCombo.addItems(['1', '5', '10', '25', '50', '100'])
        self._updatePagination()
        self.pageSpinBox.setVisible(False)
        
        # Preferences
        self._show_integers_without_decimals = True
    
    # Public API
    def setModel(self, model: DataTableModel) -> None:
        """Set the data model

        Args:
            model: DataTableModel instance
        """
        self._model = model
        self._proxy_model.setSourceModel(model)
        
        # Connect model signals
        self._model.modelReset.connect(self._onModelReset)
        self._model.rowExpandedCollapsed.connect(self._onRowExpandedCollapsed)
        
        # Apply delegates
        self._applyDelegates()
        
        # Update UI
        self._updatePagination()
    
    def setData(self, data: List[Dict[str, Any]]) -> None:
        """Set the table data

        Args:
            data: List of row data dictionaries
        """
        self._model.setModelData(data)
    
    def setColumns(self, columns: List[Tuple[str, str, DataType]]) -> None:
        """Set the table columns

        Args:
            columns: List of column definitions (key, header, type)
        """
        self._model.setColumns(columns)
        self._applyDelegates()
    
    def setVisibleColumns(self, columns: List[str]) -> None:
        """Set which columns are visible

        Args:
            columns: List of column keys to display
        """
        self._model.setVisibleColumns(columns)
    
    def enableRowCollapsing(self, enabled: bool = True, child_row_key: str = 'children') -> None:
        """Enable or disable row collapsing

        Args:
            enabled: Whether row collapsing is enabled
            child_row_key: Key in row data for child rows
        """
        self._model.enableRowCollapsing(enabled, child_row_key)
    
    def search(self, term: str) -> None:
        """Search the table

        Args:
            term: Search term
        """
        # Update the search input if it doesn't match
        if self.searchInput.text() != term:
            self.searchInput.setText(term)
            # let Qt signal does it's job
        # else:
        #     self._applySearch(term)
    
    def sort(self, column_key: str, order: SortOrder = SortOrder.ASCENDING) -> None:
        """Sort the table

        Args:
            column_key: Column key to sort by
            order: Sort order
        """
        if column_key not in self._model._visible_columns:
            return
        
        col_index = self._model._visible_columns.index(column_key)
        self.tableView.sortByColumn(col_index, order.value)
    
    def setPage(self, page: int) -> None:
        """Set the current page

        Args:
            page: Page number (1-based)
        """
        if page < 1 or page > self._total_pages:
            return
        
        self._page = page
        self.pageSpinBox.setValue(page)
        self._updatePagination()
        self.pageChanged.emit(page)
    
    def setRowsPerPage(self, rows: int) -> None:
        """Set rows per page

        Args:
            rows: Number of rows per page
        """
        if rows not in [1, 5, 10, 25, 50, 100]:
            rows = 1
        
        self._rows_per_page = rows
        index = self.rowsPerPageCombo.findText(str(rows))
        if index == -1:
            self.rowsPerPageCombo.setCurrentIndex(index)
        
        self._updatePagination()
    
    def getData(self) -> List[Dict[str, Any]]:
        """Get current table data

        Returns:
            List of row data dictionaries
        """
        return self._model._data
    
    def getSelectedRow(self) -> Optional[Dict[str, Any]]:
        """Get selected row data

        Returns:
            Selected row data or None
        """
        indexes = self.tableView.selectedIndexes()
        if not indexes:
            return None
        
        proxy_row = indexes[0].row()
        model_row = self._proxy_model.mapToSource(indexes[0]).row()
        
        return self._model._data[model_row]
    
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
    
    def setIntegerDisplay(self, show_without_decimals: bool) -> None:
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
                        col_key, lambda n: str(int(n)) if isinstance(n, (int, float)) and float(n).is_integer() 
                                else (f'{n:,.2f}' if isinstance(n, (int, float)) else str(n))
                    )
                else:
                    self._model.setFormattingFunction(
                        col_key, lambda n: f'{n:,.2f}' if isinstance(n, (int, float)) else str(n)
                    )
    
    # Private methods
    def _onModelReset(self) -> None:
        """Handle model reset"""
        self._applyDelegates()
        self._updatePagination()
        # self.statusLabel.setText(f'Total entries: {len(self._model._data)}')
    
    def _onRowExpandedCollapsed(self, row: int, is_expanded: bool) -> None:
        """Handle row expanded/collapsed

        Args:
            row: Row index
            is_expanded: Whether row is expanded
        """
        if is_expanded:
            self.rowExpanded.emit(row, self._model._data[row])
        else:
            self.rowCollapsed.emit(row, self._model._data[row])
        
        self._updatePagination()
    
    def _applyDelegates(self) -> None:
        """Apply delegates based on column types"""
        for i, col_key in enumerate(self._model._visible_columns):
            data_type = self._model._column_types.get(col_key)
            
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
        total_rows = len(self._model._data)
        startRange = (self._page - 1) * self._rows_per_page
        stopRange = min(total_rows, (self._page * self._rows_per_page))
        if self._proxy_model:
            self._proxy_model.setPaginationRange(startRange, stopRange)
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
                if not button.property("isChangePageConnected"):
                    button.setProperty("isChangePageConnected", True)
                    button.clicked.connect(
                            lambda _, page = i: self.setPage(page)
                    )
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
        if not self._model._data:
            self.totalEntriesLabel.setText('Showing 0 to 0 of 0 entries')
            return
        
        start = (self._page - 1) * self._rows_per_page
        end = min(start + self._rows_per_page, len(self._model._data))
        
        self.totalEntriesLabel.setText(
                f'Showing {start + 1} to {end} of {len(self._model._data)} entries'
        )
        
        # Here we would filter rows based on pagination
        # but because we're using a QTableView and model, we don't need to hide rows
        # We could implement custom model/view to handle pagination
    
    def _applySearch(self, term: str) -> None:
        """Apply search filter

        Args:
            term: Search term
        """
        # Use the advanced search capabilities of DataTableProxyModel
        if hasattr(self._proxy_model, 'setSearchTerm'):
            self._proxy_model.setSearchTerm(term)
        else:
            # Fallback to basic filtering if using standard QSortFilterProxyModel
            self._proxy_model.setFilterFixedString(term)
            self._proxy_model.setFilterCaseSensitivity(Qt.CaseInsensitive)
        
        # Reset pagination
        self._page = 1
        self.pageSpinBox.setValue(1)
        self._updatePagination()
    
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
        for i, key in enumerate(self._model._column_keys):
            header_text = self._model._headers[i]
            action = QAction(header_text, vis_menu)
            action.setCheckable(True)
            action.setChecked(key in self._model._visible_columns)
            action.triggered.connect(
                    lambda checked, k = key: self._toggleColumnVisibility(k, checked)
            )
            vis_menu.addAction(action)
        
        global_pos = header.mapToGlobal(pos)
        self._header_menu.popup(global_pos)
    
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
