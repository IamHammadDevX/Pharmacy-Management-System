from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel, QSizePolicy, QDialog
from PyQt5.QtCore import Qt
from sale_purchase_dialog import PurchaseDialog, SaleDialog
from widgets.supplier_customer_management import SupplierCustomerManagement
from widgets.invoice_dialog import InvoiceDialog
from ui.dashboard import Dashboard
from ui.product_management import ProductManagement
from ui.medicine_management import MedicineManagement
from ui.orders_dialog import OrdersDialog
from ui.sales_report import SalesDialog
from ui.help_support import HelpSupportDialog
from ui.settings_dialog import SettingsDialog

class Sidebar(QWidget):
    def __init__(self, user=None, parent=None):
        super().__init__(parent)
        self.user = user
        self.main_window = parent  # Store reference to main window
        self.setFixedWidth(200)
        self.setObjectName("Sidebar")

        layout = QVBoxLayout()
        layout.setContentsMargins(10, 20, 10, 10)
        layout.setSpacing(15)

        app_label = QLabel("Phermo")
        app_label.setStyleSheet("font-weight: bold; font-size: 22px; margin-bottom: 40px;")
        layout.addWidget(app_label)

        # (text, icon, admin_only, custom_handler)
        buttons = [
            ("Dashboard", "🏠", False, "open_dashboard"),
            ("Purchase", "🛒", True, "open_purchase_dialog"),
            ("Sale", "💵", False, "open_sale_dialog"),
            ("Product", "💊", True, "open_product_management"),
            ("Supplier & Customer", "👥", False, "open_supplier_customer_management"),
            ("Medicine", "🧪", True, "open_medicine_management"),
            ("Invoice", "🧾", False, "open_invoice_dialog"),
            ("Orders", "📦", True, "open_orders_dialog"),
            ("Sales Report", "📈", True, "open_sales_report"),
            ("Help & Support", "❓", False, "open_help_support"),
            ("Settings", "⚙️", True, "open_settings_dialog"),
        ]

        self.sidebar_buttons = {}
        for text, icon, admin_only, custom_handler in buttons:
            if admin_only and self.user and self.user.get('role') == 'user':
                continue
                
            btn = QPushButton(f"{icon}  {text}")
            btn.setStyleSheet("""
                QPushButton {
                    text-align: left;
                    padding: 8px 12px;
                    border-radius: 8px;
                    font-size: 15px;
                }
                QPushButton:hover {
                    background: #e3eafc;
                }
            """)
            btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
            btn.setCursor(Qt.PointingHandCursor)
            layout.addWidget(btn)
            self.sidebar_buttons[text] = btn

            # Connect custom handlers
            if custom_handler == "open_dashboard":
                btn.clicked.connect(self.open_dashboard)
            elif custom_handler == "open_purchase_dialog":
                btn.clicked.connect(self.open_purchase_dialog)
            elif custom_handler == "open_sale_dialog":
                btn.clicked.connect(self.open_sale_dialog)
            elif custom_handler == "open_product_management":
                btn.clicked.connect(self.open_product_management)
            elif custom_handler == "open_supplier_customer_management":
                btn.clicked.connect(self.open_supplier_customer_management)
            elif custom_handler == "open_medicine_management":
                btn.clicked.connect(self.open_medicine_management)
            elif custom_handler == "open_invoice_dialog":
                btn.clicked.connect(self.open_invoice_dialog)
            elif custom_handler == "open_orders_dialog":
                btn.clicked.connect(self.open_orders_dialog)
            elif custom_handler == "open_sales_report":
                btn.clicked.connect(self.open_sales_report)
            elif custom_handler == "open_help_support":
                btn.clicked.connect(self.open_help_support)
            elif custom_handler == "open_settings_dialog":
                btn.clicked.connect(self.open_settings_dialog)

        layout.addStretch()
        self.setLayout(layout)

    def open_dashboard(self):
        """Switch to Dashboard content in MainWindow"""
        if self.main_window:
            self.main_window.set_content(Dashboard(self.user, self.main_window))

    def open_purchase_dialog(self):
        dlg = PurchaseDialog(parent=self.main_window)
        dlg.exec_()

    def open_sale_dialog(self):
        dlg = SaleDialog(parent=self.main_window)
        dlg.exec_()

    def open_product_management(self):
        dlg = ProductManagement(self.user, parent=self.main_window)
        dlg.exec_()

    def open_supplier_customer_management(self):
        dlg = SupplierCustomerManagement(parent=self.main_window)
        dlg.exec_()

    def open_medicine_management(self):
        dlg = MedicineManagement(self.user, parent=self.main_window)
        dlg.exec_()

    def open_invoice_dialog(self):
        dlg = InvoiceDialog(self.user, parent=self.main_window)
        dlg.exec_()

    def open_orders_dialog(self):
        dlg = OrdersDialog(self.user, parent=self.main_window)
        dlg.exec_()

    def open_sales_report(self):
        dlg = SalesDialog(self.user, parent=self.main_window)
        dlg.exec_()

    def open_help_support(self):
        dlg = HelpSupportDialog(self.user, parent=self.main_window)
        dlg.exec_()

    def open_settings_dialog(self):
        dlg = SettingsDialog(self.user, parent=self.main_window)
        dlg.exec_()