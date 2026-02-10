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
from __future__ import annotations

from typing import Any, Dict, TYPE_CHECKING, Tuple, Union

from PySide6.QtCore import QItemSelectionModel, QModelIndex, Qt, QSortFilterProxyModel, QAbstractItemModel
from PySide6.QtWidgets import QHeaderView, QMenu


from ...core.Observer import Subscriber
from ...core.WidgetManager import WidgetManager
from ...models.datatable_model import DataTableModel, DataType, SortOrder

if TYPE_CHECKING:
    from ..FilterState import FilterState


class DataTableProxyModel(QSortFilterProxyModel):
    '''Proxy model that reads filter criteria from FilterState.

    Does NOT hold its own filter state — everything is delegated to FilterState.
    Applies search + type + pagination filters (all read from FilterState).
    '''

    def __init__(self, filterState: 'FilterState', parent=None):
        super().__init__(parent)
        self._filterState = filterState

    def invalidateAndRefresh(self) -> None:
        '''Trigger re-evaluation of filterAcceptsRow for all rows.'''
        self._filterState._invalidateCache()
        self.invalidateFilter()

    def countFilteredRows(self) -> int:
        '''Count rows matching search + type filters ONLY (ignoring pagination).

        Used by FilterState.filteredCountFn to compute totalPages correctly.
        '''
        model = self.sourceModel()
        if model is None:
            return 0
        count = 0
        emptyParent = QModelIndex()
        for row in range(model.rowCount()):
            if self._matchesSearchAndType(row, emptyParent):
                count += 1
        return count

    def filterAcceptsRow(self, sourceRow: int, sourceParent: QModelIndex) -> bool:
        '''Combined filter: search + type + pagination. Reads from FilterState.'''
        # 1. Search + Type filter
        if not self._matchesSearchAndType(sourceRow, sourceParent):
            return False

        # 2. Pagination — applied AFTER search+type filtering
        #    We need to count which "filtered index" this row is at,
        #    then check if that index falls within the current page range.
        state = self._filterState
        start, end = state.paginationRange
        filteredIdx = self._getFilteredIndex(sourceRow, sourceParent)
        if filteredIdx < start or filteredIdx >= end:
            return False

        return True

    def _matchesSearchAndType(self, sourceRow: int, sourceParent: QModelIndex) -> bool:
        '''Check if a row matches search text and data type filters.'''
        model: Union[DataTableModel, QAbstractItemModel] = self.sourceModel()
        state = self._filterState

        # Type filter — row-level: show row only if it has a non-null value
        # in at least one column whose DataType matches the filter.
        if state.dataTypeFilter is not None:
            typeMatch = False
            for colIdx, colKey in enumerate(model._visible_columns):
                if model._column_types.get(colKey) != state.dataTypeFilter:
                    continue
                # Column type matches — check if this row has a value
                index = model.index(sourceRow, colIdx, sourceParent)
                value = model.data(index, Qt.DisplayRole)
                if value is not None and str(value).strip() != '':
                    typeMatch = True
                    break
            if not typeMatch:
                return False

        # Search filter
        if state.searchText:
            searchMatch = False
            searchTerm = state.searchText

            for colIdx, colKey in enumerate(model._visible_columns):
                index = model.index(sourceRow, colIdx, sourceParent)
                value = model.data(index, Qt.DisplayRole)

                if colKey in model._search_funcs:
                    if model._search_funcs[colKey](value, searchTerm):
                        searchMatch = True
                        break
                elif value is not None and searchTerm.lower() in str(value).lower():
                    searchMatch = True
                    break

            if not searchMatch:
                return False

        return True

    def _getFilteredIndex(self, sourceRow: int, sourceParent: QModelIndex) -> int:
        '''Get the position of sourceRow among all search+type-matched rows.

        This gives us the "filtered index" so we can apply pagination correctly.
        '''
        count = 0
        for row in range(sourceRow):
            if self._matchesSearchAndType(row, sourceParent):
                count += 1
        return count


class DataTableHandler(Subscriber):
    '''Handler for DataTable events.

    Responsibility: parse UI input values → call FilterFacade methods.
    No direct filter logic, no proxy manipulation.
    '''

    # Type filter index → DataType mapping
    TYPE_MAP = {
        0: None,            # All Types
        1: DataType.NUMERIC,
        2: DataType.STRING,  # One Line Text
        3: DataType.STRING,  # Text (multiline)
        4: DataType.DATE,
        5: DataType.BOOLEAN,
    }

    def __init__(self, widget_manager: WidgetManager, events: list):
        super().__init__(events)
        self.widget_manager = widget_manager
        from ... import DataTable
        self.table: DataTable = widget_manager.controller

    def on_selection_changed(self, selected: QItemSelectionModel, deselected: QItemSelectionModel):
        '''Handle selection changes.'''
        self.table.selectionChanged.emit(selected, deselected)

    def on_search_text_changed(self, text: str, data: Dict[str, Any] = None):
        '''Handle search text changed → delegate to Facade.'''
        self.table._filterFacade.setSearch(text)

    def on_type_filter_changed(self, index: int, data: Dict[str, Any] = None):
        '''Handle type filter changed → parse index, delegate to Facade.'''
        dataType = self.TYPE_MAP.get(index)
        self.table._filterFacade.setTypeFilter(dataType)

    @staticmethod
    def getSourceIdx(index, returnTuple=False) -> QModelIndex | Tuple[QModelIndex, DataTableModel]:
        model = index.model()
        while hasattr(model, 'mapToSource'):
            index = model.mapToSource(index)
            model = model.sourceModel()
        return index if not returnTuple else (index, model)

    def on_table_row_clicked(self, index: QModelIndex, data: Dict[str, Any] = None):
        '''Handle table row clicked.'''
        if not index.isValid():
            return

        # Map view (proxy) index to source model
        sourceIndex = self.table._proxyModel.mapToSource(index)
        sourceRow = sourceIndex.row()

        # Check if this is expandable row (has children)
        if self.table._model._row_collapsing_enabled:
            if self.table._model.isRowCollapsable(sourceRow):
                self.table._model.toggleRowExpanded(sourceRow)
                return

        if sourceRow > -1:
            self.table.rowSelected.emit(sourceRow, self.table._model._data[sourceRow])

    def on_page_changed(self, page: int, data: Dict[str, Any] = None):
        '''Handle page spinbox value changed → delegate to Facade.'''
        self.table._filterFacade.setPage(page)

    def on_rows_per_page_changed(self, index: int, data: Dict[str, Any] = None):
        '''Handle rows-per-page combobox changed → parse value, delegate to Facade.'''
        combo = self.widget_manager.get('rowsPerPageCombo')
        try:
            rows = int(combo.currentText())
            self.table._filterFacade.setItemsPerPage(rows)
        except (ValueError, TypeError):
            pass

    def on_next_page_clicked(self, data: Dict[str, Any] = None):
        '''Navigate to next page.'''
        state = self.table._filterState
        if state.currentPage < state.totalPages:
            self.table._filterFacade.setPage(state.currentPage + 1)

    def on_prev_page_clicked(self, data: Dict[str, Any] = None):
        '''Navigate to previous page.'''
        state = self.table._filterState
        if state.currentPage > 1:
            self.table._filterFacade.setPage(state.currentPage - 1)

    def on_first_page_clicked(self, data: Dict[str, Any] = None):
        '''Navigate to first page.'''
        self.table._filterFacade.setPage(1)

    def on_last_page_clicked(self, data: Dict[str, Any] = None):
        '''Navigate to last page.'''
        state = self.table._filterState
        self.table._filterFacade.setPage(state.totalPages)

    def on_table_header_clicked(self, section: int, data: Dict[str, Any] = None):
        '''Handle table header clicked — emit sort signal.'''
        if section < 0 or section >= len(self.table._model._visible_columns):
            return

        column_key = self.table._model._visible_columns[section]
        header = self.table.tableView.horizontalHeader()
        sort_order = header.sortIndicatorOrder()

        self.table.sortChanged.emit(
            column_key,
            SortOrder.ASCENDING if sort_order == 0 else SortOrder.DESCENDING,
        )

    def on_column_visibility_changed(self, data: Dict[str, Any] = None):
        '''Handle column visibility button clicked.'''
        button = self.widget_manager.get('columnVisibilityButton')
        menu = QMenu(self.table)

        for i, key in enumerate(self.table._model._column_keys):
            try:
                headerIndex = self.table._model._column_keys.index(key)
                headerText = self.table._model._headers[headerIndex]
            except (ValueError, IndexError):
                headerText = key

            action = menu.addAction(headerText)
            action.setCheckable(True)
            action.setChecked(key in self.table._model._visible_columns)
            action.triggered.connect(lambda checked, k=key: self.table._toggleColumnVisibility(k, checked))

        pos = button.mapToGlobal(button.rect().bottomLeft())
        menu.popup(pos)

    def on_page_number_clicked(self, data: Dict[str, Any] = None):
        '''Handle page number button clicked.'''
        sender = self.widget_manager.sender()
        if sender:
            try:
                page = int(sender.text())
                self.table._filterFacade.setPage(page)
            except (ValueError, TypeError):
                pass
