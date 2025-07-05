from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTableWidget, 
    QTableWidgetItem, QPushButton, QLabel, QLineEdit,
    QComboBox, QSpinBox, QMessageBox
)
from PyQt5.QtCore import Qt
from PyQt5.QtPrintSupport import QPrinter, QPrintDialog
from PyQt5.QtGui import QTextDocument
from db import get_all_medicines, record_sale
import datetime

class InvoiceDialog(QDialog):
    def __init__(self, user, parent=None):
        super().__init__(parent)
        self.user = user
        self.parent_window = parent  # Store reference to parent
        self.setWindowTitle("Create Invoice")
        self.setMinimumSize(700, 600)
        
        # Main layout
        layout = QVBoxLayout()
        
        # --- Medicine Selection ---
        self.medicine_combo = QComboBox()
        self.quantity_spin = QSpinBox()
        self.quantity_spin.setMinimum(1)
        self.quantity_spin.setMaximum(999)
        
        # --- Invoice Table ---
        self.table = QTableWidget(0, 5)
        self.table.setHorizontalHeaderLabels(["Medicine", "Strength", "Qty", "Unit Price", "Total"])
        self.table.horizontalHeader().setStretchLastSection(True)
        
        # --- Totals ---
        self.subtotal_label = QLabel("Subtotal: $0.00")
        self.discount_input = QLineEdit()
        self.discount_input.setPlaceholderText("Discount Amount")
        self.discount_input.setText("0")
        self.total_label = QLabel("Total: $0.00")
        
        # --- Buttons ---
        btn_add = QPushButton("➕ Add Item")
        btn_print = QPushButton("🖨️ Print Invoice")
        btn_print.setStyleSheet("background: #4CAF50; color: white;")
        
        # Add widgets
        selection_layout = QHBoxLayout()
        selection_layout.addWidget(QLabel("Medicine:"))
        selection_layout.addWidget(self.medicine_combo, 3)
        selection_layout.addWidget(QLabel("Qty:"))
        selection_layout.addWidget(self.quantity_spin, 1)
        selection_layout.addWidget(btn_add)
        
        totals_layout = QHBoxLayout()
        totals_layout.addWidget(self.subtotal_label)
        totals_layout.addWidget(QLabel("Discount:"))
        totals_layout.addWidget(self.discount_input)
        totals_layout.addWidget(self.total_label)
        
        layout.addLayout(selection_layout)
        layout.addWidget(self.table)
        layout.addLayout(totals_layout)
        layout.addWidget(btn_print)
        
        self.setLayout(layout)
        
        # Connect signals
        btn_add.clicked.connect(self.add_item)
        btn_print.clicked.connect(self.print_invoice)
        self.discount_input.textChanged.connect(self.update_totals)
        
        self.load_medicines()
        self.invoice_items = []
    
    def load_medicines(self):
        """Populate medicine dropdown"""
        self.medicine_combo.clear()
        self.medicine_combo.addItem("Select Medicine", None)
        for med in get_all_medicines():
            if med['quantity'] > 0:  # Only show medicines in stock
                self.medicine_combo.addItem(
                    f"{med['name']} ({med['strength']}) - ${med['unit_price']} (Stock: {med['quantity']})", 
                    med
                )
    
    def add_item(self):
        """Add selected medicine to invoice"""
        med_data = self.medicine_combo.currentData()
        if not med_data:
            QMessageBox.warning(self, "Error", "Please select a medicine")
            return
            
        qty = self.quantity_spin.value()
        if qty > med_data['quantity']:
            QMessageBox.warning(self, "Error", f"Only {med_data['quantity']} available in stock")
            return
            
        # Add to invoice items
        self.invoice_items.append({
            'id': med_data['id'],
            'name': med_data['name'],
            'strength': med_data['strength'],
            'qty': qty,
            'unit_price': med_data['unit_price'],
            'total': qty * med_data['unit_price']
        })
        
        self.update_table()
        self.update_totals()
    
    def update_table(self):
        """Refresh invoice table"""
        self.table.setRowCount(len(self.invoice_items))
        for row, item in enumerate(self.invoice_items):
            self.table.setItem(row, 0, QTableWidgetItem(item['name']))
            self.table.setItem(row, 1, QTableWidgetItem(item['strength']))
            self.table.setItem(row, 2, QTableWidgetItem(str(item['qty'])))
            self.table.setItem(row, 3, QTableWidgetItem(f"${item['unit_price']:.2f}"))
            self.table.setItem(row, 4, QTableWidgetItem(f"${item['total']:.2f}"))
    
    def update_totals(self):
        """Calculate and display totals"""
        subtotal = sum(item['total'] for item in self.invoice_items)
        
        try:
            discount = float(self.discount_input.text() or 0)
        except ValueError:
            discount = 0
            
        total = max(0, subtotal - discount)
        
        self.subtotal_label.setText(f"Subtotal: ${subtotal:.2f}")
        self.total_label.setText(f"Total: ${total:.2f}")
    
    def print_invoice(self):
        """Generate printable invoice"""
        if not self.invoice_items:
            QMessageBox.warning(self, "Error", "Invoice is empty!")
            return
            
        try:
            discount = float(self.discount_input.text() or 0)
        except ValueError:
            discount = 0
            
        # Create HTML for printing
        html = f"""
        <html>
        <body>
            <h1>Pharmacy Invoice</h1>
            <p>Date: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}</p>
            <p>Cashier: {self.user['full_name']}</p>
            <hr>
            <table width="100%" border="1" cellspacing="0" cellpadding="5">
                <tr>
                    <th>Medicine</th>
                    <th>Strength</th>
                    <th>Qty</th>
                    <th>Price</th>
                    <th>Total</th>
                </tr>
                {"".join(f"""
                <tr>
                    <td>{item['name']}</td>
                    <td>{item['strength']}</td>
                    <td align="right">{item['qty']}</td>
                    <td align="right">${item['unit_price']:.2f}</td>
                    <td align="right">${item['total']:.2f}</td>
                </tr>
                """ for item in self.invoice_items)}
            </table>
            <hr>
            <table width="100%">
                <tr>
                    <td width="70%"></td>
                    <td>
                        <p>Subtotal: ${sum(item['total'] for item in self.invoice_items):.2f}</p>
                        <p>Discount: ${discount:.2f}</p>
                        <h3>Grand Total: ${max(0, sum(item['total'] for item in self.invoice_items) - discount):.2f}</h3>
                    </td>
                </tr>
            </table>
            <p style="margin-top: 30px; text-align: center">Thank you for your purchase!</p>
        </body>
        </html>
        """
        
        # Create printer and dialog
        printer = QPrinter(QPrinter.HighResolution)
        print_dialog = QPrintDialog(printer, self)
        
        # Execute the print dialog
        if print_dialog.exec_() == QPrintDialog.Accepted:
            try:
                doc = QTextDocument()
                doc.setHtml(html)
                doc.print_(printer)
                
                # Save to database
                self.save_to_db(discount)
                
                # Refresh parent window if exists
                if hasattr(self.parent_window, 'refresh_all'):
                    self.parent_window.refresh_all()
                    
                QMessageBox.information(self, "Success", "Invoice printed and saved!")
                self.accept()
            except Exception as e:
                QMessageBox.critical(self, "Print Error", f"Failed to print invoice: {str(e)}")
    
    def save_to_db(self, discount):
        """Save invoice to database"""
        # Implement your DB saving logic here
        # Example:
        for item in self.invoice_items:
            record_sale(
                medicine_id=item['id'],
                quantity=item['qty'],
                customer_id=None  # Add customer if needed
            )