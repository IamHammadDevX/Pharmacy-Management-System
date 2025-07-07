import datetime
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QDoubleValidator, QTextDocument
from PyQt5.QtPrintSupport import QPrinter, QPrintDialog
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QPushButton, QLabel, QLineEdit, QComboBox, QSpinBox, QMessageBox,
    QHeaderView, QFormLayout, QFrame, QSizePolicy
)
from db import get_all_medicines, record_sale_with_stock_update, get_customers, add_customer, db_signals

def generate_receipt_html(pharmacy_details, invoice_details, invoice_items, totals):
    """
    Generates a compact, modern HTML receipt for printing.

    Args:
        pharmacy_details (dict): Contains name, address, phone.
        invoice_details (dict): Contains invoice_number, date, cashier, customer.
        invoice_items (list): List of dictionaries for each item sold.
        totals (dict): Contains subtotal, discount, and total.
    """
    
    # --- Start of HTML Template ---
    html = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <style>
            /* Use inline styles as QTextDocument is picky */
            body {{
                font-family: 'Consolas', 'Courier New', monospace;
                font-size: 10pt;
                color: #000;
                line-height: 1.3;
                width: 2.8in; /* Common receipt paper width (adjust if needed) */
                margin: 0;
                padding: 5px;
            }}
            .container {{
                padding: 10px;
            }}
            .header {{
                text-align: center;
                margin-bottom: 10px;
            }}
            .header h2 {{
                margin: 0;
                font-size: 14pt;
                font-weight: bold;
            }}
            .header p {{
                margin: 2px 0;
                font-size: 9pt;
            }}
            hr.dashed {{
                border-top: 1px dashed #000;
                border-bottom: none;
                margin: 10px 0;
            }}
            table {{
                width: 100%;
                border-collapse: collapse;
            }}
            .meta-info td:first-child {{ text-align: left; }}
            .meta-info td:last-child {{ text-align: right; }}

            /* --- Items Table Specific Styles --- */
            .items-table {{
                border: 1px solid #000; /* Border around the entire table */
                margin-top: 5px;
                margin-bottom: 5px;
            }}
            .items-table th, .items-table td {{
                padding: 4px 5px; /* Consistent padding for cells */
                border: 1px solid #000; /* Borders for each cell */
                word-wrap: break-word; /* Ensure long text wraps */
            }}
            .items-table thead th {{
                background-color: #f0f0f0; /* Light background for header */
                font-weight: bold;
                text-align: center; /* Center align header text */
            }}
            .items-table tbody td {{
                vertical-align: top; /* Align content to the top within cells */
            }}
            
            /* Column specific alignments */
            .items-table th:nth-child(1), .items-table td:nth-child(1) {{
                text-align: left; /* Item Name - Left aligned */
                width: 45%; /* Allocate more width to the item name */
            }}
            .items-table th:nth-child(2), .items-table td:nth-child(2) {{
                text-align: center; /* Quantity - Center aligned */
                width: 15%;
            }}
            .items-table th:nth-child(3), .items-table td:nth-child(3) {{
                text-align: right; /* Unit Price - Right aligned */
                width: 20%;
            }}
            .items-table th:nth-child(4), .items-table td:nth-child(4) {{
                text-align: right; /* Total - Right aligned */
                width: 20%;
            }}

            .totals-table td:first-child {{ text-align: right; font-weight: bold; }}
            .totals-table td:last-child {{ text-align: right; width: 80px; }}
            .grand-total td {{
                font-size: 12pt;
                font-weight: bold;
                padding-top: 5px;
            }}
            .footer {{
                text-align: center;
                margin-top: 10px;
                font-size: 9pt;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h2>{pharmacy_details['name']}</h2>
                <p>{pharmacy_details['address']}</p>
                <p>Phone: {pharmacy_details['phone']}</p>
            </div>

            <hr class="dashed">

            <table class="meta-info">
                <tr><td>Invoice #:</td><td>{invoice_details['invoice_number']}</td></tr>
                <tr><td>Date:</td><td>{invoice_details['date']}</td></tr>
                <tr><td>Cashier:</td><td>{invoice_details['cashier']}</td></tr>
                <tr><td>Customer:</td><td>{invoice_details['customer']}</td></tr>
            </table>

            <hr class="dashed">

            <table class="items-table">
                <thead>
                    <tr>
                        <th>Item</th>
                        <th>Qty</th>
                        <th>Price</th>
                        <th>Total</th>
                    </tr>
                </thead>
                <tbody>
                    {''.join([f"<tr><td>{item['name']} ({item['strength']})</td><td>{item['qty']}</td><td>${item['unit_price']:.2f}</td><td>${item['total']:.2f}</td></tr>" for item in invoice_items])}
                </tbody>
            </table>

            <hr class="dashed">

            <table class="totals-table">
                <tr><td>Subtotal:</td><td>${totals['subtotal']:.2f}</td></tr>
                <tr><td>Discount:</td><td>${totals['discount']:.2f}</td></tr>
                <tr class="grand-total">
                    <td>Grand Total:</td>
                    <td>${totals['total']:.2f}</td>
                </tr>
            </table>
            
            <hr class="dashed">

            <div class="footer">
                <p>Thank you for your business!</p>
                <p>Your Health, Our Priority.</p>
            </div>
        </div>
    </body>
    </html>
    """
    # --- End of HTML Template ---
    
    return html

class InvoiceDialog(QDialog):
    def __init__(self, user, parent=None):
        super().__init__(parent)
        self.user = user
        self.parent_window = parent
        self.setWindowTitle("Create Invoice")
        # Set a more reasonable initial size; the layout will be flexible.
        self.setMinimumSize(900, 600) 

        # --- Refined Stylesheet for a Modern POS Look ---
        self.setStyleSheet("""
            QDialog {
                background-color: #f0f2f5; /* Light grey background */
            }
            /* --- Left Sidebar Styling --- */
            QFrame#left_sidebar {
                background-color: #ffffff;
                border-radius: 8px;
                border: 1px solid #e0e0e0;
                max-width: 320px; /* Constrain sidebar width */
            }
            /* --- Card Styling for Grouping Widgets --- */
            QFrame#card {
                background-color: #f8f9fa;
                border-radius: 8px;
                border: 1px solid #e9ecef;
                padding: 15px;
            }
            QLabel {
                font-size: 14px;
                color: #34495e;
            }
            /* --- Main Header for the Invoice --- */
            QLabel#header_label {
                font-size: 26px;
                font-weight: bold;
                color: #2c3e50;
                padding-bottom: 10px;
            }
            /* --- Smaller labels for forms --- */
            QFormLayout QLabel {
                font-size: 13px;
                font-weight: 500;
                color: #2c3e50;
            }
            QLineEdit, QComboBox, QSpinBox {
                border: 1px solid #d0d0d0;
                border-radius: 5px;
                padding: 8px; /* Reduced padding for compact look */
                font-size: 13px;
                background-color: white;
            }
            QComboBox::drop-down {
                border: none;
            }
            /* --- Buttons with Hover Effects --- */
            QPushButton {
                border-radius: 6px;
                padding: 10px 15px;
                font-weight: bold;
                border: none;
                color: white;
                font-size: 14px;
                transition: background 0.3s ease;
            }
            QPushButton#add_item_btn {
                background-color: #007bff; /* Blue */
            }
            QPushButton#add_item_btn:hover {
                background-color: #0056b3;
            }
            QPushButton#remove_item_btn {
                background-color: #dc3545; /* Red */
            }
            QPushButton#remove_item_btn:hover {
                background-color: #c82333;
            }
            QPushButton#print_invoice_btn {
                background-color: #28a745; /* Green */
                padding: 12px 25px; /* Make primary action button larger */
                font-size: 15px;
            }
            QPushButton#print_invoice_btn:hover {
                background-color: #218838;
            }
            /* --- Table Styling --- */
            QTableWidget {
                background-color: white;
                border: 1px solid #e0e0e0;
                border-radius: 8px;
                selection-background-color: #e0eafc;
                gridline-color: #f0f0f0;
                font-size: 13px;
            }
            QHeaderView::section {
                background-color: #f8f9fa;
                color: #34495e;
                padding: 8px;
                border: 1px solid #e0e0e0;
                font-weight: bold;
                font-size: 13px;
            }
            /* --- Totals Section Styling --- */
            QFrame#totals_frame {
                background-color: #e6f7ff;
                border: 1px solid #cceeff;
                border-radius: 8px;
            }
            QLabel#total_label {
                font-size: 20px;
                font-weight: bold;
                color: #28a745;
            }
        """)
        
        # --- Main Horizontal Layout (Sidebar + Main Content) ---
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(15)

        # --- Left Sidebar Panel ---
        left_sidebar = QFrame()
        left_sidebar.setObjectName("left_sidebar")
        sidebar_layout = QVBoxLayout(left_sidebar)
        sidebar_layout.setContentsMargins(15, 15, 15, 15)
        sidebar_layout.setSpacing(20)

        # --- Card 1: Add Medicine ---
        add_item_card = QFrame()
        add_item_card.setObjectName("card")
        add_item_layout = QFormLayout(add_item_card)
        add_item_layout.setSpacing(12)
        add_item_layout.addRow(QLabel("<b>Add Medicine</b>"))
        
        self.medicine_combo = QComboBox()
        self.load_medicines()
        add_item_layout.addRow("Medicine:", self.medicine_combo)

        self.quantity_spin = QSpinBox()
        self.quantity_spin.setMinimum(1)
        self.quantity_spin.setMaximum(9999)
        add_item_layout.addRow("Quantity:", self.quantity_spin)
        
        btn_add = QPushButton("➕ Add Item")
        btn_add.setObjectName("add_item_btn")
        btn_add.setCursor(Qt.PointingHandCursor)
        add_item_layout.addRow(btn_add)
        
        sidebar_layout.addWidget(add_item_card)

        # --- Card 2: Customer Information ---
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
        self.load_customers()
        customer_layout.addRow("Select:", self.cust_combo)
        
        self.new_cust_name = QLineEdit(placeholderText="Full Name")
        customer_layout.addRow("Name:", self.new_cust_name)
        
        self.new_cust_contact = QLineEdit(placeholderText="Phone/Email")
        customer_layout.addRow("Contact:", self.new_cust_contact)
        
        sidebar_layout.addWidget(customer_card)
        sidebar_layout.addStretch() # Push cards to the top
        
        main_layout.addWidget(left_sidebar)

        # --- Right Main Content Panel ---
        right_panel = QFrame()
        right_panel_layout = QVBoxLayout(right_panel)
        right_panel_layout.setContentsMargins(0, 0, 0, 0)
        right_panel_layout.setSpacing(15)

        header_label = QLabel("Create Invoice")
        header_label.setObjectName("header_label")
        right_panel_layout.addWidget(header_label)
        
        # Invoice Table
        self.table = QTableWidget(0, 5)
        self.table.setHorizontalHeaderLabels(["Medicine", "Strength", "Qty", "Unit Price", "Total"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding) # Allow table to grow
        right_panel_layout.addWidget(self.table)

        # Remove Item Button (aligned to the right)
        remove_btn_layout = QHBoxLayout()
        remove_btn_layout.addStretch()
        btn_remove = QPushButton("🗑️ Remove")
        btn_remove.setObjectName("remove_item_btn")
        btn_remove.setCursor(Qt.PointingHandCursor)
        btn_remove.clicked.connect(self.remove_item)
        remove_btn_layout.addWidget(btn_remove)
        right_panel_layout.addLayout(remove_btn_layout)
        
        # Bottom section with totals and print button
        bottom_layout = QHBoxLayout()
        
        # Totals Frame
        totals_frame = QFrame()
        totals_frame.setObjectName("totals_frame")
        totals_layout = QFormLayout(totals_frame)
        totals_layout.setSpacing(10)

        self.subtotal_label = QLabel("Subtotal: <b>$0.00</b>")
        self.discount_input = QLineEdit("0.00")
        self.discount_input.setValidator(QDoubleValidator(0.00, 99999.99, 2))
        self.total_label = QLabel("Total: <b>$0.00</b>")
        self.total_label.setObjectName("total_label")

        totals_layout.addRow("Subtotal:", self.subtotal_label)
        totals_layout.addRow("Discount:", self.discount_input)
        totals_layout.addRow(self.total_label)
        
        bottom_layout.addWidget(totals_frame)
        bottom_layout.addStretch()

        # Print Button
        print_btn_layout = QVBoxLayout()
        print_btn_layout.addStretch()
        btn_print = QPushButton("🖨️ Complete & Print")
        btn_print.setObjectName("print_invoice_btn")
        btn_print.setCursor(Qt.PointingHandCursor)
        print_btn_layout.addWidget(btn_print)
        print_btn_layout.addStretch()
        bottom_layout.addLayout(print_btn_layout)

        right_panel_layout.addLayout(bottom_layout)
        main_layout.addWidget(right_panel)
        
        # --- Final Setup and Signals ---
        self.setLayout(main_layout)
        self.toggle_customer_fields() # Initial field visibility
        
        self.invoice_items = []
        self.update_totals()

        # Connect signals
        btn_add.clicked.connect(self.add_item)
        btn_print.clicked.connect(self.print_and_record_invoice)
        self.discount_input.textChanged.connect(self.update_totals)
        db_signals.medicine_updated.connect(self.load_medicines)
        db_signals.sale_recorded.connect(self.load_medicines)

    def load_medicines(self):
        """Populate medicine dropdown, only showing in-stock items."""
        current_selection = self.medicine_combo.currentData()
        self.medicine_combo.clear()
        self.medicine_combo.addItem("Select Medicine...", None)
        try:
            all_medicines = get_all_medicines()
            for med in all_medicines:
                if med['quantity'] > 0:
                    text = f"{med['name']} ({med['strength']}) - Stock: {med['quantity']}"
                    self.medicine_combo.addItem(text, med)
                else:
                    text = f"{med['name']} ({med['strength']}) - OUT OF STOCK"
                    self.medicine_combo.addItem(text, med)
                    index = self.medicine_combo.findText(text)
                    if index != -1:
                        self.medicine_combo.model().item(index).setEnabled(False)
            
            if current_selection:
                index = self.medicine_combo.findData(current_selection)
                if index != -1:
                    self.medicine_combo.setCurrentIndex(index)
        except Exception as e:
            QMessageBox.critical(self, "Database Error", f"Could not load medicines: {e}")

    def load_customers(self):
        """Populate customer dropdown."""
        self.cust_combo.clear()
        self.cust_combo.addItem("Select Customer...", None)
        try:
            customers = get_customers()
            for cust in customers:
                self.cust_combo.addItem(f"{cust['name']} ({cust['contact']})", cust['id'])
        except Exception as e:
            QMessageBox.critical(self, "Database Error", f"Could not load customers: {e}")

    def toggle_customer_fields(self):
        """Toggles visibility of customer input fields based on selection."""
        selection = self.cust_type_combo.currentText()
        is_existing = selection == "Existing Customer"
        is_new = selection == "New Customer"
        
        customer_layout = self.cust_combo.parent().layout()

        self.cust_combo.setVisible(is_existing)
        label_for_cust_combo = customer_layout.labelForField(self.cust_combo)
        if label_for_cust_combo:
            label_for_cust_combo.setVisible(is_existing)

        self.new_cust_name.setVisible(is_new)
        label_for_new_name = customer_layout.labelForField(self.new_cust_name)
        if label_for_new_name:
            label_for_new_name.setVisible(is_new)

        self.new_cust_contact.setVisible(is_new)
        label_for_new_contact = customer_layout.labelForField(self.new_cust_contact)
        if label_for_new_contact:
            label_for_new_contact.setVisible(is_new)

    def get_or_create_customer(self):
        """Gets selected customer ID or creates a new customer."""
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
                return add_customer(name, contact, "") # Assuming address is optional
            except Exception as e:
                QMessageBox.critical(self, "Database Error", f"Failed to add new customer: {e}")
                return None
                
        return None # Walk-in customer

    def add_item(self):
        """Adds selected medicine to the invoice table."""
        med_data = self.medicine_combo.currentData()
        if not med_data:
            QMessageBox.warning(self, "Input Error", "Please select a medicine.")
            return
            
        qty = self.quantity_spin.value()
        if qty <= 0:
            return

        for item in self.invoice_items:
            if item['id'] == med_data['id']:
                new_qty = item['qty'] + qty
                if new_qty > med_data['quantity']:
                    QMessageBox.warning(self, "Stock Error", f"Not enough stock for {med_data['name']}. Available: {med_data['quantity']}.")
                    return
                item['qty'] = new_qty
                item['total'] = new_qty * item['unit_price']
                break
        else: 
            if qty > med_data['quantity']:
                QMessageBox.warning(self, "Stock Error", f"Not enough stock for {med_data['name']}. Available: {med_data['quantity']}.")
                return
            self.invoice_items.append({
                'id': med_data['id'], 'name': med_data['name'], 'strength': med_data['strength'],
                'qty': qty, 'unit_price': med_data['unit_price'], 'total': qty * med_data['unit_price']
            })
        
        self.update_table()
        self.update_totals()
        self.medicine_combo.setCurrentIndex(0)
        self.quantity_spin.setValue(1)
    
    def remove_item(self):
        """Removes selected row from the invoice table."""
        selected_row = self.table.currentRow()
        if selected_row < 0:
            QMessageBox.warning(self, "Selection Error", "Please select an item to remove.")
            return
        
        del self.invoice_items[selected_row]
        self.update_table()
        self.update_totals()
    
    def update_table(self):
        """Refreshes the invoice table."""
        self.table.setRowCount(0)
        for item in self.invoice_items:
            row_pos = self.table.rowCount()
            self.table.insertRow(row_pos)
            self.table.setItem(row_pos, 0, QTableWidgetItem(item['name']))
            self.table.setItem(row_pos, 1, QTableWidgetItem(item['strength']))
            self.table.setItem(row_pos, 2, QTableWidgetItem(str(item['qty'])))
            self.table.setItem(row_pos, 3, QTableWidgetItem(f"${item['unit_price']:.2f}"))
            self.table.setItem(row_pos, 4, QTableWidgetItem(f"${item['total']:.2f}"))
        self.table.resizeRowsToContents()
    
    def update_totals(self):
        """Calculates and displays subtotal, discount, and grand total."""
        subtotal = sum(item['total'] for item in self.invoice_items)
        
        try:
            discount = float(self.discount_input.text()) if self.discount_input.text() else 0.0
            if discount > subtotal:
                discount = subtotal
                self.discount_input.setText(f"{discount:.2f}")
        except ValueError:
            discount = 0.0
            
        total = max(0, subtotal - discount)
        
        self.subtotal_label.setText(f"Subtotal: <b>${subtotal:.2f}</b>")
        self.total_label.setText(f"Total: <b>${total:.2f}</b>")
    
    def save_sales_to_db(self, customer_id):
        """Records each item as a sale in the database."""
        for item in self.invoice_items:
            success, message = record_sale_with_stock_update(
                medicine_id=item['id'],
                quantity=item['qty'],
                customer_id=customer_id
            )
            if not success:
                print(f"Warning: Failed to record sale for {item['name']}: {message}") # This print statement remains for critical DB save warnings

    def print_and_record_invoice(self):
        """Generates printable invoice, records sales, and refreshes data."""
        if not self.invoice_items:
            QMessageBox.warning(self, "Error", "Invoice is empty! Add items before printing.")
            return

        try:
            discount = float(self.discount_input.text()) if self.discount_input.text() else 0.0
        except ValueError:
            discount = 0.0

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
        
        subtotal = sum(item['total'] for item in self.invoice_items)
        total = max(0, subtotal - discount)
        
        totals = {
            "subtotal": subtotal,
            "discount": discount,
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