from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton,
    QMessageBox, QHBoxLayout, QDateEdit, QDoubleSpinBox, QSpinBox, QFormLayout
)
from PyQt5.QtCore import Qt, QDate
from datetime import datetime
import db # Assuming db.py contains add_medicine, update_medicine, batch_number_exists

class AddMedicineDialog(QDialog):
    def __init__(self, parent=None, initial_data=None):
        super().__init__(parent)
        self.initial_data = initial_data # None for add, dict for edit
        self.is_edit_mode = initial_data is not None
        self.edit_id = initial_data.get("id") if initial_data else None

        if self.is_edit_mode:
            self.setWindowTitle("Edit Medicine")
        else:
            self.setWindowTitle("Add New Medicine")
        
        self.setMinimumSize(550, 600) # Increased size for better spacing

        self.setStyleSheet("""
            QDialog {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #f5f6fa, stop:1 #ffffff);
                border-radius: 12px;
            }
            QLabel {
                font-size: 16px;
                color: #34495e;
            }
            QLabel#header_label {
                font-size: 28px;
                font-weight: bold;
                color: white;
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #43cea2, stop:1 #185a9d); /* Green-blue gradient */
                padding: 15px;
                border-radius: 10px;
                text-align: center;
            }
            QLineEdit, QDateEdit, QDoubleSpinBox, QSpinBox {
                border: 1px solid #d0d0d0;
                border-radius: 5px;
                padding: 8px;
                font-size: 14px;
                background-color: white;
            }
            QLineEdit:focus, QDateEdit:focus, QDoubleSpinBox:focus, QSpinBox:focus {
                border: 1px solid #6c5ce7; /* Highlight on focus */
            }
            QDateEdit::drop-down {
                border: 0px;
                image: url(data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAAABmNLR0QA/wD/AP+gvaeTAAAAVUlEQVQ4jWNgGAWjYBSMglEwCkYBCSA+jE0gV0yVjQYg1wI+gFgYgPgfSDUaQGg+MhBqgC4g1gwMDSBVAzIKoGaAqhFkgWzUjYDRjYDRgYAIAD8mK3s6+GfXAAAAAElFTkSuQmCC); /* Calendar icon */
                width: 16px;
                height: 16px;
            }
            QSpinBox::up-button, QSpinBox::down-button,
            QDoubleSpinBox::up-button, QDoubleSpinBox::down-button {
                width: 20px;
                border: 1px solid #d0d0d0;
                border-radius: 3px;
                background-color: #f0f0f0;
            }
            QSpinBox::up-button:hover, QSpinBox::down-button:hover,
            QDoubleSpinBox::up-button:hover, QDoubleSpinBox::down-button:hover {
                background-color: #e0e0e0;
            }
            QPushButton {
                border-radius: 8px;
                padding: 10px 20px;
                min-width: 120px;
                font-weight: bold;
                border: none;
                color: white;
                font-size: 15px;
                transition: background 0.3s ease;
            }
            QPushButton#save_btn {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #28a745, stop:1 #218838); /* Green gradient */
            }
            QPushButton#save_btn:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #218838, stop:1 #28a745);
            }
            QPushButton#cancel_btn {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #e74c3c, stop:1 #c0392b); /* Red gradient */
            }
            QPushButton#cancel_btn:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #c0392b, stop:1 #e74c3c);
            }
        """)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)

        header_label = QLabel("Edit Medicine" if self.is_edit_mode else "Add New Medicine")
        header_label.setObjectName("header_label")
        main_layout.addWidget(header_label)

        form_layout = QFormLayout()
        form_layout.setSpacing(10)
        form_layout.setContentsMargins(0, 10, 0, 10)

        # Medicine Name
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("e.g., Paracetamol")
        form_layout.addRow("Medicine Name:", self.name_input)

        # Strength
        self.strength_input = QLineEdit()
        self.strength_input.setPlaceholderText("e.g., 500mg, 10mg/ml")
        form_layout.addRow("Strength (Optional):", self.strength_input)

        # Batch Number
        self.batch_no_input = QLineEdit() # Renamed from batch_input for consistency
        self.batch_no_input.setPlaceholderText("e.g., ABC12345")
        form_layout.addRow("Batch Number:", self.batch_no_input)

        # Expiry Date
        self.expiry_date_input = QDateEdit(calendarPopup=True) # Renamed from expiry_input
        self.expiry_date_input.setMinimumDate(QDate.currentDate()) # Cannot set expiry in past
        self.expiry_date_input.setDate(QDate.currentDate().addYears(1)) # Default to 1 year from now
        form_layout.addRow("Expiry Date:", self.expiry_date_input)

        # Quantity
        self.quantity_input = QSpinBox() # Changed to QSpinBox for better input control
        self.quantity_input.setMinimum(0) # Can be 0 for edit mode if stock runs out
        self.quantity_input.setMaximum(99999)
        self.quantity_input.setSingleStep(10) # Step by 10 for faster entry
        form_layout.addRow("Quantity:", self.quantity_input)

        # Unit Price
        self.unit_price_input = QDoubleSpinBox() # Changed to QDoubleSpinBox for floating point
        self.unit_price_input.setMinimum(0.01)
        self.unit_price_input.setMaximum(9999.99)
        self.unit_price_input.setPrefix("$")
        self.unit_price_input.setDecimals(2)
        self.unit_price_input.setSingleStep(0.50)
        form_layout.addRow("Unit Price:", self.unit_price_input)

        main_layout.addLayout(form_layout)

        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        self.save_btn = QPushButton("Save Medicine")
        self.save_btn.setObjectName("save_btn")
        self.save_btn.setCursor(Qt.PointingHandCursor)
        self.save_btn.clicked.connect(self.save_medicine) # Renamed to save_medicine
        button_layout.addWidget(self.save_btn)

        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.setObjectName("cancel_btn")
        self.cancel_btn.setCursor(Qt.PointingHandCursor)
        self.cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_btn)

        main_layout.addLayout(button_layout)

        # Load data if in edit mode
        if self.is_edit_mode:
            self._load_medicine_data()
            # Disable name and batch_no in edit mode to prevent changing primary identifiers
            self.name_input.setEnabled(False)
            self.batch_no_input.setEnabled(False)
            self.save_btn.setText("Update Medicine") # Change button text in edit mode


    def _load_medicine_data(self):
        """Loads existing medicine data into the form fields for editing."""
        if self.initial_data:
            self.name_input.setText(self.initial_data.get('name', ''))
            self.strength_input.setText(self.initial_data.get('strength', ''))
            self.batch_no_input.setText(self.initial_data.get('batch_no', ''))
            
            expiry_date_str = self.initial_data.get('expiry_date')
            if expiry_date_str:
                try:
                    expiry_date = QDate.fromString(expiry_date_str, "yyyy-MM-dd")
                    self.expiry_date_input.setDate(expiry_date)
                except Exception:
                    pass # Keep default date if parsing fails

            self.quantity_input.setValue(self.initial_data.get('quantity', 0))
            self.unit_price_input.setValue(self.initial_data.get('unit_price', 0.0))


    def get_data(self):
        """Returns the data from the form fields as a dictionary."""
        return {
            "name": self.name_input.text().strip(),
            "strength": self.strength_input.text().strip(),
            "batch_no": self.batch_no_input.text().strip(),
            "expiry_date": self.expiry_date_input.date().toString("yyyy-MM-dd"),
            "quantity": self.quantity_input.value(),
            "unit_price": self.unit_price_input.value()
        }

    def save_medicine(self): # Renamed from save
        """Validates input and saves/updates medicine data to the database."""
        med_data = self.get_data()

        # Basic validation
        if not med_data["name"]:
            QMessageBox.warning(self, "Input Error", "Medicine Name cannot be empty.")
            return
        if not med_data["batch_no"]:
            QMessageBox.warning(self, "Input Error", "Batch Number cannot be empty.")
            return
        # Quantity can be 0 in edit mode if stock runs out, but not negative
        if med_data["quantity"] < 0: 
            QMessageBox.warning(self, "Input Error", "Quantity cannot be negative.")
            return
        if med_data["unit_price"] <= 0:
            QMessageBox.warning(self, "Input Error", "Unit Price must be positive.")
            return
        if self.expiry_date_input.date() < QDate.currentDate():
            QMessageBox.warning(self, "Input Error", "Expiry Date cannot be in the past.")
            return

        try:
            if self.is_edit_mode:
                # In edit mode, name and batch_no are disabled, so no need to re-check existence
                db.update_medicine(self.edit_id, med_data)
                QMessageBox.information(self, "Success", f"Medicine '{med_data['name']}' updated successfully!")
            else:
                # Check if medicine with same name and batch number already exists for new additions
                if db.batch_number_exists(med_data["name"], med_data["batch_no"]):
                    QMessageBox.warning(self, "Duplicate Entry", 
                                        f"A medicine with name '{med_data['name']}' and batch number '{med_data['batch_no']}' already exists.")
                    return
                db.add_medicine(med_data)
                QMessageBox.information(self, "Success", f"New medicine '{med_data['name']}' added successfully!")
            
            self.accept() # Close dialog on success
        except Exception as e:
            QMessageBox.critical(self, "Database Error", f"Failed to save medicine:\n{str(e)}")