from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel
from db import get_sales_history

class SalesReport(QDialog):
    def __init__(self, user=None, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Sales Report")
        layout = QVBoxLayout()
        layout.addWidget(QLabel("Sales Report"))
        sales = get_sales_history()
        if sales:
            layout.addWidget(QLabel(f"Total Sales: {len(sales)}"))
        self.setLayout(layout)