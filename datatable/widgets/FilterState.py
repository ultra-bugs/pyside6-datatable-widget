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

import math
from typing import Any, Dict, List, Optional

from ..models.datatable_model import DataType


class FilterState:
    '''Single source of truth for all filter-related state in DataTable.

    Holds references to raw data, search/type filters, and pagination config.
    Computed properties (totalItems, filteredCount, totalPages) are always
    derived from the current state — never stale.
    '''

    def __init__(self):
        self._rawData: List[Dict[str, Any]] = []
        self._searchText: str = ''
        self._dataTypeFilter: Optional[DataType] = None
        self._currentPage: int = 1
        self._itemsPerPage: int = 25
        # Cache for filtered count (invalidated on filter change)
        self._filteredCountCache: Optional[int] = None
        # Callback to count filtered rows (set by FilterFacade)
        self._filteredCountFn: Optional[callable] = None

    # --- Raw data ---

    @property
    def rawData(self) -> List[Dict[str, Any]]:
        return self._rawData

    def setRawData(self, data: List[Dict[str, Any]]) -> None:
        '''Set raw data reference (not a copy).'''
        self._rawData = data
        self._invalidateCache()

    # --- Search ---

    @property
    def searchText(self) -> str:
        return self._searchText

    @searchText.setter
    def searchText(self, value: str) -> None:
        if self._searchText != value:
            self._searchText = value
            self._invalidateCache()

    # --- Type filter ---

    @property
    def dataTypeFilter(self) -> Optional[DataType]:
        return self._dataTypeFilter

    @dataTypeFilter.setter
    def dataTypeFilter(self, value: Optional[DataType]) -> None:
        if self._dataTypeFilter != value:
            self._dataTypeFilter = value
            self._invalidateCache()

    # --- Pagination ---

    @property
    def currentPage(self) -> int:
        return self._currentPage

    @currentPage.setter
    def currentPage(self, value: int) -> None:
        clamped = max(1, min(value, self.totalPages))
        self._currentPage = clamped

    @property
    def itemsPerPage(self) -> int:
        return self._itemsPerPage

    @itemsPerPage.setter
    def itemsPerPage(self, value: int) -> None:
        if value > 0 and self._itemsPerPage != value:
            self._itemsPerPage = value
            self._invalidateCache()
            # Clamp current page after items-per-page change
            self._currentPage = max(1, min(self._currentPage, self.totalPages))

    # --- Computed properties ---

    @property
    def totalItems(self) -> int:
        '''Total items in raw data (before any filter).'''
        return len(self._rawData)

    @property
    def filteredCount(self) -> int:
        '''Number of rows passing search + type filter.

        Uses proxy model rowCount when available, falls back to totalItems.
        '''
        if self._filteredCountCache is not None:
            return self._filteredCountCache
        if self._filteredCountFn is not None:
            self._filteredCountCache = self._filteredCountFn()
            return self._filteredCountCache
        return self.totalItems

    @property
    def totalPages(self) -> int:
        '''Total pages based on filtered count and items per page.'''
        count = self.filteredCount
        if count == 0:
            return 1
        return math.ceil(count / self._itemsPerPage)

    @property
    def paginationRange(self) -> tuple[int, int]:
        '''(start, end) indices for the current page (0-based, end exclusive).'''
        start = (self._currentPage - 1) * self._itemsPerPage
        end = min(start + self._itemsPerPage, self.filteredCount)
        return (start, end)

    # --- Helpers ---

    def reset(self) -> None:
        '''Reset all filters to defaults.'''
        self._searchText = ''
        self._dataTypeFilter = None
        self._currentPage = 1
        self._invalidateCache()

    def setFilteredCountFn(self, fn: callable) -> None:
        '''Set callback to compute filtered row count (typically proxy.rowCount).'''
        self._filteredCountFn = fn

    def _invalidateCache(self) -> None:
        '''Invalidate the filtered count cache.'''
        self._filteredCountCache = None
