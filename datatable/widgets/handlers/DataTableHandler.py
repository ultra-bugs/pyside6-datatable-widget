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
from typing import Any, Dict

from PySide6.QtCore import QItemSelectionModel, QModelIndex, Qt, QSortFilterProxyModel, QAbstractItemModel
from PySide6.QtWidgets import QHeaderView, QMenu


from ...core.Observer import Subscriber
from ...core.WidgetManager import WidgetManager
from ...models.datatable_model import DataType, SortOrder



class DataTableProxyModel(QSortFilterProxyModel):
    """Single proxy model handling filter, search, and pagination"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._search_term = ''
        self._data_type_filter = None
        self._pagination_start = 0
        self._pagination_end = 0
        self._pagination_enabled = False

    def setSearchTerm(self, term):
        """Set search term"""
        self._search_term = term
        self.invalidateFilter()

    def setDataTypeFilter(self, dataType):
        """Set data type filter"""
        self._data_type_filter = dataType
        self.invalidateFilter()

    def setPaginationRange(self, start: int, end: int):
        """Set pagination range"""
        self._pagination_start = start
        self._pagination_end = end
        self._pagination_enabled = True
        self.invalidateFilter()

    def disablePagination(self):
        """Disable pagination"""
        self._pagination_enabled = False
        self.invalidateFilter()

    def filterAcceptsRow(self, sourceRow: int, sourceParent: QModelIndex) -> bool:
        """Combined filter: pagination + type + search"""
        # 1. Pagination check first (most efficient)
        if self._pagination_enabled:
            if sourceRow < self._pagination_start or sourceRow >= self._pagination_end:
                return False

        # 2. Type filter
        model = self.sourceModel()
        if self._data_type_filter is not None:
            typeMatch = False
            for colKey in model._visible_columns:
                if model._column_types.get(colKey) == self._data_type_filter:
                    typeMatch = True
                    break
            if not typeMatch:
                return False

        # 3. Search filter
        if self._search_term:
            searchMatch = False
            for colIdx, colKey in enumerate(model._visible_columns):
                index = model.index(sourceRow, colIdx, sourceParent)
                value = model.data(index, Qt.DisplayRole)

                if colKey in model._search_funcs:
                    if model._search_funcs[colKey](value, self._search_term):
                        searchMatch = True
                        break
                elif value is not None and self._search_term.lower() in str(value).lower():
                    searchMatch = True
                    break

            if not searchMatch:
                return False

        return True
        
class DataTableHandler(Subscriber):
    """Handler for DataTable events"""

    def __init__(self, widget_manager: WidgetManager, events: list):
        super().__init__(events)
        self.widget_manager = widget_manager
        from ... import DataTable
        self.table:DataTable = widget_manager.controller

    def on_selection_changed(self, selected: QItemSelectionModel, deselected: QItemSelectionModel):
        """Handle selection changes

        Args:
            selected: Selected items
            deselected: Deselected items
        """
        self.table.selectionChanged.emit(selected, deselected)

    def on_search_text_changed(self, text: str, data: Dict[str, Any] = None):
        """Handle search text changed

        Args:
            text: Search text
            data: Event data
        """
        self.table.search(text)

    def on_type_filter_changed(self, index: int, data: Dict[str, Any] = None):
        """Handle type filter changed

        Args:
            index: Type filter index
            data: Event data
        """
        self._apply_combined_filters()

    def _apply_combined_filters(self):
        """Apply both text search and type filters together (AND condition)"""
        search_term = self.widget_manager.get('searchInput').text()
        type_index = self.widget_manager.get('typeComboBox').currentIndex()

        # Convert type index to DataType
        type_map = {
            0: None,  # All Types
            1: DataType.NUMERIC,
            2: DataType.STRING,  # One Line Text
            3: DataType.STRING,  # Text (multiline)
            4: DataType.DATE,
            5: DataType.BOOLEAN,
        }

        data_type = type_map.get(type_index)
        return self.table.applyFilters(search_term, data_type)
        # self.table.applyFilters(search_term, data_type)
        # Apply filters to table
        filtered_rows = []

        # Only filter if we have a search term or data type filter
        if search_term or (data_type is not None and type_index > 0):
            model = self.table._model

            # Check each row
            for row_idx, row_data in enumerate(model._data):
                row_matches = True

                # Type filter: check if any column in this row has the specified data type
                if data_type is not None and type_index > 0:
                    type_match = False

                    for col_key, col_type in model._column_types.items():
                        if col_type == data_type and col_key in model._visible_columns:
                            type_match = True
                            break

                    if not type_match:
                        row_matches = False

                # Text search: check if any column contains the search term
                if search_term and row_matches:
                    search_match = False

                    for col_key in model._visible_columns:
                        value = row_data.get(col_key)

                        # Use search function if available
                        if col_key in model._search_funcs:
                            if model._search_funcs[col_key](value, search_term):
                                search_match = True
                                break
                        # Default text-based search
                        elif value is not None and search_term.lower() in str(value).lower():
                            search_match = True
                            break

                    if not search_match:
                        row_matches = False

                # Add row to filtered list if it matches all conditions
                if row_matches:
                    filtered_rows.append(row_idx)

        # Apply filtering by setting visible rows on the model
        # Hoặc sử dụng proxy model nếu được triển khai
        if hasattr(self.table._proxy_model, 'setSearchTerm') and hasattr(self.table._proxy_model, 'setDataTypeFilter'):
            # Sử dụng proxy model nếu có các phương thức phù hợp
            self.table._proxy_model.setSearchTerm(search_term)
            self.table._proxy_model.setDataTypeFilter(data_type)
        else:
            # Hoặc áp dụng bộ lọc thông qua các phương thức có sẵn
            if hasattr(self.table, 'applyFilters'):
                self.table.applyFilters(filtered_rows)
            elif hasattr(self.table, '_applySearch'):
                self.table._applySearch(search_term)
                # Không có cách trực tiếp để áp dụng bộ lọc loại

        # Reset page to 1 when filter changes
        self.table._page = 1
        self.widget_manager.get('pageSpinBox').setValue(1)
        self.table._updatePagination()
    
    def on_page_changed(self, page: int, data: Dict[str, Any] = None):
        """Xử lý khi trang thay đổi

        Args:
            page: Số trang mới
            data: Dữ liệu sự kiện
        """
        self.table.setPage(page)

    def on_rows_per_page_changed(self, index: int, data: Dict[str, Any] = None):
        """Xử lý khi số dòng mỗi trang thay đổi

        Args:
            index: Index được chọn trong combobox
            data: Dữ liệu sự kiện
        """
        combo = self.widget_manager.get('rowsPerPageCombo')
        rows_text = combo.currentText()
        try:
            rows = int(rows_text)
            self.table.setRowsPerPage(rows)
        except (ValueError, TypeError):
            pass

    def on_next_page_clicked(self, data: Dict[str, Any] = None):
        """Xử lý khi nút trang kế tiếp được click

        Args:
            data: Dữ liệu sự kiện
        """
        if self.table._page < self.table._total_pages:
            self.table.setPage(self.table._page + 1)

    def on_prev_page_clicked(self, data: Dict[str, Any] = None):
        """Xử lý khi nút trang trước được click

        Args:
            data: Dữ liệu sự kiện
        """
        if self.table._page > 1:
            self.table.setPage(self.table._page - 1)

    def on_first_page_clicked(self, data: Dict[str, Any] = None):
        """Xử lý khi nút trang đầu tiên được click

        Args:
            data: Dữ liệu sự kiện
        """
        self.table.setPage(1)

    def on_last_page_clicked(self, data: Dict[str, Any] = None):
        """Xử lý khi nút trang cuối cùng được click

        Args:
            data: Dữ liệu sự kiện
        """
        self.table.setPage(self.table._total_pages)

    def on_table_header_clicked(self, section: int, data: Dict[str, Any] = None):
        """Handle table header clicked

        Args:
            section: Header section index
            data: Event data
        """
        # Sorting is handled by QTableView's sorting mechanism
        # We only need to emit signal about sort change
        if section < 0 or section >= len(self.table._model._visible_columns):
            return

        column_key = self.table._model._visible_columns[section]
        header = self.table.tableView.horizontalHeader()
        sort_order = header.sortIndicatorOrder()

        self.table.sortChanged.emit(column_key, SortOrder.ASCENDING if sort_order == 0 else SortOrder.DESCENDING)

    def on_table_row_clicked(self, index: QModelIndex, data: Dict[str, Any] = None):
        """Handle table row clicked

        Args:
            index: Model index from the view (proxy model)
            data: Event data
        """
        if not index.isValid():
            return

        # Map view (proxy) index to source model
        sourceIndex = self.table._proxyModel.mapToSource(index)
        sourceRow = sourceIndex.row()
        if sourceRow > -1:
            # Emit signal with correct source row and data
            self.table.rowSelected.emit(sourceRow, self.table._model._data[sourceRow])
        # Check if this is expandable row (has children)
        if self.table._model._row_collapsing_enabled:
            if self.table._model.isRowCollapsable(sourceRow):
                # Toggle expansion when clicking anywhere on row
                self.table._model.toggleRowExpanded(sourceRow)
                return



    def on_column_visibility_changed(self, data: Dict[str, Any] = None):
        """Handle column visibility button clicked

        Args:
            data: Event data
        """
        # Show column visibility menu
        button = self.widget_manager.get('columnVisibilityButton')
        menu = QMenu(self.table)

        # Add column visibility actions
        for i, key in enumerate(self.table._model._column_keys):
            # Lấy header text từ vị trí tương ứng trong _column_keys
            try:
                header_index = self.table._model._column_keys.index(key)
                header_text = self.table._model._headers[header_index]
            except (ValueError, IndexError):
                header_text = key  # Fallback nếu không tìm thấy header

            action = menu.addAction(header_text)
            action.setCheckable(True)
            action.setChecked(key in self.table._model._visible_columns)
            action.triggered.connect(lambda checked, k=key: self.table._toggleColumnVisibility(k, checked))

        # Show menu under button
        pos = button.mapToGlobal(button.rect().bottomLeft())
        menu.popup(pos)

    def on_page_number_clicked(self, data: Dict[str, Any] = None):
        """Handle page number button clicked

        Args:
            data: Event data
        """
        sender = self.widget_manager.sender()
        if sender:
            try:
                page = int(sender.text())
                self.table.setPage(page)
            except (ValueError, TypeError):
                pass
