import datetime
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QTextDocument
from PyQt5.QtPrintSupport import QPrinter, QPrintDialog
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QPushButton, QLabel, QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox, QMessageBox,
    QHeaderView, QFormLayout, QFrame, QSizePolicy, QAbstractItemView, QSpacerItem,
    QApplication, QDialogButtonBox
)
from db import get_all_medicines, record_sale_with_stock_update, get_customers, add_customer, db_signals

def is_expired(expiry_date_str):
    """Check if expiry_date_str (format YYYY-MM-DD) is before today."""
    try:
        return datetime.datetime.strptime(expiry_date_str, "%Y-%m-%d").date() < datetime.date.today()
    except Exception:
        return False

def generate_receipt_html(pharmacy_details, invoice_details, invoice_items, totals):
    """
    Generate a short, modern, centralized HTML receipt for thermal/roll printing.
    Uses Pakistani Rupee symbol (₨) for currency.
    """
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            body {{
                font-family: Arial, monospace, 'Courier New';
                font-size: 11pt;
                width: 2.6in;
                margin: 0 auto;
                color: #111;
                background: #fff;
            }}
            .centered {{ text-align: center; }}
            .bold {{ font-weight: bold; }}
            .header {{
                margin-bottom: 6px;
            }}
            .header h2 {{
                margin: 0 0 2px 0;
                font-size: 15pt;
                font-weight: bold;
                letter-spacing: 1px;
            }}
            .header p {{
                margin: 0;
                font-size: 9pt;
            }}
            hr {{
                border: none;
                border-top: 1px dashed #bbb;
                margin: 8px 0;
            }}
            .meta {{
                font-size: 8.5pt;
                margin-bottom: 2px;
            }}
            .meta td {{ padding: 2px 0; }}
            table.items {{
                width: 100%;
                font-size: 9pt;
                border-collapse: collapse;
                margin-bottom: 2px;
            }}
            table.items th, table.items td {{
                padding: 2px 2px;
            }}
            table.items th {{
                border-bottom: 1px solid #bbb;
                font-weight: bold;
            }}
            .right {{ text-align: right; }}
            .totals {{
                font-size: 10pt;
                margin-top: 4px;
            }}
            .totals td {{
                padding: 2px 0;
            }}
            .grandtotal td {{
                font-weight: bold;
                font-size: 11pt;
            }}
            .footer {{
                margin-top: 8px;
                font-size: 8.5pt;
                text-align: center;
                color: #999;
            }}
        </style>
    </head>
    <body>
        <div class="header centered">
            <h2>{pharmacy_details['name']}</h2>
            <p>{pharmacy_details['address']}</p>
            <p>Tel: {pharmacy_details['phone']}</p>
        </div>
        <hr>
        <table class="meta" width="100%">
            <tr><td>Invoice #:</td><td class="right">{invoice_details['invoice_number']}</td></tr>
            <tr><td>Date:</td><td class="right">{invoice_details['date']}</td></tr>
            <tr><td>Cashier:</td><td class="right">{invoice_details['cashier']}</td></tr>
            <tr><td>Customer:</td><td class="right">{invoice_details['customer']}</td></tr>
        </table>
        <hr>
        <table class="items">
            <thead>
                <tr>
                    <th>Item</th>
                    <th class="right">Qty</th>
                    <th class="right">Rate</th>
                    <th class="right">Disc</th>
                    <th class="right">Amt</th>
                </tr>
            </thead>
            <tbody>
                {''.join([
                    f"<tr><td>{item['name']}</td><td class='right'>{item['qty']}</td><td class='right'>₨ {item['unit_price']:.2f}</td><td class='right'>{item['discount']:.2f}%</td><td class='right'>₨ {item['total']:.2f}</td></tr>"
                    for item in invoice_items
                ])}
            </tbody>
        </table>
        <hr>
        <table class="totals" width="100%">
            <tr class="grandtotal"><td>Total</td><td class="right">₨ {totals['total']:.2f}</td></tr>
        </table>
        <hr>
        <div class="footer">
            Thank you for shopping!<br>
            <span style="font-size:7.5pt;">No returns without receipt.</span>
        </div>
    </body>
    </html>
    """
    return html

class MedicineSearchDialog(QDialog):
    """Dedicated dialog for searching and selecting medicines."""
    medicine_selected = pyqtSignal(dict)  # Signal emitted when a medicine is selected
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Search Medicines")
        self.setMinimumSize(800, 500)
        
        self.setStyleSheet("""
            QDialog { background-color: #f5f7fa; }
            QLineEdit {
                padding: 8px;
                border: 1px solid #d1d9e6;
                border-radius: 4px;
                font-size: 14px;
            }
            QTableWidget {
                background-color: white;
                border: 1px solid #e0e3eb;
                selection-background-color: #e3f2fd;
                font-size: 13px;
            }
            QHeaderView::section {
                background-color: #f8f9fa;
                padding: 8px;
                border: none;
                font-weight: bold;
            }
            QPushButton {
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: 500;
                border: none;
            }
            QPushButton#select_btn {
                background-color: #4caf50;
                color: white;
            }
            QPushButton#select_btn:hover {
                background-color: #3d8b40;
            }
            QPushButton#cancel_btn {
                background-color: #f44336;
                color: white;
            }
            QPushButton#cancel_btn:hover {
                background-color: #d32f2f;
            }
        """)
        
        layout = QVBoxLayout(self)
        
        # Search bar
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search by name, strength, batch, manufacturer...")
        self.search_input.textChanged.connect(self.filter_medicines)
        layout.addWidget(self.search_input)
        
        # Medicine table
        self.medicine_table = QTableWidget()
        self.medicine_table.setColumnCount(8)
        self.medicine_table.setHorizontalHeaderLabels([
            "Name", "Generic", "Strength", "Batch", "Manufacturer", "Expiry", "Stock", "Price"
        ])
        self.medicine_table.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive)
        self.medicine_table.verticalHeader().setVisible(False)
        self.medicine_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.medicine_table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.medicine_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.medicine_table.doubleClicked.connect(self.select_medicine)
        layout.addWidget(self.medicine_table)
        
        # Button box
        button_box = QDialogButtonBox()
        self.select_button = QPushButton("Select")
        self.select_button.setObjectName("select_btn")
        self.select_button.clicked.connect(self.select_medicine)
        button_box.addButton(self.select_button, QDialogButtonBox.AcceptRole)
        
        cancel_button = QPushButton("Cancel")
        cancel_button.setObjectName("cancel_btn")
        cancel_button.clicked.connect(self.reject)
        button_box.addButton(cancel_button, QDialogButtonBox.RejectRole)
        layout.addWidget(button_box)
        
        self.load_medicines()
        
    def load_medicines(self):
        """Load all medicines from database."""
        try:
            self.medicines = get_all_medicines()
            self.filter_medicines()  # Populate table with all medicines initially
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load medicines: {str(e)}")
    
    def filter_medicines(self):
        """Filter medicines based on search text."""
        search_text = self.search_input.text().lower()
        
        if not self.medicines:
            return
            
        filtered = [
            med for med in self.medicines 
            if (search_text in med.get('name', '').lower() or 
                search_text in med.get('generic_name', '').lower() or
                search_text in med.get('strength', '').lower() or
                search_text in med.get('batch_no', '').lower() or
                search_text in med.get('manufacturer', '').lower())
        ]
        
        self.medicine_table.setRowCount(len(filtered))
        
        for row, med in enumerate(filtered):
            # Set visual appearance based on stock/expiry
            expired = is_expired(med.get('expiry_date', ''))
            out_of_stock = med.get('quantity', 0) <= 0
            
            # Name
            name_item = QTableWidgetItem(med.get('name', 'N/A'))
            if expired or out_of_stock:
                name_item.setForeground(Qt.red)
            self.medicine_table.setItem(row, 0, name_item)
            
            # Generic
            self.medicine_table.setItem(row, 1, QTableWidgetItem(med.get('generic_name', '-')))
            
            # Strength
            self.medicine_table.setItem(row, 2, QTableWidgetItem(med.get('strength', '-')))
            
            # Batch
            self.medicine_table.setItem(row, 3, QTableWidgetItem(med.get('batch_no', '-')))
            
            # Manufacturer
            self.medicine_table.setItem(row, 4, QTableWidgetItem(med.get('manufacturer', '-')))
            
            # Expiry
            expiry_item = QTableWidgetItem(self._format_date(med.get('expiry_date', '')))
            if expired:
                expiry_item.setForeground(Qt.red)
                expiry_item.setToolTip("Expired - cannot be sold")
            self.medicine_table.setItem(row, 5, expiry_item)
            
            # Stock
            stock_item = QTableWidgetItem(str(med.get('quantity', 0)))
            if out_of_stock:
                stock_item.setForeground(Qt.red)
                stock_item.setToolTip("Out of stock")
            self.medicine_table.setItem(row, 6, stock_item)
            
            # Price
            self.medicine_table.setItem(row, 7, QTableWidgetItem(f"₨ {med.get('unit_price', 0):.2f}"))
        
        # Resize columns to fit content
        self.medicine_table.resizeColumnsToContents()
        
    def _format_date(self, date_str):
        """Format date for display."""
        if not date_str:
            return "-"
        try:
            date = datetime.datetime.strptime(date_str, "%Y-%m-%d").date()
            return date.strftime("%d-%b-%Y")
        except ValueError:
            return date_str
            
    def select_medicine(self):
        """Handle medicine selection."""
        selected_row = self.medicine_table.currentRow()
        if selected_row >= 0:
            search_text = self.search_input.text().lower()
            filtered = [
                med for med in self.medicines 
                if (search_text in med.get('name', '').lower() or 
                    search_text in med.get('generic_name', '').lower() or
                    search_text in med.get('strength', '').lower() or
                    search_text in med.get('batch_no', '').lower() or
                    search_text in med.get('manufacturer', '').lower())
            ]
            if selected_row < len(filtered):
                self.medicine_selected.emit(filtered[selected_row])
                self.accept()

class InvoiceDialog(QDialog):
    def __init__(self, user, parent=None):
        super().__init__(parent)
        self.user = user
        self.parent_window = parent
        self.setWindowTitle("Create Invoice")
        self.setMinimumSize(1300, 650)  # Increased width for better layout

        self.setStyleSheet("""
            QDialog { background-color: #f0f2f5; }
            QFrame#left_sidebar {
                background-color: #ffffff;
                border-radius: 8px;
                border: 1px solid #e0e0e0;
            }
            QFrame#card {
                background-color: #f8f9fa;
                border-radius: 8px;
                border: 1px solid #e9ecef;
                padding: 15px;
            }
            QFrame#table_container {
                background-color: #ffffff;
                border: 1px solid #e0e0e0;
                border-radius: 8px;
                padding: 10px;
                margin-bottom: 15px;
            }
            QLabel { font-size: 14px; color: #34495e; }
            QLabel#header_label {
                font-size: 26px; font-weight: bold; color: #2c3e50; padding-bottom: 10px;
            }
            QFormLayout QLabel { font-size: 13px; font-weight: 500; color: #2c3e50; }
            QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox {
                border: 1.5px solid #b4c3d3; border-radius: 5px; padding: 8px; font-size: 13px; background-color: #f7fbff;
            }
            QComboBox::drop-down { border: none; }
            QPushButton {
                border-radius: 6px; padding: 10px 15px; font-weight: bold; border: none; color: white; font-size: 14px; transition: background 0.3s ease;
            }
            QPushButton#add_item_btn { background-color: #007bff; }
            QPushButton#add_item_btn:hover { background-color: #0056b3; }
            QPushButton#remove_item_btn { background-color: #dc3545; }
            QPushButton#remove_item_btn:hover { background-color: #c82333; }
            QPushButton#print_invoice_btn {
                background-color: #28a745; padding: 12px 25px; font-size: 15px;
            }
            QPushButton#print_invoice_btn:hover { background-color: #218838; }
            QPushButton#search_btn {
                background-color: #6c757d;
                padding: 8px 15px;
                font-size: 13px;
            }
            QPushButton#search_btn:hover {
                background-color: #5a6268;
            }
            QTableWidget {
                background-color: white;
                border: none;
                selection-background-color: #e0eafc;
                gridline-color: #f0f0f0;
                font-size: 13px;
                alternate-background-color: #f8f9fa;  # Zebra striping
            }
            QTableWidget::item {
                padding: 4px;
            }
            QHeaderView::section {
                background-color: #f8f9fa;
                color: #34495e;
                padding: 8px;
                border: 1px solid #e0e0e0;
                font-weight: bold;
                font-size: 13px;
            }
            QFrame#totals_frame {
                background-color: #e6f7ff;
                border: 1px solid #cceeff;
                border-radius: 8px;
            }
            QLabel#total_label { font-size: 20px; font-weight: bold; color: #28a745; }
        """)

        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(15)

        # Left sidebar
        left_sidebar = QFrame()
        left_sidebar.setObjectName("left_sidebar")
        sidebar_layout = QVBoxLayout(left_sidebar)
        sidebar_layout.setContentsMargins(15, 15, 15, 15)
        sidebar_layout.setSpacing(15)

        # Add item card
        add_item_card = QFrame()
        add_item_card.setObjectName("card")
        add_item_layout = QVBoxLayout(add_item_card)
        add_item_layout.setSpacing(10)
        add_item_layout.addWidget(QLabel("<b>Add Medicine to Invoice</b>"))

        # Search button row
        search_btn_row = QHBoxLayout()
        self.search_btn = QPushButton("🔍 Search Medicines...")
        self.search_btn.setObjectName("search_btn")
        self.search_btn.setCursor(Qt.PointingHandCursor)
        self.search_btn.clicked.connect(self.show_search_dialog)
        search_btn_row.addWidget(self.search_btn)
        add_item_layout.addLayout(search_btn_row)

        # Selected medicine info
        self.selected_med_frame = QFrame()
        self.selected_med_frame.setVisible(False)
        selected_med_layout = QVBoxLayout(self.selected_med_frame)
        selected_med_layout.setContentsMargins(0, 10, 0, 0)
        
        self.med_name_label = QLabel()
        self.med_name_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        selected_med_layout.addWidget(self.med_name_label)
        
        med_details_layout = QHBoxLayout()
        self.med_batch_label = QLabel()
        self.med_batch_label.setStyleSheet("color: #555; font-size: 12px;")
        med_details_layout.addWidget(self.med_batch_label)
        
        self.med_expiry_label = QLabel()
        self.med_expiry_label.setStyleSheet("color: #555; font-size: 12px;")
        med_details_layout.addWidget(self.med_expiry_label)
        
        self.med_stock_label = QLabel()
        self.med_stock_label.setStyleSheet("color: #555; font-size: 12px;")
        med_details_layout.addWidget(self.med_stock_label)
        med_details_layout.addStretch()
        selected_med_layout.addLayout(med_details_layout)
        
        add_item_layout.addWidget(self.selected_med_frame)

        # Quantity & Discount layout
        qty_disc_widget = QFrame()
        qty_disc_layout = QHBoxLayout(qty_disc_widget)
        qty_disc_layout.setSpacing(18)
        qty_disc_layout.setContentsMargins(0, 6, 0, 6)

        qty_vbox = QVBoxLayout()
        qty_label = QLabel("Quantity")
        qty_label.setStyleSheet("font-weight: bold; font-size: 13px; padding-bottom: 2px; color: #223b61;")
        self.quantity_spin = QSpinBox()
        self.quantity_spin.setMinimum(1)
        self.quantity_spin.setMaximum(9999)
        self.quantity_spin.setFixedWidth(90)
        qty_vbox.addWidget(qty_label)
        qty_vbox.addWidget(self.quantity_spin)
        qty_disc_layout.addLayout(qty_vbox)

        disc_vbox = QVBoxLayout()
        disc_label = QLabel("Discount")
        disc_label.setStyleSheet("font-weight: bold; font-size: 13px; padding-bottom: 2px; color: #223b61;")
        self.discount_spin = QDoubleSpinBox()
        self.discount_spin.setMinimum(0)
        self.discount_spin.setMaximum(100)
        self.discount_spin.setSuffix('%')
        self.discount_spin.setFixedWidth(90)
        self.discount_spin.setValue(0.0)
        disc_vbox.addWidget(disc_label)
        disc_vbox.addWidget(self.discount_spin)
        qty_disc_layout.addLayout(disc_vbox)

        add_item_layout.addWidget(qty_disc_widget)

        btn_add = QPushButton("➕ Add Item")
        btn_add.setObjectName("add_item_btn")
        btn_add.setCursor(Qt.PointingHandCursor)
        btn_add.clicked.connect(self.add_item)
        add_item_layout.addWidget(btn_add)
        sidebar_layout.addWidget(add_item_card)

        # Customer card
        customer_card = QFrame()
        customer_card.setObjectName("card")
        customer_layout = QFormLayout(customer_card)
        customer_layout.setSpacing(12)
        customer_layout.addRow(QLabel("<b>Customer Info</b>"))
        self.cust_type_combo = QComboBox()
        self.cust_type_combo.addItems(["Walk-in Customer", "Existing Customer", "New Customer"])
        self.cust_type_combo.currentIndexChanged.connect(self.toggle_customer_fields)
        customer_layout.addRow("Type:", self.cust_type_combo)
        self.cust_combo = QComboBox()
        customer_layout.addRow("Select:", self.cust_combo)
        self.new_cust_name = QLineEdit()
        self.new_cust_name.setPlaceholderText("Full Name")
        customer_layout.addRow("Name:", self.new_cust_name)
        self.new_cust_contact = QLineEdit()
        self.new_cust_contact.setPlaceholderText("Phone/Email")
        customer_layout.addRow("Contact:", self.new_cust_contact)
        sidebar_layout.addWidget(customer_card)
        sidebar_layout.addStretch()

        main_layout.addWidget(left_sidebar, stretch=1)

        # Right panel
        right_panel = QFrame()
        right_panel_layout = QVBoxLayout(right_panel)
        right_panel_layout.setContentsMargins(0, 0, 0, 0)
        right_panel_layout.setSpacing(15)

        header_label = QLabel("Create Invoice")
        header_label.setObjectName("header_label")
        right_panel_layout.addWidget(header_label)

        self.table = QTableWidget(0, 6)
        self.table.setHorizontalHeaderLabels(["Medicine", "Strength", "Qty", "Unit Price", "Discount", "Total"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        right_panel_layout.addWidget(self.table)

        remove_btn_layout = QHBoxLayout()
        remove_btn_layout.addStretch()
        btn_remove = QPushButton("🗑️ Remove")
        btn_remove.setObjectName("remove_item_btn")
        btn_remove.setCursor(Qt.PointingHandCursor)
        btn_remove.clicked.connect(self.remove_item)
        remove_btn_layout.addWidget(btn_remove)
        right_panel_layout.addLayout(remove_btn_layout)

        bottom_layout = QHBoxLayout()
        totals_frame = QFrame()
        totals_frame.setObjectName("totals_frame")
        totals_layout = QFormLayout(totals_frame)
        totals_layout.setSpacing(10)
        self.total_label = QLabel("Total: <b>₨ 0.00</b>")
        self.total_label.setObjectName("total_label")
        totals_layout.addRow(self.total_label)
        bottom_layout.addWidget(totals_frame)
        bottom_layout.addStretch()
        print_btn_layout = QVBoxLayout()
        print_btn_layout.addStretch()
        btn_print = QPushButton("🖨️ Complete & Print")
        btn_print.setObjectName("print_invoice_btn")
        btn_print.setCursor(Qt.PointingHandCursor)
        btn_print.clicked.connect(self.print_and_record_invoice)
        print_btn_layout.addWidget(btn_print)
        print_btn_layout.addStretch()
        bottom_layout.addLayout(print_btn_layout)
        right_panel_layout.addLayout(bottom_layout)

        main_layout.addWidget(right_panel, stretch=1)

        self.setLayout(main_layout)
        self.invoice_items = []
        self.selected_medicine = None
        self.load_customers()
        self.toggle_customer_fields()
        self.update_totals()

        # db_signals.medicine_updated.connect(self.load_medicines)
        # db_signals.sale_recorded.connect(self.load_medicines)

    def show_search_dialog(self):
        """Show the medicine search dialog."""
        dialog = MedicineSearchDialog(self)
        dialog.medicine_selected.connect(self.set_selected_medicine)
        dialog.exec_()

    def set_selected_medicine(self, medicine):
        """Set the selected medicine from search dialog."""
        self.selected_medicine = medicine
        self.selected_med_frame.setVisible(True)
        
        # Update UI with selected medicine info
        self.med_name_label.setText(medicine.get('name', 'N/A'))
        
        batch_text = f"Batch: {medicine.get('batch_no', '-')}"
        self.med_batch_label.setText(batch_text)
        
        expiry_date = medicine.get('expiry_date', '')
        expiry_text = "Expiry: " + self._format_date(expiry_date)
        self.med_expiry_label.setText(expiry_text)
        
        stock = medicine.get('quantity', 0)
        stock_text = f"Stock: {stock}"
        self.med_stock_label.setText(stock_text)
        
        # Set quantity limits
        self.quantity_spin.setMaximum(stock if stock > 0 else 9999)
        self.quantity_spin.setValue(1)
        
        # Set visual cues for expiry/stock
        if is_expired(expiry_date):
            self.med_expiry_label.setStyleSheet("color: red; font-size: 12px;")
        else:
            self.med_expiry_label.setStyleSheet("color: #555; font-size: 12px;")
            
        if stock <= 0:
            self.med_stock_label.setStyleSheet("color: red; font-size: 12px;")
        else:
            self.med_stock_label.setStyleSheet("color: #555; font-size: 12px;")

    def _format_date(self, date_str):
        """Format date for display."""
        if not date_str:
            return "-"
        try:
            date = datetime.datetime.strptime(date_str, "%Y-%m-%d").date()
            return date.strftime("%d-%b-%Y")
        except ValueError:
            return date_str

    def load_customers(self):
        """Load customers from the database into the customer combo box."""
        self.cust_combo.clear()
        self.cust_combo.addItem("Select Customer...", None)
        try:
            customers = get_customers()
            for cust in customers:
                self.cust_combo.addItem(f"{cust['name']} ({cust['contact']})", cust['id'])
        except Exception as e:
            QMessageBox.critical(self, "Database Error", f"Could not load customers: {e}")

    def toggle_customer_fields(self):
        """Toggle visibility of customer fields based on customer type selection."""
        selection = self.cust_type_combo.currentText()
        is_existing = selection == "Existing Customer"
        is_new = selection == "New Customer"
        self.cust_combo.setVisible(is_existing)
        label_for_cust_combo = self.cust_combo.parent().layout().labelForField(self.cust_combo) if self.cust_combo.parent() else None
        if label_for_cust_combo:
            label_for_cust_combo.setVisible(is_existing)
        self.new_cust_name.setVisible(is_new)
        label_for_new_name = self.new_cust_name.parent().layout().labelForField(self.new_cust_name) if self.new_cust_name.parent() else None
        if label_for_new_name:
            label_for_new_name.setVisible(is_new)
        self.new_cust_contact.setVisible(is_new)
        label_for_new_contact = self.new_cust_contact.parent().layout().labelForField(self.new_cust_contact) if self.new_cust_contact.parent() else None
        if label_for_new_contact:
            label_for_new_contact.setVisible(is_new)

    def add_item(self):
        """Add a selected medicine to the invoice items."""
        if not self.selected_medicine:
            QMessageBox.warning(self, "Selection Error", "Please select a medicine first.")
            return

        med = self.selected_medicine
        if is_expired(med.get("expiry_date", "2099-01-01")):
            QMessageBox.warning(self, "Expired Medicine", f"{med['name']} is expired and cannot be sold.")
            return

        qty = self.quantity_spin.value()
        discount = self.discount_spin.value()
        if qty <= 0:
            return

        # Check if medicine already exists in invoice
        for item in self.invoice_items:
            if item['id'] == med['id']:
                new_qty = item['qty'] + qty
                if new_qty > med['quantity']:
                    QMessageBox.warning(self, "Stock Error", f"Not enough stock for {med['name']}. Available: {med['quantity']}.")
                    return
                item['qty'] = new_qty
                item['discount'] = discount
                item['total'] = new_qty * med['unit_price'] * (1 - discount / 100)
                break
        else:
            if qty > med['quantity']:
                QMessageBox.warning(self, "Stock Error", f"Not enough stock for {med['name']}. Available: {med['quantity']}.")
                return
            self.invoice_items.append({
                'id': med['id'], 
                'name': med['name'], 
                'strength': med['strength'],
                'qty': qty,
                'unit_price': med['unit_price'],
                'discount': discount,
                'total': qty * med['unit_price'] * (1 - discount / 100)
            })
            
        self.update_table()
        self.update_totals()
        self.clear_selection()

    def clear_selection(self):
        """Clear the current medicine selection."""
        self.selected_medicine = None
        self.selected_med_frame.setVisible(False)
        self.quantity_spin.setValue(1)
        self.discount_spin.setValue(0.0)

    def remove_item(self):
        """Remove a selected item from the invoice table."""
        selected_row = self.table.currentRow()
        if selected_row < 0:
            QMessageBox.warning(self, "Selection Error", "Please select an item to remove.")
            return
        del self.invoice_items[selected_row]
        self.update_table()
        self.update_totals()

    def update_table(self):
        """Update the invoice table with current items."""
        self.table.setRowCount(0)
        for item in self.invoice_items:
            row_pos = self.table.rowCount()
            self.table.insertRow(row_pos)
            self.table.setItem(row_pos, 0, QTableWidgetItem(item['name']))
            self.table.setItem(row_pos, 1, QTableWidgetItem(item['strength']))
            self.table.setItem(row_pos, 2, QTableWidgetItem(str(item['qty'])))
            self.table.setItem(row_pos, 3, QTableWidgetItem(f"₨ {item['unit_price']:.2f}"))
            self.table.setItem(row_pos, 4, QTableWidgetItem(f"{item['discount']:.2f}%"))
            self.table.setItem(row_pos, 5, QTableWidgetItem(f"₨ {item['total']:.2f}"))
        self.table.resizeRowsToContents()

    def update_totals(self):
        """Update the total amount displayed in the invoice."""
        total = sum(item['total'] for item in self.invoice_items)
        self.total_label.setText(f"Total: <b>₨ {total:.2f}</b>")

    def get_or_create_customer(self):
        """Get or create a customer ID based on the selected customer type."""
        selection = self.cust_type_combo.currentText()
        if selection == "Existing Customer":
            return self.cust_combo.currentData()
        if selection == "New Customer":
            name = self.new_cust_name.text().strip()
            contact = self.new_cust_contact.text().strip()
            if not name or not contact:
                QMessageBox.warning(self, "Input Error", "New customer name and contact are required.")
                return None
            try:
                return add_customer(name, contact, "")
            except Exception as e:
                QMessageBox.critical(self, "Database Error", f"Failed to add new customer: {e}")
                return None
        return None

    def save_sales_to_db(self, customer_id):
        """Save invoice items to the database."""
        for item in self.invoice_items:
            success, message = record_sale_with_stock_update(
                medicine_id=item['id'],
                quantity=item['qty'],
                customer_id=customer_id
            )
            if not success:
                print(f"Warning: Failed to record sale for {item['name']}: {message}")

    def print_and_record_invoice(self):
        """Print the invoice and record sales in the database."""
        if not self.invoice_items:
            QMessageBox.warning(self, "Error", "Invoice is empty! Add items before printing.")
            return
        customer_id = self.get_or_create_customer()
        if self.cust_type_combo.currentText() == "New Customer" and customer_id is None:
            QMessageBox.warning(self, "Customer Error", "Please provide a name and contact for the new customer.")
            return
        pharmacy_details = {
            "name": "City Pharmacy",
            "address": "123 Health St, Kāmoke, Pakistan",
            "phone": "+92 300 1234567"
        }
        customer_name = "Walk-in Customer"
        if self.cust_type_combo.currentText() == "New Customer":
            customer_name = self.new_cust_name.text()
        elif self.cust_type_combo.currentText() == "Existing Customer" and self.cust_combo.currentData() is not None:
            customer_name = self.cust_combo.currentText().split('(')[0].strip() if self.cust_combo.currentText() else "Unknown"
        invoice_details = {
            "invoice_number": datetime.datetime.now().strftime("%Y%m%d%H%M%S"),
            "date": datetime.datetime.now().strftime('%d-%b-%Y %I:%M %p'),
            "cashier": self.user.get('full_name', 'N/A'),
            "customer": customer_name
        }
        total = sum(item['total'] for item in self.invoice_items)
        totals = {
            "total": total
        }
        html_receipt = generate_receipt_html(pharmacy_details, invoice_details, self.invoice_items, totals)
        printer = QPrinter(QPrinter.HighResolution)
        print_dialog = QPrintDialog(printer, self)
        if print_dialog.exec_() == QPrintDialog.Accepted:
            try:
                doc = QTextDocument()
                doc.setHtml(html_receipt)
                doc.print_(printer)
                self.save_sales_to_db(customer_id)
                if hasattr(self.parent_window, 'refresh_all'):
                    self.parent_window.refresh_all()
                QMessageBox.information(self, "Success", "Invoice printed and sales recorded successfully!")
                db_signals.sale_recorded.emit()
                self.accept()
            except Exception as e:
                QMessageBox.critical(self, "Print/Save Error", f"Failed to print or save invoice: {str(e)}")
        else:
            QMessageBox.information(self, "Print Cancelled", "Invoice printing was cancelled.")