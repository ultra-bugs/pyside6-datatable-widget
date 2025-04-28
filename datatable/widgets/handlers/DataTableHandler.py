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

from typing import Any, Dict

from ...core.observer import Subscriber
from ...core.widget_manager import WidgetManager
from PySide6.QtCore import QSortFilterProxyModel, Qt


class DataTableHandler(Subscriber):
    """Handler for DataTable events"""

    def __init__(self, widget_manager: WidgetManager, events: list):
        super().__init__(events)
        self.widget_manager = widget_manager
        self.table = widget_manager.controller

    def on_search_text_changed(self, data: Dict[str, Any] = None):
        """Handle search text changed

        Args:
            data: Event data
        """
        search_term = self.widget_manager.get('searchInput').text()
        self.table._applySearch(search_term)

    def on_page_changed(self, data: Dict[str, Any] = None):
        """Handle page changed

        Args:
            data: Event data
        """
        page = self.widget_manager.get('pageSpinBox').value()
        self.table.setPage(page)

    def on_rows_per_page_changed(self, data: Dict[str, Any] = None):
        """Handle rows per page changed

        Args:
            data: Event data
        """
        combo = self.widget_manager.get('rowsPerPageCombo')
        rows_text = combo.currentText()
        try:
            rows = int(rows_text)
            self.table.setRowsPerPage(rows)
        except (ValueError, TypeError):
            pass

    def on_next_page_clicked(self, data: Dict[str, Any] = None):
        """Handle next page clicked

        Args:
            data: Event data
        """
        if self.table._page < self.table._total_pages:
            self.table.setPage(self.table._page + 1)

    def on_prev_page_clicked(self, data: Dict[str, Any] = None):
        """Handle previous page clicked

        Args:
            data: Event data
        """
        if self.table._page > 1:
            self.table.setPage(self.table._page - 1)

    def on_first_page_clicked(self, data: Dict[str, Any] = None):
        """Handle first page clicked

        Args:
            data: Event data
        """
        self.table.setPage(1)

    def on_last_page_clicked(self, data: Dict[str, Any] = None):
        """Handle last page clicked

        Args:
            data: Event data
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

        self.table.sortChanged.emit(
            column_key, sort_order.ASCENDING if sort_order == 0 else sort_order.DESCENDING
        )

    def on_table_row_clicked(self, index, data: Dict[str, Any] = None):
        """Handle table row clicked

        Args:
            index: Model index
            data: Event data
        """
        if not index.isValid():
            return

        # Map proxy index to source index
        source_index = self.table._proxy_model.mapToSource(index)
        row = source_index.row()

        # Check if it's the expand/collapse column and the first column
        if index.column() == 0 and self.table._model._row_collapsing_enabled:
            if self.table._model.isRowCollapsable(row):
                self.table._model.toggleRowExpanded(row)
                return

        # Emit signal
        self.table.rowSelected.emit(row, self.table._model._data[row])

    def on_column_visibility_changed(self, data: Dict[str, Any] = None):
        """Handle column visibility button clicked

        Args:
            data: Event data
        """
        # Show column visibility menu
        button = self.widget_manager.get('columnVisibilityButton')
        menu = self.table._header_menu

        # Clear and rebuild menu
        menu.clear()

        # Add column visibility actions
        model = self.table._model
        for key in model._column_keys:
            # Find the corresponding header for this key safely
            try:
                idx = model._column_keys.index(key)
                if idx < len(model._headers):
                    header_text = model._headers[idx]
                else:
                    header_text = key  # Fallback to the key name
            except (ValueError, IndexError):
                header_text = key  # Fallback to the key name

            action = menu.addAction(header_text)
            action.setCheckable(True)
            action.setChecked(key in model._visible_columns)

            # Store the column key as data on the action
            action.setData(key)
            action.triggered.connect(
                lambda checked, k=key: self.table._toggleColumnVisibility(k, checked)
            )

        # Show menu under button
        pos = button.mapToGlobal(button.rect().bottomLeft())
        menu.popup(pos)


class DataTableProxyModel(QSortFilterProxyModel):
    """Extended proxy model with advanced filtering capabilities"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._search_term = ''
        self._column_filters = {}  # {column_index: search_term}
        self._filter_enabled = True

    def setSearchTerm(self, term):
        """Set global search term"""
        self._search_term = term
        self.invalidateFilter()

    def setColumnFilter(self, column_index, term):
        """Set filter for specific column"""
        if term:
            self._column_filters[column_index] = term
        elif column_index in self._column_filters:
            del self._column_filters[column_index]
        self.invalidateFilter()

    def clearFilters(self):
        """Clear all filters"""
        self._search_term = ''
        self._column_filters.clear()
        self.invalidateFilter()

    def enableFiltering(self, enabled):
        """Enable or disable filtering"""
        self._filter_enabled = enabled
        self.invalidateFilter()

    def filterAcceptsRow(self, source_row, source_parent):
        """Custom filtering logic"""
        if not self._filter_enabled:
            return True

        model = self.sourceModel()

        # Nếu không có bộ lọc, hiển thị tất cả hàng
        if not self._search_term and not self._column_filters:
            return True

        # Kiểm tra bộ lọc toàn cục
        if self._search_term:
            row_matches = False
            # Kiểm tra từng cột trong hàng
            for col in range(model.columnCount()):
                index = model.index(source_row, col, source_parent)
                value = model.data(index, Qt.DisplayRole)

                # Sử dụng hàm tìm kiếm tùy chỉnh nếu có
                col_key = model._visible_columns[col]
                if col_key in model._search_funcs:
                    if model._search_funcs[col_key](value, self._search_term):
                        row_matches = True
                        break
                # Mặc định tìm trong chuỗi
                elif value is not None and self._search_term.lower() in str(value).lower():
                    row_matches = True
                    break

            if not row_matches:
                return False

        # Kiểm tra bộ lọc theo cột
        for col, term in self._column_filters.items():
            if col >= model.columnCount():
                continue

            index = model.index(source_row, col, source_parent)
            value = model.data(index, Qt.DisplayRole)

            # Sử dụng hàm tìm kiếm tùy chỉnh nếu có
            col_key = model._visible_columns[col]
            if col_key in model._search_funcs:
                if not model._search_funcs[col_key](value, term):
                    return False
            # Mặc định tìm trong chuỗi
            elif value is None or term.lower() not in str(value).lower():
                return False

        return True
