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

from typing import TYPE_CHECKING, Callable, Optional

from ..models.datatable_model import DataType

if TYPE_CHECKING:
    from .FilterState import FilterState


class FilterFacade:
    '''Orchestrator for all filter operations on DataTable.

    Every filter action goes through this facade:
    1. Update FilterState properties
    2. Invalidate proxy model
    3. Trigger UI callback to refresh pagination controls

    Handler/Widget should never manipulate proxy or pagination directly.
    '''

    def __init__(
        self,
        state: 'FilterState',
        invalidateProxy: Callable[[], None],
        onStateChanged: Callable[[], None],
    ):
        self._state = state
        self._invalidateProxy = invalidateProxy
        self._onStateChanged = onStateChanged

    def setSearch(self, text: str) -> None:
        '''Update search text and refresh.'''
        self._state.searchText = text
        self._applyAndRefreshUI(resetPage=True)

    def setTypeFilter(self, dataType: Optional[DataType]) -> None:
        '''Update data type filter and refresh.'''
        self._state.dataTypeFilter = dataType
        self._applyAndRefreshUI(resetPage=True)

    def setPage(self, page: int) -> None:
        '''Navigate to a specific page.'''
        self._state.currentPage = page
        self._invalidateProxy()
        self._onStateChanged()

    def setItemsPerPage(self, count: int) -> None:
        '''Change items per page and refresh.'''
        self._state.itemsPerPage = count
        self._applyAndRefreshUI(resetPage=True)

    def refresh(self) -> None:
        '''Force full recalculation from current state.'''
        self._applyAndRefreshUI(resetPage=False)

    def _applyAndRefreshUI(self, resetPage: bool = False) -> None:
        '''Internal: invalidate proxy, optionally reset page, then update UI.'''
        self._invalidateProxy()
        if resetPage:
            self._state.currentPage = 1
        self._onStateChanged()
