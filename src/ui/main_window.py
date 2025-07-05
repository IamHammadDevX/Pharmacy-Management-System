from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QPushButton, 
    QMessageBox, QSizePolicy, QFileDialog
)
from PyQt5.QtCore import Qt
from sale_purchase_dialog import SaleDialog, PurchaseDialog
from widgets.sidebar import Sidebar
from widgets.topbar import Topbar
from ui.dashboard import Dashboard
from widgets.add_medicine_dialog import AddMedicineDialog
from db import add_medicine, db_signals
import csv

class MainWindow(QMainWindow):
    def __init__(self, user):
        super().__init__()
        self.user = user
        self.setWindowTitle("Pharmacy Management App")
        self.setGeometry(100, 100, 1200, 700)

        # Connect DB signals
        db_signals.sale_recorded.connect(self.refresh_all)
        db_signals.medicine_updated.connect(self.refresh_all)

        # Central widget setup
        central = QWidget()
        main_layout = QHBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)

        self.sidebar = Sidebar(user=self.user)
        main_layout.addWidget(self.sidebar)

        main_area = QWidget()
        area_layout = QVBoxLayout(main_area)
        area_layout.setContentsMargins(0, 0, 0, 0)

        self.topbar = Topbar(user=self.user)
        area_layout.addWidget(self.topbar)

        # --- Buttons Layout ---
        btn_layout = QHBoxLayout()
        btn_layout.setContentsMargins(12, 6, 12, 6)
        btn_layout.addStretch(1)

        self.new_sale_btn = QPushButton("➕ New Sale")
        self.new_sale_btn.setCursor(Qt.PointingHandCursor)
        self.new_sale_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #43cea2, stop:1 #185a9d);
                color: white;
                border-radius: 12px;
                padding: 8px 22px;
                font-size: 15px;
                font-weight: bold;
                margin-right: 10px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #185a9d, stop:1 #43cea2);
            }
        """)
        self.new_sale_btn.clicked.connect(self.open_sale_dialog)
        self.new_sale_btn.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Preferred)
        btn_layout.addWidget(self.new_sale_btn)

        self.new_purchase_btn = QPushButton("📦 New Purchase")
        self.new_purchase_btn.setCursor(Qt.PointingHandCursor)
        self.new_purchase_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #ff9966, stop:1 #ff5e62);
                color: white;
                border-radius: 12px;
                padding: 8px 22px;
                font-size: 15px;
                font-weight: bold;
                margin-left: 10px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #ff5e62, stop:1 #ff9966);
            }
        """)
        self.new_purchase_btn.clicked.connect(self.open_purchase_dialog)
        self.new_purchase_btn.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Preferred)
        btn_layout.addWidget(self.new_purchase_btn)

        self.export_inventory_btn = QPushButton("⬇️ Export Inventory (CSV)")
        self.export_inventory_btn.setCursor(Qt.PointingHandCursor)
        self.export_inventory_btn.setStyleSheet("""
            QPushButton {
                background: #00b894;
                color: white;
                border-radius: 12px;
                padding: 8px 18px;
                font-size: 14px;
                font-weight: bold;
                margin-left: 16px;
            }
            QPushButton:hover {
                background: #00cec9;
            }
        """)
        self.export_inventory_btn.clicked.connect(self.export_inventory_csv)
        btn_layout.addWidget(self.export_inventory_btn)

        self.export_sales_btn = QPushButton("⬇️ Export Sales (CSV)")
        self.export_sales_btn.setCursor(Qt.PointingHandCursor)
        self.export_sales_btn.setStyleSheet("""
            QPushButton {
                background: #0984e3;
                color: white;
                border-radius: 12px;
                padding: 8px 18px;
                font-size: 14px;
                font-weight: bold;
                margin-left: 8px;
            }
            QPushButton:hover {
                background: #74b9ff;
            }
        """)
        self.export_sales_btn.clicked.connect(self.export_sales_csv)
        btn_layout.addWidget(self.export_sales_btn)

        btn_layout.addStretch(1)
        area_layout.addLayout(btn_layout)

        self.dashboard = Dashboard(user=self.user)
        area_layout.addWidget(self.dashboard, 1)

        main_layout.addWidget(main_area, 1)
        self.setCentralWidget(central)

        self.topbar.add_product_clicked.connect(self.open_add_medicine_dialog)
        self.topbar.logout_clicked.connect(self.handle_logout)

        self.configure_role_access()

    def configure_role_access(self):
        if self.user["role"] == "user":
            self.new_purchase_btn.hide()
            self.export_inventory_btn.hide()

    def open_add_medicine_dialog(self):
        if self.user["role"] != "admin":
            QMessageBox.warning(self, "Permission Denied", "Only admin can add medicines.")
            return
        dialog = AddMedicineDialog(self)
        if dialog.exec_() == dialog.Accepted:
            med = dialog.get_data()
            try:
                add_medicine(med)
            except Exception as e:
                QMessageBox.critical(self, "Database Error", f"Failed to add medicine:\n{str(e)}")
                return
            self.dashboard.load_table_data()

    def open_sale_dialog(self):
        try:
            dlg = SaleDialog(self)
            if dlg.exec_():
                self.dashboard.load_table_data()
        except Exception as e:
            QMessageBox.critical(self, "Sale Error", f"An error occurred while processing the sale:\n{str(e)}")

    def open_purchase_dialog(self):
        if self.user["role"] != "admin":
            QMessageBox.warning(self, "Permission Denied", "Only admin can record purchases.")
            return
        try:
            dlg = PurchaseDialog(self)
            if dlg.exec_():
                self.dashboard.load_table_data()
        except Exception as e:
            QMessageBox.critical(self, "Purchase Error", f"An error occurred while processing the purchase:\n{str(e)}")

    def export_inventory_csv(self):
        if self.user["role"] != "admin":
            QMessageBox.warning(self, "Permission Denied", "Only admin can export inventory data.")
            return
        from db import get_inventory_data
        data = get_inventory_data()
        if not data:
            QMessageBox.information(self, "Export Inventory", "No inventory data to export.")
            return
        path, _ = QFileDialog.getSaveFileName(self, "Save Inventory CSV", "inventory.csv", "CSV Files (*.csv)")
        if not path:
            return
        try:
            with open(path, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(data[0].keys())
                for row in data:
                    writer.writerow(row.values())
            QMessageBox.information(self, "Export Inventory", f"Inventory exported to {path}")
        except Exception as e:
            QMessageBox.critical(self, "Export Error", str(e))

    def export_sales_csv(self):
        from db import get_sales_data
        data = get_sales_data()
        if not data:
            QMessageBox.information(self, "Export Sales", "No sales data to export.")
            return
        path, _ = QFileDialog.getSaveFileName(self, "Save Sales CSV", "sales.csv", "CSV Files (*.csv)")
        if not path:
            return
        try:
            with open(path, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(data[0].keys())
                for row in data:
                    writer.writerow(row.values())
            QMessageBox.information(self, "Export Sales", f"Sales exported to {path}")
        except Exception as e:
            QMessageBox.critical(self, "Export Error", str(e))

    def handle_logout(self):
        # Only show login dialog if user chose "Switch Account"/logout,
        # but if closed via X, just exit (no re-login dialog).
        self.hide()
        from widgets.login_dialog import LoginDialog
        login = LoginDialog()
        if login.exec_() == login.Accepted:
            user = login.result
            from ui.main_window import MainWindow
            self.new_window = MainWindow(user)
            self.new_window.show()
        self.close()

    def closeEvent(self, event):
        # Just accept, no login dialog on app exit via X
        event.accept()
    def refresh_all(self):
        """Refresh all data views in the application"""
        self.dashboard.load_table_data()
    # Add this method to your main window class
    def refresh_medicine_data(self):
        """Refresh all medicine-related UI components"""
        # Example for a QComboBox
        self.ui.medicine_combo.clear()
        medicines = db.get_all_medicines()  # This now only returns in-stock meds
        for med in medicines:
            self.ui.medicine_combo.addItem(
                f"{med['name']} ({med['strength']}) - Stock: {med['quantity']}",
                med['id']
            )
        
        # Refresh any other medicine lists or tables
        if hasattr(self, 'medicine_table'):
            self.update_medicine_table()