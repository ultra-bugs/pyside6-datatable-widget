# PySide6 DataTable

A powerful DataTable widget for PySide6 applications with functionality similar to jQuery DataTable.

## Features

- **Customizable Table**: Easily configure columns, types, and formatting
- **Data Type Detection**: Automatically detect and handle different data types
- **Type-based Sorting**: Different column types sort appropriately
- **Search Functionality**: Global and column-specific search
- **Row Collapsing**: Support for expandable/collapsible rows
- **Pagination**: Built-in pagination with configurable page sizes
- **Column Visibility**: Show/hide columns easily
- **Aggregation Functions**: Calculate sums, averages, percentages, etc.
- **Custom Formatting**: Format data display for different column types
- **Observer Pattern**: Event-driven architecture for clear code organization

## Installation

```bash
pip install pyside6-datatable-widget
```

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
            ("active", "Active", DataType.BOOLEAN)
        ]
        
        # Set up data
        data = [
            {"id": 1, "name": "John", "age": 30, "active": True},
            {"id": 2, "name": "Jane", "age": 25, "active": False},
            {"id": 3, "name": "Bob", "age": 40, "active": True}
        ]
        
        # Apply to table
        self.data_table.setColumns(columns)
        self.data_table.setData(data)
        
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

## API Reference

### DataTable

Main widget class that provides the UI and functionality.

#### Methods

- `setData(data)`: Set table data
- `setColumns(columns)`: Set table columns
- `setVisibleColumns(columns)`: Set which columns are visible
- `enableRowCollapsing(enabled, child_row_key)`: Enable/disable row collapsing
- `search(term)`: Search the table
- `sort(column_key, order)`: Sort the table
- `setPage(page)`: Set current page
- `setRowsPerPage(rows)`: Set rows per page
- `getData()`: Get current table data
- `getSelectedRow()`: Get selected row data
- `getAggregateValue(column_key, agg_type)`: Get aggregate value for column

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

## License

MIT
