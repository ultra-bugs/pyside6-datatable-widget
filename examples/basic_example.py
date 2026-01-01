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
import sys
import datetime
import random
from typing import List, Dict, Any

from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QLabel
from PySide6.QtCore import QTimer

from packages.pdw.datatable import DataTable, DataType


class ExampleWindow(QMainWindow):
    """Example window demonstrating DataTable usage"""

    def __init__(self):
        super().__init__()
        self.setWindowTitle('DataTable Example')
        self.resize(800, 600)

        # Central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # Create DataTable
        self.data_table = DataTable()
        layout.addWidget(self.data_table)

        # Create sample data
        data = self._create_sample_data()

        # Set up columns (key, header, data_type)
        columns = [
            ('id', 'ID', DataType.NUMERIC),
            ('name', 'Name', DataType.STRING),
            ('position', 'Position', DataType.STRING),
            ('office', 'Office', DataType.STRING),
            ('age', 'Age', DataType.NUMERIC),
            ('start_date', 'Start Date', DataType.DATE),
            ('salary', 'Salary', DataType.NUMERIC),
            ('active', 'Active', DataType.BOOLEAN),
        ]

        # Connect signals
        self.data_table.rowSelected.connect(self.on_row_selected)
        self.data_table.sortChanged.connect(self.on_sort_changed)

        # Apply data and columns
        self.data_table.setColumns(columns)
        self.data_table.setData(data)

        # Make the salary column sum visible at the bottom
        status_label = QLabel('Total Salary: $0')
        layout.addWidget(status_label)

        # Update salary sum when data changes
        def update_salary_sum():
            salary_sum = self.data_table.getAggregateValue('salary', 'sum')
            if salary_sum is not None:
                status_label.setText(f'Total Salary: ${salary_sum:,.2f}')

        update_salary_sum()
        self.data_table._model.dataChanged.connect(update_salary_sum)

    def _create_sample_data(self) -> List[Dict[str, Any]]:
        """Create sample data for the table

        Returns:
            List of row data dictionaries
        """
        names = [
            'Airi Satou',
            'Angelica Ramos',
            'Ashton Cox',
            'Bradley Greer',
            'Brenden Wagner',
            'Brielle Williamson',
            'Bruno Nash',
            'Caesar Vance',
            'Cara Stevens',
            'Cedric Kelly',
        ]

        positions = [
            'Accountant',
            'Chief Executive Officer (CEO)',
            'Junior Technical Author',
            'Software Engineer',
            'Software Engineer',
            'Integration Specialist',
            'Software Engineer',
            'Pre-Sales Support',
            'Sales Assistant',
            'Senior Javascript Developer',
        ]

        offices = ['Tokyo', 'London', 'San Francisco', 'London', 'San Francisco', 'New York', 'London', 'New York', 'New York', 'Edinburgh']

        ages = [33, 47, 66, 41, 28, 61, 38, 21, 46, 22]

        start_dates = [
            datetime.date(2008, 11, 28),
            datetime.date(2009, 10, 9),
            datetime.date(2009, 1, 12),
            datetime.date(2012, 10, 13),
            datetime.date(2011, 6, 7),
            datetime.date(2012, 12, 2),
            datetime.date(2011, 5, 3),
            datetime.date(2011, 12, 12),
            datetime.date(2011, 12, 6),
            datetime.date(2012, 3, 29),
        ]

        salaries = [162700, 1200000, 86000, 132000, 145000, 372000, 163500, 106450, 145600, 433060]

        data = []
        for i in range(len(names)):
            row = {
                'id': i + 1,
                'name': names[i],
                'position': positions[i],
                'office': offices[i],
                'age': ages[i],
                'start_date': start_dates[i],
                'salary': salaries[i],
                'active': random.choice([True, False]),
            }
            data.append(row)

        return data

    def on_row_selected(self, row: int, row_data: Dict[str, Any]) -> None:
        """Handle row selected

        Args:
            row: Row index
            row_data: Row data
        """
        print(f'Row {row} selected: {row_data["name"]}')

        # Calculate row's salary as percentage of total
        salary = row_data['salary']
        total_salary = self.data_table.getAggregateValue('salary', 'sum')
        percentage = (salary / total_salary) * 100 if total_salary else 0

        print(f'Salary: ${salary:,.2f} ({percentage:.1f}% of total)')

    def on_sort_changed(self, column_key: str, sort_order) -> None:
        """Handle sort changed

        Args:
            column_key: Column key
            sort_order: Sort order
        """
        order_str = 'ascending' if sort_order.value == 0 else 'descending'
        print(f'Table sorted by {column_key} in {order_str} order')


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = ExampleWindow()
    window.show()
    sys.exit(app.exec())
