# PySide6 DataTable

A powerful DataTable widget for PySide6 applications with functionality similar to jQuery DataTable.

## Features

- **Customizable Table**: Easily configure columns, types, and formatting
- **Data Type Detection**: Automatically detect and handle different data types [NOT-IMPLEMENTED-YET]
- **Type-based Sorting**: Different column types sort appropriately
- **Search Functionality**: Global and column-specific search
- **Row Collapsing**: Support for expandable/collapsible rows
- **Pagination**: Built-in pagination with configurable page sizes [SEMI-IMPLEMENTED]
- **Column Visibility**: Show/hide columns easily
- **Aggregation Functions**: Calculate sums, averages, percentages, etc. [SEMI-IMPLEMENTED]
- **Custom Formatting**: Format data display for different column types
- **Observer Pattern**: Event-driven architecture for clear code organization
- **Builtin-Delegates**: Packages has some useful delegates built-in for popular datatypes
- **Fluent-Interface**: Allow you channing calls on most methods of `DataTable` instance (return self)

## Installation

```bash
pip install pyside6-datatable-widget
```
## Versions - Current Release State

| Version | Date | Notes |
|---|---|---|


## Basic Usage

```python
import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget
from datatable import DataTable, DataType

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("DataTable Example")
        self.resize(800, 600)
        
        # Create central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # Create DataTable
        self.data_table = DataTable()
        layout.addWidget(self.data_table)
        
        # Set up columns (key, header, data_type)
        columns = [
            ("id", "ID", DataType.NUMERIC),
            ("name", "Name", DataType.STRING),
            ("age", "Age", DataType.NUMERIC),
            ("active", "Active", DataType.BOOLEAN),
            ("progress", "Progress", DataType.PROGRESS)
        ]
        
        # Set up data
        data = [
            {"id": 1, "name": "John", "age": 30, "active": True, "progress": 75},
            {"id": 2, "name": "Jane", "age": 25, "active": False, "progress": 30},
            {"id": 3, "name": "Bob", "age": 40, "active": True, "progress": 100}
        ]
        
        # Apply to table
        self.data_table.setColumns(columns).setData(data)
        
        # Connect signals
        self.data_table.rowSelected.connect(self.on_row_selected)
        
    def on_row_selected(self, row, row_data):
        print(f"Row {row} selected: {row_data}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
```

## Advanced Features

### Custom Column Formatting

```python
from datatable import DataTableModel

# Create model with custom formatting
model = DataTableModel()
model.setFormattingFunction("price", lambda value: f"${value:.2f}")
model.setFormattingFunction("percentage", lambda value: f"{value:.1f}%")

# Set model to table
data_table.setModel(model)
```

### Row Collapsing

```python
# Enable row collapsing
data_table.enableRowCollapsing(True, "subrows")

# Example data with subrows
data = [
    {
        "id": 1,
        "name": "Category A",
        "total": 1000,
        "subrows": [
            {"id": 101, "name": "Item A1", "total": 500},
            {"id": 102, "name": "Item A2", "total": 500}
        ]
    },
    {
        "id": 2,
        "name": "Category B",
        "total": 2000,
        "subrows": [
            {"id": 201, "name": "Item B1", "total": 1200},
            {"id": 202, "name": "Item B2", "total": 800}
        ]
    }
]

data_table.setData(data)

# Connect expansion signals
data_table.rowExpanded.connect(lambda row, data: print(f"Row {row} expanded"))
data_table.rowCollapsed.connect(lambda row, data: print(f"Row {row} collapsed"))
```

### Aggregation Functions

```python
# Get aggregate values
total = data_table.getAggregateValue("amount", "sum")
average = data_table.getAggregateValue("amount", "avg")
count = data_table.getAggregateValue("id", "count")

# Calculate percentage of a row value relative to total
row_data = data_table.getSelectedRow()
if row_data:
    amount = row_data["amount"]
    total = data_table.getAggregateValue("amount", "sum")
    percentage = data_table.calculateRowPercentage(row_index, "amount")
```

### Custom Search Functions

```python
# Set custom search function for a column
model.setSearchFunction("complex_data", lambda value, term: term in str(value["name"]))

# Search in table
data_table.search("search term")

# Search specific column
matching_rows = model.searchColumn("name", "John")
```

## Built-in Custom Delegates

The library provides several built-in delegates for enhanced data visualization.

### Progress Bar Delegate (`DataType.PROGRESS_BAR`)

A highly customizable progress bar delegate.

- **Default Behavior**: Displays a progress bar using the theme's highlight color.
- **Customization**:
    - `setProgressBarColor(column_key, color)`: Set a static base color.
    - `setProgressBarGradient(column_key, enabled)`: Enable a gradient effect (fade from 0% to 100% opacity).
    - `addProgressBarRange(column_key, min_pct, max_pct, color)`: Add color ranges (e.g., Red for <50%, Green for >80%).

```python
# Configure Progress Bar
self.data_table.setProgressBarColor('completion', "#3b82f6") # Base color
self.data_table.setProgressBarGradient('completion', True)   # Enable gradient

# Or use ranges
self.data_table.addProgressBarRange('completion', 0, 50, "#ef4444")   # Red for low
self.data_table.addProgressBarRange('completion', 50, 80, "#eab308")  # Yellow for medium
self.data_table.addProgressBarRange('completion', 80, 100, "#22c55e") # Green for high
```

### Icon Boolean Delegate (`DataType.ICON_BOOLEAN`)

Displays boolean values using SVG icons instead of text or checkboxes.

- **Default Behavior**: Displays a checkmark for `True` and an 'X' for `False`.
- **Customization**:
    - `setIconBooleanColors(column_key, yes_color, no_color)`: Customize the colors for the Yes and No states.

```python
# Configure Icon Boolean (defaults are Green/Red)
self.data_table.setIconBooleanColors('status', yes_color="#00FF00", no_color="#FF0000")
```

## API Reference

### DataTable

Main widget class that provides the UI and functionality.

#### Methods

- `setData(data) -> Self`: Set table data
- `appendRow(row_data) -> bool`: Append a row to the table
- `insertRow(row_index, row_data) -> bool`: Insert a row at a specific index
- `setColumns(columns) -> Self`: Set table columns
- `setVisibleColumns(columns) -> Self`: Set which columns are visible
- `enableRowCollapsing(enabled, child_row_key) -> Self`: Enable/disable row collapsing
- `setFormattingFunction(column_key, func) -> Self`: Set formatting function. Actually, this method is alias of `Model.setFormattingFunction`
- `search(term) -> Self`: Search the table
- `sort(column_key, order) -> Self`: Sort the table
- `setPage(page) -> Self`: Set current page
- `setRowsPerPage(rows) -> Self`: Set rows per page
- `getData()`: Get current table data
- `getSelectedRow()`: Get selected row data
- `getAggregateValue(column_key, agg_type)`: Get aggregate value for column
- `setUiSelectionType(mode, behavior) -> Self`: Set selection mode and behavior for the table view
- `selectAll() -> Self`: This is fluent alias of `Model.selectAll()`
- `selectNone() -> Self`: This is fluent alias of `Model.clearSelection()`
- `clearSelection() -> Self`: This is fluent alias of `DataTable.selectNone()`
- `selectInverse() -> Self`: Fluent select inverse
- `setProgressBarColor(column_key, color) -> Self`: Set base color for a progress bar column
- `setProgressBarGradient(column_key, enabled) -> Self`: Enable/disable gradient for a progress bar column
- `addProgressBarRange(column_key, min_pct, max_pct, color) -> Self`: Add a color range for a progress bar column
- `setIconBooleanColors(column_key, yes_color, no_color) -> Self`: Set colors for an icon boolean column

#### Signals

- `pageChanged(page)`: Emitted when page changes
- `rowSelected(row, row_data)`: Emitted when row is selected
- `rowExpanded(row, row_data)`: Emitted when row is expanded
- `rowCollapsed(row, row_data)`: Emitted when row is collapsed
- `dataFiltered(rows)`: Emitted when data is filtered
- `sortChanged(column, order)`: Emitted when sort order changes

### DataTableModel

Model class that manages data and operations.

#### Methods

- `setData(data)`: Set model data
- `setColumns(columns)`: Set model columns
- `setFormattingFunction(column_key, func)`: Set formatting function
- `setEditableColumns(editable_columns)`: Set which columns are editable
- `setVisibleColumns(visible_columns)`: Set which columns are visible
- `setSearchFunction(column_key, func)`: Set search function
- `setSortFunction(column_key, func)`: Set sort function
- `setAggregationFunction(column_key, agg_type, func)`: Set aggregation function
- `enableRowCollapsing(enabled, child_row_key)`: Enable row collapsing
- `search(term)`: Search all rows
- `searchColumn(column_key, term)`: Search specific column
- `aggregate(column_key, agg_type)`: Aggregate column values
- `calculateRowPercentage(row_index, column_key)`: Calculate row percentage

#### Signals

- `rowExpandedCollapsed(int, bool)`  : row, is_expanded. Emitted when a row, sub-rows expanded or collapsed
> Note: The model is child class of `QAbstractTableModel`. So these signals below are inherited (from `QAbstractItemModel`).

- `dataChanged(topLeft, bottomRight, roles)`: Emitted when data in the specified range has been modified.
- `headerDataChanged(orientation, first, last)`: Emitted when header data for a section changes.
- `layoutChanged()`: Emitted when layout of the model changes drastically.
- `layoutAboutToBeChanged()`: Emitted before a major layout change.
- `modelReset()`: Emitted after the model is reset.
- `rowsAboutToBeInserted(parent, start, end)`: Emitted before rows are inserted.
- `rowsInserted(parent, start, end)`: Emitted after rows are inserted.
- `rowsAboutToBeRemoved(parent, start, end)`: Emitted before rows are removed.
- `rowsRemoved(parent, start, end)`: Emitted after rows are removed.
- `columnsAboutToBeInserted(parent, start, end)`: Emitted before columns are inserted.
- `columnsInserted(parent, start, end)`: Emitted after columns are inserted.
- `columnsAboutToBeRemoved(parent, start, end)`: Emitted before columns are removed.
- `columnsRemoved(parent, start, end)`: Emitted after columns are removed.
- `rowsMoved(parent, start, end, destination, row)`: Emitted after rows are moved.
- `columnsMoved(parent, start, end, destination, column)`: Emitted after columns are moved.

## License

This project is licensed under the GNU General Public License v3.0 (GPLv3).  
See the [LICENSE](./LICENSE) file for details.
