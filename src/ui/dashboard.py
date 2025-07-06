from PyQt5.QtWidgets import (QWidget, QHBoxLayout, QVBoxLayout, QLabel, QMessageBox, 
                            QLineEdit, QPushButton, QDialog, QTableWidget, 
                            QTableWidgetItem, QHeaderView)
from PyQt5.QtCore import Qt
from widgets.dashboard_card import DashboardCard
from widgets.paginated_table import PaginatedTable
from db import get_all_medicines, update_medicine, delete_medicine, get_sales_history
from widgets.add_medicine_dialog import AddMedicineDialog
from datetime import datetime, timedelta

class DetailDialog(QDialog):
    def __init__(self, title, data, headers, parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setModal(True)
        self.setMinimumSize(600, 400)
        layout = QVBoxLayout()
        self.table = QTableWidget(len(data), len(headers))
        self.table.setHorizontalHeaderLabels(headers)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self._populate_table(data)
        layout.addWidget(self.table)
        self.setLayout(layout)

    def _populate_table(self, data):
        for row, row_data in enumerate(data):
            for col, value in enumerate(row_data):
                item = QTableWidgetItem(str(value))
                item.setTextAlignment(Qt.AlignCenter)
                self.table.setItem(row, col, item)

class Dashboard(QWidget):
    def __init__(self, user=None, parent=None):
        super().__init__(parent)
        self.user = user
        self.parent = parent
        self.setObjectName("InventoryDashboard")
        self.setStyleSheet("""
            QWidget#InventoryDashboard {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #ecf0f1, stop:1 #ffffff);
                border-radius: 10px;
                box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
            }
        """)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(25, 25, 25, 25)
        main_layout.setSpacing(25)

        # Header
        header = QLabel("Inventory")
        header.setStyleSheet("font-size: 18px; font-weight: bold; color: #2c3e50;")
        header.setAlignment(Qt.AlignLeft)
        main_layout.addWidget(header)

        # Cards row
        cards_layout = QHBoxLayout()
        cards_layout.setSpacing(20)

        self.card_total = DashboardCard("Total Medicines", 0, "In Stock", "#1abc9c")
        self.btn_total = QPushButton("👁️ Details")
        self.btn_total.setStyleSheet("background: #16a085; color: white; padding: 5px 10px; border-radius: 5px;")
        self.btn_total.clicked.connect(self.show_total_details)
        self.card_total.add_button(self.btn_total)

        self.card_sales = DashboardCard("Today's Sales", 0, "Invoices Today", "#8e44ad")
        self.btn_sales = QPushButton("👁️ Details")
        self.btn_sales.setStyleSheet("background: #8e44ad; color: white; padding: 5px 10px; border-radius: 5px;")
        self.btn_sales.clicked.connect(self.show_sales_details)
        self.card_sales.add_button(self.btn_sales)

        self.card_low_stock = DashboardCard("Low Stock", 0, "< 10 Units", "#e74c3c")
        self.btn_low_stock = QPushButton("👁️ Details")
        self.btn_low_stock.setStyleSheet("background: #c0392b; color: white; padding: 5px 10px; border-radius: 5px;")
        self.btn_low_stock.clicked.connect(self.show_low_stock_details)
        self.card_low_stock.add_button(self.btn_low_stock)

        self.card_expiry = DashboardCard("Expiring Soon", 0, "Next 30 Days", "#f1c40f")
        self.btn_expiry = QPushButton("👁️ Details")
        self.btn_expiry.setStyleSheet("background: #f39c12; color: white; padding: 5px 10px; border-radius: 5px;")
        self.btn_expiry.clicked.connect(self.show_expiring_details)
        self.card_expiry.add_button(self.btn_expiry)

        self.cards = [self.card_total, self.card_sales, self.card_low_stock, self.card_expiry]
        for card in self.cards:
            card.setStyleSheet("border: 1px solid #ddd; border-radius: 10px; box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);")
            cards_layout.addWidget(card)
        main_layout.addLayout(cards_layout)

        # Search bar
        search_layout = QHBoxLayout()
        search_label = QLabel("🔍 Search:")
        search_label.setStyleSheet("font-size: 16px; color: #34495e;")
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search by name, batch, strength, expiry...")
        self.search_input.setStyleSheet("""
            QLineEdit {
                padding: 10px; border: 2px solid #bdc3c7; border-radius: 10px;
                font-size: 14px; background: white; box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
            }
            QLineEdit:focus { border-color: #1abc9c; outline: none; }
        """)
        search_layout.addWidget(search_label)
        search_layout.addWidget(self.search_input)
        main_layout.addLayout(search_layout)

        # Inventory table
        self.table = PaginatedTable()
        self.table.setStyleSheet("""
            QTableWidget {
                background: white; border-radius: 10px; border: 1px solid #ddd;
                box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
            }
            QTableWidget::item { padding: 8px; }
            QTableWidget::item:alternate { background: #f9f9f9; }
            QHeaderView::section {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #1abc9c, stop:1 #16a085);
                color: white; font-weight: bold; padding: 10px; border: none;
                border-radius: 8px 8px 0 0;
            }
        """)
        main_layout.addWidget(self.table)

        # No medicines found label
        self.no_medicines_label = QLabel("🚫 No medicines found")
        self.no_medicines_label.setStyleSheet("""
            color: #e74c3c; font-size: 16px; font-weight: bold; text-align: center;
            padding: 15px; background: #fef2f2; border-radius: 10px; box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        """)
        self.no_medicines_label.setAlignment(Qt.AlignCenter)
        self.no_medicines_label.hide()
        main_layout.addWidget(self.no_medicines_label)

        # Store data
        self.medicines = []
        self.low_stock_meds = []
        self.expiring_meds = []
        self.today_sales = []

        # Connect signals
        self.table.edit_requested.connect(self.edit_medicine)
        self.table.delete_requested.connect(self.delete_medicine)
        self.search_input.textChanged.connect(self.filter_table)

        self.load_table_data()

    # Replace load_table_data
    def load_table_data(self):
        self.medicines = get_all_medicines()
        today = datetime.now().strftime("%Y-%m-%d")
        self.today_sales = [sale for sale in get_sales_history() if sale.get('date', '').startswith(today)]
        self.low_stock_meds = [m for m in self.medicines if int(m.get("quantity", 0)) < 10]
        now = datetime.today()
        self.expiring_meds = [m for m in self.medicines if m.get("expiry_date") and 
                            now < datetime.strptime(m["expiry_date"], "%Y-%m-%d") <= now + timedelta(days=30)]
        self.table.set_data(self.medicines)
        self.update_dashboard_cards()

    def update_dashboard_cards(self):
        self.card_total.set_value(len(self.medicines))
        self.card_sales.set_value(len(self.today_sales))
        self.card_low_stock.set_value(len(self.low_stock_meds))
        self.card_expiry.set_value(len(self.expiring_meds))

    def filter_table(self):
        query = self.search_input.text().strip().lower()
        if not query:
            self.no_medicines_label.hide()
            self.table.set_data(self.medicines)
            return
        filtered = next((m for m in self.medicines if any(str(m.get(k, "")).lower().startswith(query) 
                                                        for k in ["name", "strength", "batch_no", 
                                                                  "expiry_date", "quantity", "unit_price"])), None)
        if filtered:
            self.no_medicines_label.hide()
            self.table.set_data([m for m in self.medicines if any(str(m.get(k, "")).lower().startswith(query) 
                                                                for k in ["name", "strength", "batch_no", 
                                                                          "expiry_date", "quantity", "unit_price"])])
        else:
            self.no_medicines_label.show()
            self.table.set_data([])

    def show_total_details(self):
        headers = ["ID", "Name", "Strength", "Batch No", "Expiry", "Qty", "Unit Price"]
        data = [[m["id"], m["name"], m.get("strength", "N/A"), m.get("batch_no", "N/A"), 
                 m.get("expiry_date", "N/A"), m.get("quantity", 0), f"${m.get('unit_price', 0):.2f}"] 
                for m in self.medicines]
        dialog = DetailDialog("Inventory Details", data, headers, self)
        dialog.exec_()

    def show_sales_details(self):
        headers = ["Sale ID", "Medicine", "Qty", "Customer", "Date"]
        data = [[s["id"], s["medicine_name"], s["quantity"], s.get("customer_name", "N/A"), s["date"]] 
                for s in self.today_sales]
        dialog = DetailDialog("Today's Sales Details", data, headers, self)
        dialog.exec_()

    def show_low_stock_details(self):
        headers = ["ID", "Name", "Strength", "Batch No", "Current Qty", "Unit Price"]
        data = [[m["id"], m["name"], m.get("strength", "N/A"), m.get("batch_no", "N/A"), 
                 m.get("quantity", 0), f"${m.get('unit_price', 0):.2f}"] for m in self.low_stock_meds]
        dialog = DetailDialog("Low Stock Details", data, headers, self)
        dialog.exec_()

    def show_expiring_details(self):
        headers = ["ID", "Name", "Strength", "Batch No", "Expiry Date", "Qty Left", "Days Left"]
        today = datetime.today()
        data = [[m["id"], m["name"], m.get("strength", "N/A"), m.get("batch_no", "N/A"), 
                 m.get("expiry_date", ""), m.get("quantity", 0), 
                 (datetime.strptime(m.get("expiry_date", ""), "%Y-%m-%d") - today).days 
                 if m.get("expiry_date") else "N/A"] for m in self.expiring_meds]
        dialog = DetailDialog("Expiring Soon Details", data, headers, self)
        dialog.exec_()

    def edit_medicine(self, med):
        try:
            dialog = AddMedicineDialog(self.parent, initial_data=med)
            if dialog.exec_():
                new_data = dialog.get_data()
                update_medicine(med["id"], new_data)
                self.load_table_data()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to edit medicine: {str(e)}")

    def delete_medicine(self, med_id):
        try:
            reply = QMessageBox.question(
                self, "Confirm Delete", "Are you sure you want to delete this medicine?",
                QMessageBox.Yes | QMessageBox.No
            )
            if reply == QMessageBox.Yes:
                delete_medicine(med_id)
                self.load_table_data()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to delete medicine: {str(e)}")