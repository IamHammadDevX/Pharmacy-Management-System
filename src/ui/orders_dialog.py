from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QHBoxLayout, QStatusBar, QMessageBox, QHeaderView, QFileDialog, QPushButton, QTableWidget, QTableWidgetItem, QInputDialog, QWidget, QSizePolicy
from PyQt5.QtCore import Qt, pyqtSignal
# from widgets.paginated_table import PaginatedTable # This import might not be needed if PaginatedTable isn't used elsewhere
from db import get_all_medicines, get_all_orders, update_order_status, insert_order, db_signals
import csv
from datetime import datetime

class OrdersDialog(QDialog):
    order_updated = pyqtSignal()  # Local signal for internal refresh

    def __init__(self, user=None, parent=None):
        super().__init__(parent)
        if not user or user.get("role") != "admin":
            QMessageBox.critical(self, "Access Denied", "Only admins can manage orders.")
            self.reject()
            return
        self.user = user
        self._cached_medicines = []
        self._cached_orders = []
        self.setWindowTitle("Order Management")
        self.setMinimumSize(1000, 700)
        self.setStyleSheet("""
            QDialog {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #f5f6fa, stop:1 #ffffff);
                border-radius: 12px;
            }
            QLabel {
                font-size: 28px;
                font-weight: bold;
                color: #2c3e50;
            }
            QTableWidget {
                background: white;
                border: 1px solid #e0e0e0;
                border-radius: 10px;
                gridline-color: #f0f0f0; /* Lighter grid lines */
            }
            QTableWidget::item {
                padding: 8px; /* Slightly reduced padding */
            }
            QTableWidget::item:selected {
                background: #6c5ce7; /* Modern purple for selection */
                color: white;
            }
            QHeaderView::section {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #6c5ce7, stop:1 #4834d4); /* Purple gradient */
                color: white;
                font-weight: bold;
                padding: 10px; /* Consistent padding */
                border: none;
                border-top-left-radius: 8px; /* Rounded corners for header */
                border-top-right-radius: 8px;
            }
            QPushButton {
                border-radius: 8px; /* More rounded corners */
                padding: 8px 16px; /* Increased padding for larger buttons */
                min-width: 90px; /* Slightly wider */
                font-weight: bold;
                border: none; /* No default border */
                color: white; /* Default text color */
                font-size: 14px; /* Slightly larger font */
                transition: background 0.3s ease; /* Smooth transition for hover */
            }
            QPushButton#export_btn {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #0984e3, stop:1 #0062a3); /* Blue gradient */
            }
            QPushButton#export_btn:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #0062a3, stop:1 #0984e3);
            }

            /* --- STYLING FOR APPROVE/REJECT BUTTONS --- */
            QPushButton#approve_btn {
                background: transparent; /* No background color */
                color: #27ae60; /* Green text */
                border: 1px solid #27ae60; /* Green border */
                border-radius: 5px; /* Smaller rounding for compact look */
                padding: 3px 8px; /* Smaller padding */
                min-width: 60px; /* Even smaller min-width */
                font-size: 12px; /* Smaller font size */
                font-weight: normal; /* Less bold */
            }
            QPushButton#approve_btn:hover {
                background: #e6f7ed; /* Light green background on hover */
                color: #27ae60;
            }
            QPushButton#reject_btn {
                background: transparent; /* No background color */
                color: #c0392b; /* Red text */
                border: 1px solid #c0392b; /* Red border */
                border-radius: 5px; /* Smaller rounding for compact look */
                padding: 3px 8px; /* Smaller padding */
                min-width: 60px; /* Even smaller min-width */
                font-size: 12px; /* Smaller font size */
                font-weight: normal; /* Less bold */
            }
            QPushButton#reject_btn:hover {
                background: #fdeaea; /* Light red background on hover */
                color: #c0392b;
            }
            /* Disabled state for action buttons (Approve/Reject) */
            QPushButton#approve_btn:disabled, QPushButton#reject_btn:disabled {
                background: #f8f8f8; /* Very light background for disabled */
                color: #b0b0b0; /* Light grey text */
                border: 1px solid #d0d0d0; /* Light grey border */
                cursor: default; /* No pointer cursor when disabled */
            }

            QStatusBar {
                background: #ecf0f1;
                color: #2c3e50;
                font-size: 13px;
                border-top: 1px solid #ddd;
                border-bottom-left-radius: 12px; /* Rounded corners for status bar */
                border-bottom-right-radius: 12px;
            }
            /* Styling for the Add Order button in medicines table */
            QPushButton.add_order_btn {
                background: transparent; /* No background color */
                color: #6c5ce7; /* Purple text */
                border: 1px solid #6c5ce7; /* Purple border */
                border-radius: 5px; /* Consistent smaller rounding */
                padding: 3px 8px; /* Consistent smaller padding */
                min-width: 80px; /* Adjusted min-width */
                font-weight: normal; /* Less bold */
                font-size: 12px; /* Consistent smaller font size */
            }
            QPushButton.add_order_btn:hover {
                background: #f0f0ff; /* Very light purple background on hover */
                color: #6c5ce7;
            }
            QPushButton.add_order_btn:pressed {
                background: #e0e0ff; /* Slightly darker light purple on press */
                border: 1px solid #4834d4; /* Darker border on press */
            }
        """)

        # Main layout
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)

        # Header for Medicines Table
        medicines_header = QLabel("Available Medicines")
        medicines_header.setStyleSheet("""
            QLabel {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #6c5ce7, stop:1 #4834d4); /* Purple gradient */
                padding: 15px; /* More padding for header */
                border-radius: 10px;
                color: white;
                text-align: center;
                font-size: 24px; /* Slightly smaller header font */
            }
        """)
        main_layout.addWidget(medicines_header)

        # Medicines Table (for creating orders)
        self.medicines_table = QTableWidget()
        self.medicines_table.setColumnCount(7)
        self.medicines_table.setHorizontalHeaderLabels(["ID", "Name", "Strength", "Batch No", "Expiry Date", "Quantity", "Add Order"])
        self.medicines_table.horizontalHeader().setStretchLastSection(True)
        self.medicines_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        main_layout.addWidget(self.medicines_table)

        # Header for Orders Table
        orders_header = QLabel("All Orders")
        orders_header.setStyleSheet("""
            QLabel {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #6c5ce7, stop:1 #4834d4); /* Purple gradient */
                padding: 15px; /* More padding for header */
                border-radius: 10px;
                color: white;
                text-align: center;
                font-size: 24px; /* Slightly smaller header font */
            }
        """)
        main_layout.addWidget(orders_header)

        # Orders Table (for displaying all orders)
        self.orders_table = QTableWidget()
        self.orders_table.setColumnCount(6)
        self.orders_table.setHorizontalHeaderLabels(["ID", "Medicine Name", "Quantity", "Status", "Order Date", "Actions"])
        self.orders_table.horizontalHeader().setStretchLastSection(True)
        self.orders_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        main_layout.addWidget(self.orders_table)

        # Export button
        button_layout = QHBoxLayout()
        button_layout.setSpacing(15)

        self.export_btn = QPushButton("⬇️ Export All Orders")
        self.export_btn.setObjectName("export_btn")
        self.export_btn.setCursor(Qt.PointingHandCursor)
        self.export_btn.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.export_btn.clicked.connect(self.export_orders) # Connect the button to the method
        button_layout.addWidget(self.export_btn)

        button_layout.addStretch(1)
        main_layout.addLayout(button_layout)

        # Status bar
        self.status_bar = QStatusBar()
        main_layout.addWidget(self.status_bar)

        self.setLayout(main_layout)
        self.load_medicines()
        self.load_orders()

    def load_medicines(self):
        """Load all medicines into the table for order creation"""
        try:
            medicines = get_all_medicines()
            if not medicines:
                self.status_bar.showMessage("No medicines found.", 3000)
                self.medicines_table.setRowCount(0)
                return

            self._cached_medicines = medicines
            self.medicines_table.setRowCount(len(medicines))

            # Optimization: Disable updates before populating table
            self.medicines_table.setUpdatesEnabled(False)
            for row, med in enumerate(medicines):
                self.medicines_table.setItem(row, 0, QTableWidgetItem(str(med["id"])))
                self.medicines_table.setItem(row, 1, QTableWidgetItem(med["name"]))
                self.medicines_table.setItem(row, 2, QTableWidgetItem(med["strength"] or ""))
                self.medicines_table.setItem(row, 3, QTableWidgetItem(med["batch_no"] or ""))
                self.medicines_table.setItem(row, 4, QTableWidgetItem(med["expiry_date"] or ""))
                self.medicines_table.setItem(row, 5, QTableWidgetItem(str(med["quantity"])))
                add_btn = QPushButton("Add Order")
                add_btn.setProperty("class", "add_order_btn")
                add_btn.setCursor(Qt.PointingHandCursor)
                add_btn.clicked.connect(lambda checked, med_id=med["id"]: self.add_order(med_id))
                self.medicines_table.setCellWidget(row, 6, add_btn)
            # Optimization: Re-enable updates after populating table
            self.medicines_table.setUpdatesEnabled(True)

            self.medicines_table.resizeColumnsToContents()
            self.status_bar.showMessage(f"Loaded {len(medicines)} medicines.", 3000)
        except Exception as e:
            self.status_bar.showMessage(f"Error loading medicines: {str(e)}", 5000)

    def load_orders(self):
        """Load all orders (including pending) into the table"""
        try:
            orders = get_all_orders()

            if not orders:
                self.status_bar.showMessage("No orders found.", 3000)
                self.orders_table.setRowCount(0)
                return
            self._cached_orders = orders
            self.orders_table.setRowCount(len(orders))

            # Optimization: Disable updates before populating table
            self.orders_table.setUpdatesEnabled(False)
            for row, order in enumerate(orders):
                self.orders_table.setItem(row, 0, QTableWidgetItem(str(order["id"])))
                self.orders_table.setItem(row, 1, QTableWidgetItem(order["medicine_name"]))
                self.orders_table.setItem(row, 2, QTableWidgetItem(str(order["quantity_ordered"])))
                self.orders_table.setItem(row, 3, QTableWidgetItem(order["status"]))
                self.orders_table.setItem(row, 4, QTableWidgetItem(order["order_date"]))

                # Action buttons container
                action_widget = QWidget()
                action_layout = QHBoxLayout(action_widget)
                action_layout.setContentsMargins(0, 0, 0, 0)
                action_layout.setSpacing(5)

                approve_btn = QPushButton("Approve")
                approve_btn.setObjectName("approve_btn")
                approve_btn.setCursor(Qt.PointingHandCursor)

                reject_btn = QPushButton("Reject")
                reject_btn.setObjectName("reject_btn")
                reject_btn.setCursor(Qt.PointingHandCursor)

                # --- Visibility Logic ---
                current_status = order["status"]

                if current_status == "Pending":
                    approve_btn.setEnabled(True)
                    reject_btn.setEnabled(True)
                elif current_status in ["Approved", "Rejected"]:
                    approve_btn.setEnabled(False)
                    reject_btn.setEnabled(False)
                else:
                    approve_btn.setEnabled(False)
                    reject_btn.setEnabled(False)

                approve_btn.clicked.connect(lambda checked, oid=order["id"]: self.update_order_status(oid, "Approved"))
                reject_btn.clicked.connect(lambda checked, oid=order["id"]: self.update_order_status(oid, "Rejected"))

                action_layout.addWidget(approve_btn)
                action_layout.addWidget(reject_btn)
                action_layout.addStretch(1)
                self.orders_table.setCellWidget(row, 5, action_widget)
            # Optimization: Re-enable updates after populating table
            self.orders_table.setUpdatesEnabled(True)

            self.orders_table.resizeColumnsToContents()
            self.status_bar.showMessage(f"Loaded {len(orders)} orders.", 3000)
            self.order_updated.emit()
        except Exception as e:
            self.status_bar.showMessage(f"Error loading orders: {str(e)}", 5000)

    def add_order(self, medicine_id):
        """Add a new order for the selected medicine"""
        if not self.user or self.user.get("role") != "admin":
            self.status_bar.showMessage("Access denied: Admin only.", 3000)
            return

        medicine = next((m for m in self._cached_medicines if m["id"] == medicine_id), None)
        if not medicine or medicine["quantity"] <= 0:
            self.status_bar.showMessage("Cannot order: No stock available.", 3000)
            return

        quantity, ok = QInputDialog.getInt(
            self,
            "Add Order",
            f"Enter quantity for {medicine['name']} (Available: {medicine['quantity']}):",
            1, 1, medicine["quantity"], 1
        )

        if ok:
            try:
                order_id = insert_order(medicine["name"], quantity)
                self.load_orders()
                self.status_bar.showMessage(
                    f"Order for {medicine['name']} (Qty: {quantity}) added with ID {order_id}. Status: Pending",
                    3000
                )
            except Exception as e:
                self.status_bar.showMessage(f"Error adding order: {str(e)}", 5000)

    def update_order_status(self, order_id, status):
        """Update the status of an order"""
        try:
            update_order_status(order_id, status)
            self.load_orders()
            self.status_bar.showMessage(f"Order {order_id} status updated to {status}.", 3000)
        except Exception as e:
            self.status_bar.showMessage(f"Error updating order status: {str(e)}", 5000)

    def export_orders(self):
        """Export all orders to a CSV file"""
        if not self.user or self.user.get("role") != "admin":
            self.status_bar.showMessage("Access denied: Admin only.", 3000)
            return

        try:
            # Get all orders directly from the database for export to ensure latest data
            all_orders_for_export = get_all_orders()

            if not all_orders_for_export:
                self.status_bar.showMessage("No orders to export.", 3000)
                return

            file_name, _ = QFileDialog.getSaveFileName(
                self,
                "Save All Orders",
                f"all_orders_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                "CSV Files (*.csv)"
            )

            if file_name:
                with open(file_name, 'w', newline='', encoding='utf-8') as csvfile:
                    # Define fieldnames based on the keys in your order dictionaries
                    fieldnames = ["id", "medicine_name", "quantity_ordered", "status", "order_date"]
                    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                    writer.writeheader() # Write the header row
                    for order in all_orders_for_export:
                        writer.writerow(order) # Write each order as a row
                self.status_bar.showMessage(f"All orders exported to {file_name}.", 3000)
        except Exception as e:
            self.status_bar.showMessage(f"Error exporting orders: {str(e)}", 5000)