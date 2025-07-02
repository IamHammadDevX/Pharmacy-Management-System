from PyQt5.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QLabel, QMessageBox, QLineEdit
from widgets.dashboard_card import DashboardCard
from widgets.paginated_table import PaginatedTable
from db import get_all_medicines, update_medicine, delete_medicine
from widgets.add_medicine_dialog import AddMedicineDialog
from datetime import datetime, timedelta

class Dashboard(QWidget):
    def __init__(self, user=None, parent=None):
        super().__init__(parent)
        self.user = user  # Accept and store user info (for future role-based UI)
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(18)

        # Cards row
        self.cards = []
        cards_layout = QHBoxLayout()
        cards_layout.setSpacing(18)
        self.card_total = DashboardCard("Total Medicines", 0, "In inventory", "#3864fa")
        self.card_sales = DashboardCard("Today's Sales", 0, "Invoices created today", "#36b37e")
        self.card_low_stock = DashboardCard("Low Stock", 0, "Below threshold", "#ffab00")
        self.card_expiry = DashboardCard("Expiring Soon", 0, "Next 30 days", "#ff5630")
        self.cards = [self.card_total, self.card_sales, self.card_low_stock, self.card_expiry]
        cards_layout.addWidget(self.card_total)
        cards_layout.addWidget(self.card_sales)
        cards_layout.addWidget(self.card_low_stock)
        cards_layout.addWidget(self.card_expiry)
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

        # Connect edit/delete signals to their handlers!
        self.table.edit_requested.connect(self.edit_medicine)
        self.table.delete_requested.connect(self.delete_medicine)

        self.load_table_data()

        # Connect search bar
        self.search_input.textChanged.connect(self.filter_table)

    def load_table_data(self):
        medicines = get_all_medicines()
        self.medicines = medicines
        self.table.set_data(medicines)
        self.update_dashboard_cards(medicines)

    def update_dashboard_cards(self, medicines):
        # Total
        self.card_total.set_value(len(medicines))
        # Low stock
        low_stock_count = sum(1 for m in medicines if int(m.get("quantity", 0)) < 10)
        self.card_low_stock.set_value(low_stock_count)
        # Expiring soon
        now = datetime.today()
        soon = now + timedelta(days=30)
        expiring_count = 0
        for m in medicines:
            expiry_str = m.get("expiry_date", "")
            if expiry_str:
                try:
                    expiry = datetime.strptime(expiry_str, "%Y-%m-%d")
                    if now < expiry <= soon:
                        expiring_count += 1
                except Exception:
                    pass
        self.card_expiry.set_value(expiring_count)
        # (Optional) Sales card can be updated if you have invoices module

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