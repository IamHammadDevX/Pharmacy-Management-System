from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel, QSizePolicy
from PyQt5.QtCore import Qt
from widgets.supplier_customer_management import SupplierCustomerManagement
from widgets.invoice_dialog import InvoiceDialog

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
            ("Dashboard", "🏠", False, None),
            ("Purchase", "🛒", True, None),
            ("Sale", "💵", False, None),
            ("Product", "💊", True, None),
            ("Supplier & Customer", "👥", False, "open_supplier_customer_management"),
            ("Medicine", "🧪", True, None),
            ("Invoice", "🧾", False, "open_invoice_dialog"),  # Added handler
            ("Orders", "📦", True, None),
            ("Sales Report", "📈", True, None),
            ("Help & Support", "❓", False, None),
            ("Settings", "⚙️", True, None),
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
            if custom_handler == "open_supplier_customer_management":
                btn.clicked.connect(self.open_supplier_customer_management)
            elif custom_handler == "open_invoice_dialog":
                btn.clicked.connect(self.open_invoice_dialog)

        layout.addStretch()
        self.setLayout(layout)

    def open_supplier_customer_management(self):
        dlg = SupplierCustomerManagement(self)
        dlg.exec_()

    def open_invoice_dialog(self):
        """Open invoice dialog with parent reference"""
        dlg = InvoiceDialog(user=self.user, parent=self.main_window)
        dlg.exec_()