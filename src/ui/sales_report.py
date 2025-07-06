from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QHBoxLayout, QTableWidget, QTableWidgetItem, QPushButton, QHeaderView, QDateEdit, QWidget, QStatusBar, QMessageBox, QSizePolicy, QFileDialog
from PyQt5.QtCore import Qt, QDate
from db import get_sales_report_data # Assuming this new function will be in your db.py
import csv
from datetime import datetime

class SalesDialog(QDialog):
    def __init__(self, user=None, parent=None):
        super().__init__(parent)
        # Basic access control, similar to OrdersDialog
        if not user or user.get("role") != "admin":
            QMessageBox.critical(self, "Access Denied", "Only admins can view sales reports.")
            self.reject()
            return

        self.user = user
        self.setWindowTitle("Sales Report")
        self.setMinimumSize(1000, 700)
        self._cached_sales_data = [] # To store the detailed sales data for export

        self.setStyleSheet("""
            QDialog {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #f5f6fa, stop:1 #ffffff);
                border-radius: 12px;
            }
            QLabel {
                font-size: 28px;
                font-weight: bold;
                color: #2c3e50;
            }
            QLabel#header_label {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #6c5ce7, stop:1 #4834d4); /* Purple gradient */
                padding: 15px;
                border-radius: 10px;
                color: white;
                text-align: center;
                font-size: 24px;
            }
            QLabel#summary_label {
                font-size: 16px;
                font-weight: bold;
                color: #34495e;
                padding: 5px;
            }
            QTableWidget {
                background: white;
                border: 1px solid #e0e0e0;
                border-radius: 10px;
                gridline-color: #f0f0f0;
            }
            QTableWidget::item {
                padding: 8px;
            }
            QTableWidget::item:selected {
                background: #6c5ce7;
                color: white;
            }
            QHeaderView::section {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #6c5ce7, stop:1 #4834d4);
                color: white;
                font-weight: bold;
                padding: 10px;
                border: none;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
            }
            QPushButton {
                border-radius: 8px;
                padding: 8px 16px;
                min-width: 90px;
                font-weight: bold;
                border: none;
                color: white;
                font-size: 14px;
                transition: background 0.3s ease;
            }
            QPushButton#export_btn {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #0984e3, stop:1 #0062a3);
            }
            QPushButton#export_btn:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #0062a3, stop:1 #0984e3);
            }
            QDateEdit {
                border: 1px solid #d0d0d0;
                border-radius: 5px;
                padding: 5px;
                font-size: 14px;
                color: #34495e;
            }
            QStatusBar {
                background: #ecf0f1;
                color: #2c3e50;
                font-size: 13px;
                border-top: 1px solid #ddd;
                border-bottom-left-radius: 12px;
                border-bottom-right-radius: 12px;
            }
        """)

        # Main layout
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)

        # Header
        header_label = QLabel("Sales Report Overview")
        header_label.setObjectName("header_label")
        main_layout.addWidget(header_label)

        # Date Filter Layout
        date_filter_layout = QHBoxLayout()
        date_filter_layout.addWidget(QLabel("From:"))
        self.start_date_edit = QDateEdit(calendarPopup=True)
        self.start_date_edit.setDate(QDate.currentDate().addMonths(-1)) # Default to last month
        self.start_date_edit.setMinimumDate(QDate(2000, 1, 1)) # Set a reasonable minimum date
        self.start_date_edit.setMaximumDate(QDate.currentDate()) # Cannot select future date
        date_filter_layout.addWidget(self.start_date_edit)

        date_filter_layout.addWidget(QLabel("To:"))
        self.end_date_edit = QDateEdit(calendarPopup=True)
        self.end_date_edit.setDate(QDate.currentDate()) # Default to today
        self.end_date_edit.setMinimumDate(QDate(2000, 1, 1))
        self.end_date_edit.setMaximumDate(QDate.currentDate())
        date_filter_layout.addWidget(self.end_date_edit)

        self.apply_filter_btn = QPushButton("Apply Filter")
        self.apply_filter_btn.setStyleSheet("""
            QPushButton {
                background: #28a745; /* Green for apply */
                color: white;
                border-radius: 8px;
                padding: 6px 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: #218838;
            }
        """)
        self.apply_filter_btn.clicked.connect(self.load_sales_data)
        date_filter_layout.addWidget(self.apply_filter_btn)
        date_filter_layout.addStretch(1) # Push elements to left
        main_layout.addLayout(date_filter_layout)

        # Summary Section
        self.total_orders_label = QLabel("Total Orders: 0")
        self.total_orders_label.setObjectName("summary_label")
        self.total_quantity_label = QLabel("Total Quantity Sold: 0")
        self.total_quantity_label.setObjectName("summary_label")

        summary_grid_layout = QHBoxLayout()
        summary_grid_layout.addWidget(self.total_orders_label)
        summary_grid_layout.addWidget(self.total_quantity_label)
        summary_grid_layout.addStretch(1)
        main_layout.addLayout(summary_grid_layout)

        # Sales by Medicine Table
        sales_table_header = QLabel("Sales by Medicine")
        sales_table_header.setObjectName("header_label") # Reusing header style
        sales_table_header.setText("Sales by Medicine") # Override text
        sales_table_header.setStyleSheet(sales_table_header.styleSheet() + "font-size: 20px; padding: 10px;") # Smaller for sub-header
        main_layout.addWidget(sales_table_header)

        self.sales_table = QTableWidget()
        self.sales_table.setColumnCount(3)
        self.sales_table.setHorizontalHeaderLabels(["Medicine Name", "Total Quantity Sold", "Number of Orders"])
        self.sales_table.horizontalHeader().setStretchLastSection(True)
        self.sales_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        main_layout.addWidget(self.sales_table)

        # Export Button
        export_layout = QHBoxLayout()
        self.export_btn = QPushButton("⬇️ Export Sales Report")
        self.export_btn.setObjectName("export_btn")
        self.export_btn.setCursor(Qt.PointingHandCursor)
        self.export_btn.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.export_btn.clicked.connect(self.export_sales_report)
        export_layout.addStretch(1) # Push button to center/right
        export_layout.addWidget(self.export_btn)
        export_layout.addStretch(1)
        main_layout.addLayout(export_layout)

        # Status bar
        self.status_bar = QStatusBar()
        main_layout.addWidget(self.status_bar)

        self.setLayout(main_layout)
        self.load_sales_data() # Initial load of sales data

    def load_sales_data(self):
        """Loads sales data based on the selected date range."""
        start_date = self.start_date_edit.date().toString("yyyy-MM-dd")
        end_date = self.end_date_edit.date().toString("yyyy-MM-dd")

        if self.start_date_edit.date() > self.end_date_edit.date():
            self.status_bar.showMessage("Start date cannot be after end date.", 5000)
            return

        try:
            summary, sales_by_medicine = get_sales_report_data(start_date, end_date)

            # Update Summary Labels
            self.total_orders_label.setText(f"Total Orders: {summary['total_orders']}")
            self.total_quantity_label.setText(f"Total Quantity Sold: {summary['total_quantity_sold']}")

            # Populate Sales by Medicine Table
            self._cached_sales_data = sales_by_medicine # Cache for export
            self.sales_table.setRowCount(len(sales_by_medicine))
            self.sales_table.setUpdatesEnabled(False) # Optimization: Disable updates
            for row, item in enumerate(sales_by_medicine):
                self.sales_table.setItem(row, 0, QTableWidgetItem(item["medicine_name"]))
                self.sales_table.setItem(row, 1, QTableWidgetItem(str(item["total_quantity_sold"])))
                self.sales_table.setItem(row, 2, QTableWidgetItem(str(item["num_orders"])))
            self.sales_table.setUpdatesEnabled(True) # Optimization: Re-enable updates

            self.sales_table.resizeColumnsToContents()
            self.status_bar.showMessage(f"Sales data loaded for {start_date} to {end_date}.", 3000)

        except Exception as e:
            self.status_bar.showMessage(f"Error loading sales data: {str(e)}", 5000)

    def export_sales_report(self):
        """Exports the current sales report data to a CSV file."""
        if not self.user or self.user.get("role") != "admin":
            self.status_bar.showMessage("Access denied: Admin only.", 3000)
            return

        if not self._cached_sales_data:
            self.status_bar.showMessage("No sales data to export.", 3000)
            return

        try:
            file_name, _ = QFileDialog.getSaveFileName(
                self,
                "Save Sales Report",
                f"sales_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                "CSV Files (*.csv)"
            )

            if file_name:
                with open(file_name, 'w', newline='', encoding='utf-8') as csvfile:
                    fieldnames = ["medicine_name", "total_quantity_sold", "num_orders"]
                    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                    writer.writeheader()
                    for item in self._cached_sales_data:
                        writer.writerow(item)
                self.status_bar.showMessage(f"Sales report exported to {file_name}.", 3000)
        except Exception as e:
            self.status_bar.showMessage(f"Error exporting sales report: {str(e)}", 5000)

