from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QHBoxLayout, QStatusBar, QMessageBox, QHeaderView, QPushButton
from PyQt5.QtCore import Qt
from widgets.paginated_table import PaginatedTable
from db import get_all_medicines, add_medicine, update_medicine, delete_medicine, db_signals
from widgets.add_medicine_dialog import AddMedicineDialog

class ProductManagement(QDialog):
    def __init__(self, user=None, parent=None):
        super().__init__(parent)
        if not user or user.get("role") != "admin":
            QMessageBox.critical(self, "Access Denied", "Only admins can manage products.")
            self.reject()
            return
        self.user = user
        self.setWindowTitle("Product Management")
        self.setMinimumSize(1000, 700)
        self.setStyleSheet("""
            QDialog {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #f5f6fa, stop:1 #ffffff);
                border-radius: 12px;
                box-shadow: 0 6px 15px rgba(0, 0, 0, 0.1);
            }
        """)

        # Main layout
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)

        # Header
        header = QLabel("Product Management")
        header.setStyleSheet("""
            QLabel {
                font-size: 28px;
                font-weight: bold;
                color: #2c3e50;
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #3498db, stop:1 #2980b9);
                padding: 12px;
                border-radius: 10px;
                color: white;
                text-align: center;
            }
        """)
        main_layout.addWidget(header)

        # Paginated Table
        self.table = PaginatedTable(self)
        self.table.setStyleSheet("""
            QTableWidget {
                background: white;
                border: 1px solid #e0e0e0;
                border-radius: 10px;
                box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
            }
            QTableWidget::item {
                padding: 10px;
            }
            QTableWidget::item:selected {
                background: #3498db;
                color: white;
            }
            QHeaderView::section {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #3498db, stop:1 #2980b9);
                color: white;
                font-weight: bold;
                padding: 12px;
                border: none;
            }
            QPushButton {
                border-radius: 6px;
                padding: 6px 12px;
            }
            QPushButton#edit_btn { background: #36b37e; color: white; }
            QPushButton#delete_btn { background: #ff5630; color: white; }
            QPushButton:hover { opacity: 0.9; }
        """)
        self.table.edit_requested.connect(self.edit_product)
        self.table.delete_requested.connect(self.delete_product)
        main_layout.addWidget(self.table)

        # Button layout
        button_layout = QHBoxLayout()
        button_layout.setSpacing(15)

        self.add_btn = QPushButton("➕ Add Product")
        self.add_btn.setCursor(Qt.PointingHandCursor)
        self.add_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #2ecc71, stop:1 #27ae60);
                color: white;
                border-radius: 12px;
                padding: 12px 25px;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #27ae60, stop:1 #2ecc71);
            }
        """)
        self.add_btn.clicked.connect(self.add_product)
        button_layout.addWidget(self.add_btn)

        self.refresh_btn = QPushButton("🔄 Refresh")
        self.refresh_btn.setCursor(Qt.PointingHandCursor)
        self.refresh_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #6c5ce7, stop:1 #5b4de0);
                color: white;
                border-radius: 12px;
                padding: 12px 25px;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #5b4de0, stop:1 #6c5ce7);
            }
        """)
        self.refresh_btn.clicked.connect(self.load_products)
        button_layout.addWidget(self.refresh_btn)

        button_layout.addStretch(1)
        main_layout.addLayout(button_layout)

        # Status bar
        self.status_bar = QStatusBar()
        self.status_bar.setStyleSheet("""
            QStatusBar {
                background: #ecf0f1;
                color: #2c3e50;
                font-size: 13px;
                border-top: 1px solid #ddd;
            }
        """)
        main_layout.addWidget(self.status_bar)

        self.setLayout(main_layout)
        self.load_products()

    def load_products(self):
        """Load all medicines into the paginated table"""
        try:
            medicines = get_all_medicines()
            if not medicines:
                self.status_bar.showMessage("No products found.", 3000)
                self.table.set_data([])
                return
            self.table.set_data(medicines)
            self.status_bar.showMessage(f"Loaded {len(medicines)} products.", 3000)
        except Exception as e:
            self.status_bar.showMessage(f"Error loading products: {str(e)}", 5000)

    def add_product(self):
        """Add a new medicine with validation and signal emission"""
        if not self.user or self.user.get("role") != "admin":
            self.status_bar.showMessage("Access denied: Admin only.", 3000)
            return
        dialog = AddMedicineDialog(self)
        if dialog.exec_() == dialog.Accepted:
            med = dialog.get_data()
            if not med.get("name") or not med.get("name").strip():
                self.status_bar.showMessage("Error: Product name is required.", 3000)
                return
            if med.get("quantity", 0) < 0 or med.get("unit_price", 0.0) < 0:
                self.status_bar.showMessage("Error: Quantity and price must be non-negative.", 3000)
                return
            med["name"] = med["name"].strip().title()
            try:
                add_medicine(med)
                db_signals.medicine_updated.emit()  # Signal update to all views
                self.load_products()
                self.status_bar.showMessage("Product added successfully.", 3000)
            except Exception as e:
                self.status_bar.showMessage(f"Error adding product: {str(e)}", 5000)

    def edit_product(self, med):
        """Edit the selected medicine with validation and signal emission"""
        if not self.user or self.user.get("role") != "admin":
            self.status_bar.showMessage("Access denied: Admin only.", 3000)
            return
        dialog = AddMedicineDialog(self, initial_data=med)
        if dialog.exec_() == dialog.Accepted:
            new_data = dialog.get_data()
            if not new_data.get("name") or not new_data.get("name").strip():
                self.status_bar.showMessage("Error: Product name is required.", 3000)
                return
            if new_data.get("quantity", 0) < 0 or new_data.get("unit_price", 0.0) < 0:
                self.status_bar.showMessage("Error: Quantity and price must be non-negative.", 3000)
                return
            new_data["name"] = new_data["name"].strip().title()
            try:
                update_medicine(med["id"], new_data)
                db_signals.medicine_updated.emit()  # Signal update to all views
                self.load_products()
                self.status_bar.showMessage("Product updated successfully.", 3000)
            except Exception as e:
                self.status_bar.showMessage(f"Error updating product: {str(e)}", 5000)

    def delete_product(self, med_id):
        """Delete the selected medicine with specific confirmation and signal emission"""
        if not self.user or self.user.get("role") != "admin":
            self.status_bar.showMessage("Access denied: Admin only.", 3000)
            return
        # Find the medicine to get its name
        try:
            medicines = get_all_medicines()
            med = next((m for m in medicines if m["id"] == med_id), None)
            if not med:
                self.status_bar.showMessage("Product not found.", 3000)
                return
            med_name = med["name"]
            reply = QMessageBox.question(self, "Confirm Delete", f"Are you sure you want to delete '{med_name}' (ID: {med_id})?",
                                       QMessageBox.Yes | QMessageBox.No)
            if reply == QMessageBox.Yes:
                try:
                    delete_medicine(med_id)
                    db_signals.medicine_updated.emit()  # Signal update to all views
                    self.load_products()
                    self.status_bar.showMessage(f"Product '{med_name}' deleted successfully.", 3000)
                except Exception as e:
                    self.status_bar.showMessage(f"Error deleting product: {str(e)}", 5000)
        except Exception as e:
            self.status_bar.showMessage(f"Error processing delete: {str(e)}", 5000)