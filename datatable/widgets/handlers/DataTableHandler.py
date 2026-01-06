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
#
from typing import Any, Dict

from PySide6.QtCore import QModelIndex, Qt, QSortFilterProxyModel, QAbstractItemModel
from PySide6.QtWidgets import QHeaderView, QMenu

from ...core.Observer import Subscriber
from ...core.WidgetManager import WidgetManager
from ...models.datatable_model import DataType, SortOrder


class PaginationProxyModel(QSortFilterProxyModel):
    """Proxy model for pagination"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._page = 1
        self._rows_per_page = 10

    def setPagination(self, page: int, rows_per_page: int):
        """Set pagination parameters"""
        self._page = page
        self._rows_per_page = rows_per_page
        self.invalidateFilter()

    def filterAcceptsRow(self, source_row: int, source_parent: QModelIndex) -> bool:
        """Filter rows based on pagination"""
        start = (self._page - 1) * self._rows_per_page
        end = start + self._rows_per_page
        return start <= source_row < end


class DataTableProxyModel(QSortFilterProxyModel):
    """Extensive proxy model with advanced filtration ability"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._search_term = ''
        self._data_type_filter = None

    def setSearchTerm(self, term):
        """Set Search term"""
        self._search_term = term
        self.invalidateFilter()

    def setDataTypeFilter(self, data_type):
        """Set data type filter"""
        self._data_type_filter = data_type
        self.invalidateFilter()

    def filterAcceptsRow(self, source_row, source_parent):
        """Check if a row should be displayed"""
        # Kiểm tra bộ lọc loại dữ liệu
        model = self.sourceModel()
        if self._data_type_filter is not None:
            type_match = False

            for col_idx, col_key in enumerate(model._visible_columns):
                col_type = model._column_types.get(col_key)
                if col_type == self._data_type_filter:
                    type_match = True
                    break

            if not type_match:
                return False

        # Kiểm tra từ khóa tìm kiếm
        if self._search_term:
            search_match = False

            for col_idx, col_key in enumerate(model._visible_columns):
                index = model.index(source_row, col_idx, source_parent)
                value = model.data(index, Qt.DisplayRole)

                # Sử dụng hàm tìm kiếm tùy chỉnh nếu có
                if col_key in model._search_funcs:
                    if model._search_funcs[col_key](value, self._search_term):
                        search_match = True
                        break
                # Tìm kiếm văn bản mặc định
                elif value is not None and self._search_term.lower() in str(value).lower():
                    search_match = True
                    break

            if not search_match:
                return False

        return True

    def lessThan(self, left: QModelIndex, right: QModelIndex) -> bool:
        """Sort using the sort functions defined in the source model"""
        source_model = self.sourceModel()

        # Map proxy indices to source indices
        source_left = self.mapToSource(left)
        source_right = self.mapToSource(right)

        # Get column key
        try:
            # Column index is the same for proxy and source in this setup
            col_key = source_model._visible_columns[left.column()]
        except (AttributeError, IndexError):
            return super().lessThan(left, right)

        # Get values from source model using mapped indices
        left_val = source_model.data(source_left, Qt.EditRole)
        right_val = source_model.data(source_right, Qt.EditRole)

        # Use custom sort function if available
        if hasattr(source_model, '_sort_funcs') and col_key in source_model._sort_funcs:
            sort_func = source_model._sort_funcs[col_key]
            try:
                return sort_func(left_val) < sort_func(right_val)
            except Exception:
                pass

        # Default comparison
        if left_val == right_val:
            return False

        if left_val is None:
            return False
        if right_val is None:
            return True

        try:
            return left_val < right_val
        except TypeError:
            return str(left_val) < str(right_val)


class DataTableHandler(Subscriber):
    """Handler for DataTable events"""

    def __init__(self, widget_manager: WidgetManager, events: list):
        super().__init__(events)
        self.widget_manager = widget_manager
        self.table = widget_manager.controller

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

        self.table.applyFilters(search_term, data_type)

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
            index: Model index from the view (potentially a proxy model)
            data: Event data
        """
        if not index.isValid():
            return

        # Map the view index back to the source model index
        pagination_index = index
        filter_index = self.table._paginationModel.mapToSource(pagination_index)
        source_index = self.table._proxyModel.mapToSource(filter_index)

        source_row = source_index.row()

        # Check if it's the expand/collapse column and the first column
        if index.column() == 0 and self.table._model._row_collapsing_enabled:
            if self.table._model.isRowCollapsable(source_row):
                self.table._model.toggleRowExpanded(source_row)
                return

        if source_row > -1:
            # Emit signal with the correct source row and data
            self.table.rowSelected.emit(source_row, self.table._model._data[source_row])

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
