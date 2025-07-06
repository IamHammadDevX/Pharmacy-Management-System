from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QHBoxLayout, QStatusBar, QMessageBox, QHeaderView, QFileDialog, QPushButton
from PyQt5.QtCore import Qt, pyqtSignal
from widgets.paginated_table import PaginatedTable
from db import get_all_medicines, delete_medicine, db_signals
import csv
from datetime import datetime

class MedicineManagement(QDialog):
    medicine_updated = pyqtSignal()  # Local signal for internal refresh

    def __init__(self, user=None, parent=None):
        super().__init__(parent)
        if not user or user.get("role") != "admin":
            QMessageBox.critical(self, "Access Denied", "Only admins can manage medicine inventory.")
            self.reject()
            return
        self.user = user
        self._cached_medicines = []
        self.setWindowTitle("Medicine Inventory Management")
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
        header = QLabel("Medicine Inventory Management")
        header.setStyleSheet("""
            QLabel {
                font-size: 28px;
                font-weight: bold;
                color: #2c3e50;
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #e74c3c, stop:1 #c0392b);
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
                background: #e74c3c;
                color: white;
            }
            QHeaderView::section {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #e74c3c, stop:1 #c0392b);
                color: white;
                font-weight: bold;
                padding: 12px;
                border: none;
            }
            QPushButton {
                border-radius: 6px;
                padding: 6px 12px;
            }
            QPushButton#alert_btn { background: #f1c40f; color: white; }
            QPushButton#export_btn { background: #3498db; color: white; }
            QPushButton:hover { opacity: 0.9; }
        """)
        main_layout.addWidget(self.table)

        # Button layout
        button_layout = QHBoxLayout()
        button_layout.setSpacing(15)

        self.alert_btn = QPushButton("⚠️ Generate Alerts")
        self.alert_btn.setCursor(Qt.PointingHandCursor)
        self.alert_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #f1c40f, stop:1 #f39c12);
                color: white;
                border-radius: 12px;
                padding: 12px 25px;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #f39c12, stop:1 #f1c40f);
            }
        """)
        self.alert_btn.clicked.connect(self.generate_alerts)
        button_layout.addWidget(self.alert_btn)

        self.export_btn = QPushButton("⬇️ Export Inventory")
        self.export_btn.setCursor(Qt.PointingHandCursor)
        self.export_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #3498db, stop:1 #2980b9);
                color: white;
                border-radius: 12px;
                padding: 12px 25px;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #2980b9, stop:1 #3498db);
            }
        """)
        self.export_btn.clicked.connect(self.export_inventory)
        button_layout.addWidget(self.export_btn)

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
        self.load_medicines()

    def load_medicines(self):
        """Load medicines into the paginated table with caching and alerts"""
        try:
            if not self._cached_medicines:  # Load only if cache is empty
                self._cached_medicines = get_all_medicines()
            if not self._cached_medicines:
                self.status_bar.showMessage("No medicines found.", 3000)
                self.table.set_data([])
                return
            # Prepare data with alert status
            data = []
            today = datetime.today()
            for med in self._cached_medicines:
                alert = "None"
                expiry_date = datetime.strptime(med.get("expiry_date", "9999-12-31"), "%Y-%m-%d")
                if expiry_date <= today:
                    alert = "Expired"
                elif (expiry_date - today).days <= 30:
                    alert = "Expiring Soon"
                if int(med.get("quantity", 0)) < 10:
                    alert = "Low Stock" if alert == "None" else f"{alert}, Low Stock"
                med["alert_status"] = alert
                data.append(med)
            self.table.set_data(data)
            self.status_bar.showMessage(f"Loaded {len(self._cached_medicines)} medicines.", 3000)
            self.medicine_updated.emit()  # Local refresh
        except Exception as e:
            self.status_bar.showMessage(f"Error loading medicines: {str(e)}", 5000)

    def generate_alerts(self):
        """Generate and display alerts for low stock and expiry"""
        if not self.user or self.user.get("role") != "admin":
            self.status_bar.showMessage("Access denied: Admin only.", 3000)
            return
        try:
            alerts = []
            today = datetime.today()
            for med in self._cached_medicines:
                expiry_date = datetime.strptime(med.get("expiry_date", "9999-12-31"), "%Y-%m-%d")
                if expiry_date <= today:
                    alerts.append(f"'{med['name']}' (ID: {med['id']}) is expired.")
                elif (expiry_date - today).days <= 30:
                    alerts.append(f"'{med['name']}' (ID: {med['id']}) expires in {(expiry_date - today).days} days.")
                if int(med.get("quantity", 0)) < 10:
                    alerts.append(f"'{med['name']}' (ID: {med['id']}) has low stock ({med['quantity']} units).")
            if alerts:
                QMessageBox.information(self, "Inventory Alerts", "\n".join(alerts))
                self.status_bar.showMessage(f"Generated alerts for {len(alerts)} issues.", 3000)
            else:
                self.status_bar.showMessage("No alerts generated.", 3000)
        except Exception as e:
            self.status_bar.showMessage(f"Error generating alerts: {str(e)}", 5000)

    def export_inventory(self):
        """Export current inventory to a CSV file"""
        if not self.user or self.user.get("role") != "admin":
            self.status_bar.showMessage("Access denied: Admin only.", 3000)
            return
        try:
            file_name, _ = QFileDialog.getSaveFileName(self, "Save Inventory Report", "inventory_report.csv", "CSV Files (*.csv)")
            if file_name:
                with open(file_name, 'w', newline='', encoding='utf-8') as csvfile:
                    fieldnames = ["id", "name", "strength", "batch_no", "expiry_date", "quantity", "unit_price", "alert_status"]
                    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                    writer.writeheader()
                    for med in self._cached_medicines:
                        writer.writerow(med)
                self.status_bar.showMessage(f"Inventory exported to {file_name}.", 3000)
        except Exception as e:
            self.status_bar.showMessage(f"Error exporting inventory: {str(e)}", 5000)

    def delete_medicine(self, med_id):
        """Delete the selected medicine with specific confirmation and signal emission"""
        if not self.user or self.user.get("role") != "admin":
            self.status_bar.showMessage("Access denied: Admin only.", 3000)
            return
        try:
            med = next((m for m in self._cached_medicines if m["id"] == med_id), None)
            if not med:
                self.status_bar.showMessage("Medicine not found.", 3000)
                return
            med_name = med["name"]
            reply = QMessageBox.question(self, "Confirm Delete", f"Are you sure you want to delete '{med_name}' (ID: {med_id})?",
                                       QMessageBox.Yes | QMessageBox.No)
            if reply == QMessageBox.Yes:
                try:
                    delete_medicine(med_id)
                    self._cached_medicines = [m for m in self._cached_medicines if m["id"] != med_id]  # Update cache
                    db_signals.medicine_updated.emit()  # Signal app-wide update
                    self.load_medicines()
                    self.status_bar.showMessage(f"Medicine '{med_name}' deleted successfully.", 3000)
                except Exception as e:
                    self.status_bar.showMessage(f"Failed to delete medicine: {str(e)}", 5000)
        except Exception as e:
            self.status_bar.showMessage(f"Error processing delete: {str(e)}", 5000)