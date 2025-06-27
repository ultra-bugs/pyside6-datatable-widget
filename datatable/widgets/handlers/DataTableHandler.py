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

from PySide6.QtCore import QModelIndex, Qt, QSortFilterProxyModel
from PySide6.QtWidgets import QHeaderView, QMenu

from ...core.Observer import Subscriber
from ...core.WidgetManager import WidgetManager
from ...models.datatable_model import DataType, SortOrder


class DataTableProxyModel(QSortFilterProxyModel):
    """Extensive proxy model with advanced filtration ability """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._search_term = ""
        self._data_type_filter = None
        self._pagination_start = 0
        self._pagination_end = 0
        self._pagination_enabled = False
        
    def setSearchTerm(self, term):
        """Set Search term"""
        self._search_term = term
        self.invalidateFilter()
        
    def setDataTypeFilter(self, data_type):
        """Set data type filter"""
        self._data_type_filter = data_type
        self.invalidateFilter()
        
    def setPaginationRange(self, start, end):
        """Set the range of the page"""
        self._pagination_start = start
        self._pagination_end = end
        self._pagination_enabled = True
        self.invalidateFilter()
        
    def disablePagination(self):
        """Turn off Pagination"""
        self._pagination_enabled = False
        self.invalidateFilter()
        
    def filterAcceptsRow(self, source_row, source_parent):
        """Check if a row should be displayed"""
        # Kiểm tra phân trang
        if self._pagination_enabled:
            if source_row < self._pagination_start or source_row >= self._pagination_end:
                return False
                
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
        self._apply_combined_filters()
        
    def on_type_filter_changed(self, index: int, data: Dict[str, Any] = None):
        """Handle type filter changed
        
        Args:
            index: Type filter index
            data: Event data
        """
        self._apply_combined_filters()
        
    def _apply_combined_filters(self):
        """Apply both text search and type filters together (AND condition)"""
        search_term = self.widget_manager.get("searchLineEdit").text()
        type_index = self.widget_manager.get("typeComboBox").currentIndex()
        
        # Convert type index to DataType
        type_map = {
            0: None,  # All Types
            1: DataType.NUMERIC,
            2: DataType.STRING,  # One Line Text
            3: DataType.STRING,  # Text (multiline) 
            4: DataType.DATE,
            5: DataType.BOOLEAN
        }
        
        data_type = type_map.get(type_index)
        
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
        self.widget_manager.get("pageSpinBox").setValue(1)
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
        combo = self.widget_manager.get("rowsPerPageCombo")
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
        
        self.table.sortChanged.emit(
            column_key, 
            SortOrder.ASCENDING if sort_order == 0 else SortOrder.DESCENDING
        )
        
    def on_table_row_clicked(self, index: QModelIndex, data: Dict[str, Any] = None):
        """Handle table row clicked
        
        Args:
            index: Model index
            data: Event data
        """
        import inspect
        print("on_table_row_clicked", inspect.getframeinfo(inspect.currentframe()))
        breakpoint()
        if not index.isValid():
            return
            
        # Map proxy index to source index
        if hasattr(self.table, '_proxy_model') and self.table._proxy_model:
            source_index = self.table._proxy_model.mapToSource(index)
            row = source_index.row()
        else:
            row = index.row()
        
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
        button = self.widget_manager.get("columnVisibilityButton")
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
            action.triggered.connect(
                lambda checked, k=key: self.table._toggleColumnVisibility(k, checked)
            )
            
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
