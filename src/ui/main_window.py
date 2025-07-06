from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QPushButton, 
    QMessageBox, QSizePolicy, QFileDialog
)
from PyQt5.QtCore import Qt
from sale_purchase_dialog import SaleDialog, PurchaseDialog
from widgets.sidebar import Sidebar
from widgets.topbar import Topbar
from ui.dashboard import Dashboard
from ui.medicine_management import MedicineManagement
from ui.orders_dialog import OrdersDialog
from ui.sales_report import SalesDialog
from widgets.add_medicine_dialog import AddMedicineDialog

# Import the newly created dialogs
from ui.help_support import HelpSupportDialog # New import
from ui.settings_dialog import SettingsDialog     # New import

from db import add_medicine, db_signals, get_all_medicines, get_inventory_data, get_sales_data, get_all_orders, update_order_status
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
        db_signals.order_updated.connect(self.refresh_all)

        # Central widget setup
        central = QWidget()
        self.main_layout = QHBoxLayout(central)
        self.main_layout.setContentsMargins(0, 0, 0, 0)

        # Sidebar
        self.sidebar = Sidebar(user=self.user, parent=self)
        # No direct signal connections here from sidebar, as sidebar handles its own button clicks
        # and calls methods like open_sales_report directly.

        self.main_layout.addWidget(self.sidebar)

        # Main area
        main_area = QWidget()
        self.area_layout = QVBoxLayout(main_area)
        self.area_layout.setContentsMargins(0, 0, 0, 0)

        # Topbar
        self.topbar = Topbar(user=self.user)
        self.area_layout.addWidget(self.topbar)

        # Buttons Layout (existing buttons)
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
        self.area_layout.addLayout(btn_layout)

        # Dynamic content area
        self.content_area = Dashboard(user=self.user, parent=self)
        self.area_layout.addWidget(self.content_area, 1)

        self.main_layout.addWidget(main_area, 1)
        self.setCentralWidget(central)

        # Connect topbar signals
        self.topbar.add_product_clicked.connect(self.open_add_medicine_dialog)
        self.topbar.logout_clicked.connect(self.handle_logout)

        # Configure role-based access
        self.configure_role_access()

    def set_content(self, widget):
        """Replace the content area with a new widget"""
        if hasattr(self, 'content_area') and self.content_area:
            self.area_layout.replaceWidget(self.content_area, widget)
            self.content_area.deleteLater()
            self.content_area = widget
        else:
            self.area_layout.addWidget(widget)
            self.content_area = widget

    def configure_role_access(self):
        if self.user["role"] == "user":
            self.new_purchase_btn.hide()
            self.export_inventory_btn.hide()
            # The sidebar's configure_role_access should handle its own button visibility.
            # No need to hide sidebar buttons from here if Sidebar class already does it.
            pass

    def open_add_medicine_dialog(self):
        if self.user["role"] != "admin":
            QMessageBox.warning(self, "Permission Denied", "Only admin can add medicines.")
            return
        dialog = AddMedicineDialog(self)
        if dialog.exec_() == dialog.Accepted:
            med = dialog.get_data()
            try:
                add_medicine(med)
                self.refresh_all()
            except Exception as e:
                QMessageBox.critical(self, "Database Error", f"Failed to add medicine:\n{str(e)}")

    def open_sale_dialog(self):
        try:
            dlg = SaleDialog(parent=self)
            if hasattr(dlg, 'user'):
                dlg.user = self.user  # Pass user context if supported
            if dlg.exec_():
                self.refresh_all()
        except Exception as e:
            QMessageBox.critical(self, "Sale Error", f"An error occurred while processing the sale:\n{str(e)}")

    def open_purchase_dialog(self):
        if self.user["role"] != "admin":
            QMessageBox.warning(self, "Permission Denied", "Only admin can record purchases.")
            return
        try:
            dlg = PurchaseDialog(parent=self)
            if hasattr(dlg, 'user'):
                dlg.user = self.user  # Pass user context if supported
            if dlg.exec_():
                self.refresh_all()
        except Exception as e:
            QMessageBox.critical(self, "Purchase Error", f"An error occurred while processing the purchase:\n{str(e)}")

    def export_inventory_csv(self):
        if self.user["role"] != "admin":
            QMessageBox.warning(self, "Permission Denied", "Only admin can export inventory data.")
            return
        from db import get_inventory_data
        try:
            data = get_inventory_data()
            if not data:
                QMessageBox.information(self, "Export Inventory", "No inventory data to export.")
                return
            path, _ = QFileDialog.getSaveFileName(self, "Save Inventory CSV", "inventory.csv", "CSV Files (*.csv)")
            if path:
                with open(path, "w", newline="", encoding="utf-8") as f:
                    writer = csv.writer(f)
                    writer.writerow(data[0].keys())
                    for row in data:
                        writer.writerow(row.values())
                QMessageBox.information(self, "Export Inventory", f"Inventory exported to {path}")
        except Exception as e:
            QMessageBox.critical(self, "Export Error", str(e))

    def export_sales_csv(self):
        # This export is for the general sales history, not the detailed report
        if self.user["role"] != "admin":
            QMessageBox.warning(self, "Permission Denied", "Only admin can export sales data.")
            return
        from db import get_sales_data # This is the general sales history function
        try:
            data = get_sales_data()
            if not data:
                QMessageBox.information(self, "Export Sales", "No sales data to export.")
                return
            path, _ = QFileDialog.getSaveFileName(self, "Save Sales CSV", "sales.csv", "CSV Files (*.csv)")
            if path:
                with open(path, "w", newline="", encoding="utf-8") as f:
                    writer = csv.writer(f)
                    writer.writerow(data[0].keys())
                    for row in data:
                        writer.writerow(row.values())
                QMessageBox.information(self, "Export Sales", f"Sales exported to {path}")
        except Exception as e:
            QMessageBox.critical(self, "Export Error", str(e))

    def handle_logout(self):
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
        event.accept()

    def refresh_all(self):
        """Refresh all data views in the application"""
        if hasattr(self, 'content_area') and hasattr(self.content_area, 'load_table_data'):
            self.content_area.load_table_data()
        if hasattr(self, 'content_area') and hasattr(self.content_area, 'load_dashboard_data'):
            self.content_area.load_dashboard_data()
        # Refresh MedicineManagement if open
        if isinstance(self.content_area, MedicineManagement):
            self.content_area.load_medicines()
        # Refresh OrdersDialog if open
        if isinstance(self.content_area, OrdersDialog):
            self.content_area.load_orders()
        # Refresh SalesDialog if open
        if isinstance(self.content_area, SalesDialog):
            self.content_area.load_sales_data()


    def refresh_medicine_data(self):
        """Refresh all medicine-related UI components"""
        if hasattr(self, 'content_area') and hasattr(self.content_area, 'load_table_data'):
            self.content_area.load_table_data()
        medicines = get_all_medicines()
        # Example for a QComboBox (if used in content_area)
        if hasattr(self.content_area, 'medicine_combo'):
            self.content_area.medicine_combo.clear()
            for med in medicines:
                self.content_area.medicine_combo.addItem(
                    f"{med['name']} ({med['strength']}) - Stock: {med['quantity']}",
                    med['id']
                )
        # Refresh MedicineManagement if open
        if isinstance(self.content_area, MedicineManagement):
            self.content_area.load_medicines()
        # Refresh any other medicine lists or tables if implemented
        if hasattr(self.content_area) and hasattr(self.content_area, 'update_medicine_table'):
            self.content_area.update_medicine_table()

    def open_medicine_management(self):
        """Open Medicine Inventory Management dialog"""
        if self.user["role"] != "admin":
            QMessageBox.warning(self, "Permission Denied", "Only admin can manage medicine inventory.")
            return
        dialog = MedicineManagement(self.user, self)
        dialog.exec_()
        
    def open_orders_dialog(self):
        """Open Orders Management dialog"""
        if self.user["role"] != "admin":
            QMessageBox.warning(self, "Permission Denied", "Only admin can manage orders.")
            return
        dialog = OrdersDialog(self.user, self)
        dialog.exec_()

    def open_sales_report(self):
        """Open Sales Report dialog."""
        if self.user["role"] != "admin":
            QMessageBox.warning(self, "Permission Denied", "Only admin can view sales reports.")
            return
        dialog = SalesDialog(user=self.user, parent=self)
        dialog.exec_()
    
    # New methods for Help & Support and Settings
    def open_help_support(self):
        """Open Help & Support dialog."""
        # No role check needed for help
        dialog = HelpSupportDialog(user=self.user, parent=self)
        dialog.exec_()

    def open_settings_dialog(self):
        """Open Settings dialog."""
        # No role check needed here, as the dialog itself will handle user context
        dialog = SettingsDialog(user=self.user, parent=self)
        dialog.exec_()