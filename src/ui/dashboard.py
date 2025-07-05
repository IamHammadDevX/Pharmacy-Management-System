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
        
        # Create table
        self.table = QTableWidget()
        self.table.setColumnCount(len(headers))
        self.table.setHorizontalHeaderLabels(headers)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        
        # Populate data
        self.populate_table(data)
        
        layout.addWidget(self.table)
        self.setLayout(layout)
    
    def populate_table(self, data):
        self.table.setRowCount(len(data))
        for row_idx, row_data in enumerate(data):
            for col_idx, value in enumerate(row_data):
                item = QTableWidgetItem(str(value))
                item.setTextAlignment(Qt.AlignCenter)
                self.table.setItem(row_idx, col_idx, item)

class Dashboard(QWidget):
    def __init__(self, user=None, parent=None):
        super().__init__(parent)
        self.user = user
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(18)

        # Cards row
        self.cards = []
        cards_layout = QHBoxLayout()
        cards_layout.setSpacing(18)
        
        # Total Medicines Card
        self.card_total = DashboardCard("Total Medicines", 0, "In inventory", "#3864fa")
        self.btn_total = QPushButton("View Details")
        self.btn_total.clicked.connect(self.show_total_details)
        self.card_total.add_button(self.btn_total)
        
        # Today's Sales Card
        self.card_sales = DashboardCard("Today's Sales", 0, "Invoices created today", "#36b37e")
        self.btn_sales = QPushButton("View Details")
        self.btn_sales.clicked.connect(self.show_sales_details)
        self.card_sales.add_button(self.btn_sales)
        
        # Low Stock Card
        self.card_low_stock = DashboardCard("Low Stock", 0, "Below threshold", "#ffab00")
        self.btn_low_stock = QPushButton("View Details")
        self.btn_low_stock.clicked.connect(self.show_low_stock_details)
        self.card_low_stock.add_button(self.btn_low_stock)
        
        # Expiring Soon Card
        self.card_expiry = DashboardCard("Expiring Soon", 0, "Next 30 days", "#ff5630")
        self.btn_expiry = QPushButton("View Details")
        self.btn_expiry.clicked.connect(self.show_expiring_details)
        self.card_expiry.add_button(self.btn_expiry)
        
        self.cards = [self.card_total, self.card_sales, self.card_low_stock, self.card_expiry]
        for card in self.cards:
            cards_layout.addWidget(card)
        
        main_layout.addLayout(cards_layout)

        title = QLabel("Medicine Inventory")
        title.setStyleSheet("font-size:18px; font-weight:bold; margin-top:20px;")
        main_layout.addWidget(title)

        # Search bar layout
        search_bar_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search by name, batch, strength, expiry...")
        search_bar_layout.addWidget(QLabel("Search:"))
        search_bar_layout.addWidget(self.search_input)
        main_layout.addLayout(search_bar_layout)

        self.table = PaginatedTable()
        main_layout.addWidget(self.table)

        self.setLayout(main_layout)

        # Store all medicines for filtering
        self.medicines = []
        self.low_stock_meds = []
        self.expiring_meds = []
        self.today_sales = []

        # Connect edit/delete signals to their handlers
        self.table.edit_requested.connect(self.edit_medicine)
        self.table.delete_requested.connect(self.delete_medicine)

        self.load_table_data()

        # Connect search bar
        self.search_input.textChanged.connect(self.filter_table)

    def load_table_data(self):
        """Public method to reload medicine data"""
        medicines = get_all_medicines()
        self.medicines = medicines
        
        # Calculate today's sales
        today = datetime.now().strftime("%Y-%m-%d")
        sales = get_sales_history()
        self.today_sales = [sale for sale in sales if sale['date'].startswith(today)]
        
        # Find low stock medicines
        self.low_stock_meds = [m for m in medicines if int(m.get("quantity", 0)) < 10]
        
        # Find expiring soon medicines
        now = datetime.today()
        soon = now + timedelta(days=30)
        self.expiring_meds = []
        for m in medicines:
            expiry_str = m.get("expiry_date", "")
            if expiry_str:
                try:
                    expiry = datetime.strptime(expiry_str, "%Y-%m-%d")
                    if now < expiry <= soon:
                        self.expiring_meds.append(m)
                except ValueError:  # Use ValueError for datetime parsing errors
                    pass
        
        self.table.set_data(medicines)
        self.update_dashboard_cards()

    def update_dashboard_cards(self):
        # Update all card values
        self.card_total.set_value(len(self.medicines))
        self.card_sales.set_value(len(self.today_sales))
        self.card_low_stock.set_value(len(self.low_stock_meds))
        self.card_expiry.set_value(len(self.expiring_meds))

    def filter_table(self):
        query = self.search_input.text().strip().lower()
        if not query:
            self.table.set_data(self.medicines)
            return
        filtered = []
        for med in self.medicines:
            combined = " ".join([
                str(med.get("name", "")),
                str(med.get("strength", "")),
                str(med.get("batch_no", "")),
                str(med.get("expiry_date", "")),
                str(med.get("quantity", "")),
                str(med.get("unit_price", "")),
            ]).lower()
            if query in combined:
                filtered.append(med)
        self.table.set_data(filtered)

    def show_total_details(self):
        headers = ["ID", "Name", "Strength", "Batch No", "Expiry", "Qty", "Unit Price"]
        data = []
        for med in self.medicines:
            data.append([
                med["id"],
                med["name"],
                med.get("strength", "N/A"),
                med.get("batch_no", "N/A"),
                med.get("expiry_date", "N/A"),
                med.get("quantity", 0),
                f"${med.get('unit_price', 0):.2f}"
            ])
        dialog = DetailDialog("All Medicines Inventory", data, headers, self)
        dialog.exec_()

    def show_sales_details(self):
        headers = ["Sale ID", "Medicine", "Qty", "Customer", "Date"]
        data = []
        for sale in self.today_sales:
            data.append([
                sale["id"],
                sale["medicine_name"],
                sale["quantity"],
                sale.get("customer_name", "N/A"),
                sale["date"]
            ])
        dialog = DetailDialog("Today's Sales", data, headers, self)
        dialog.exec_()

    def show_low_stock_details(self):
        headers = ["ID", "Name", "Strength", "Batch No", "Current Qty", "Unit Price"]
        data = []
        for med in self.low_stock_meds:
            data.append([
                med["id"],
                med["name"],
                med.get("strength", "N/A"),
                med.get("batch_no", "N/A"),
                med.get("quantity", 0),
                f"${med.get('unit_price', 0):.2f}"
            ])
        dialog = DetailDialog("Low Stock Medicines", data, headers, self)
        dialog.exec_()

    def show_expiring_details(self):
        headers = ["ID", "Name", "Strength", "Batch No", "Expiry Date", "Qty Left", "Days Left"]
        data = []
        today = datetime.today()
        for med in self.expiring_meds:
            expiry_str = med.get("expiry_date", "")
            days_left = "N/A"
            if expiry_str:
                try:
                    expiry = datetime.strptime(expiry_str, "%Y-%m-%d")
                    days_left = (expiry - today).days
                except ValueError:
                    pass
            data.append([
                med["id"],
                med["name"],
                med.get("strength", "N/A"),
                med.get("batch_no", "N/A"),
                expiry_str,
                med.get("quantity", 0),
                days_left
            ])
        dialog = DetailDialog("Expiring Soon Medicines", data, headers, self)
        dialog.exec_()

    def edit_medicine(self, med):
        dialog = AddMedicineDialog(self, initial_data=med)
        if dialog.exec_():
            new_data = dialog.get_data()
            update_medicine(med["id"], new_data)
            self.load_table_data()

    def delete_medicine(self, med_id):
        reply = QMessageBox.question(
            self,
            "Confirm Delete",
            "Are you sure you want to delete this medicine?",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            delete_medicine(med_id)
            self.load_table_data()