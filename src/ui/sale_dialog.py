from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton
from db import record_sale, get_all_medicines

class SaleDialog(QDialog):
    def __init__(self, user=None, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Sale")
        layout = QVBoxLayout()
        layout.addWidget(QLabel("Record a Sale"))
        medicines = get_all_medicines()
        if medicines:
            layout.addWidget(QLabel(f"Available Medicines: {len(medicines)}"))
        btn = QPushButton("Record Sale")
        btn.clicked.connect(self.record)
        layout.addWidget(btn)
        self.setLayout(layout)

    def record(self):
        # Placeholder: Implement medicine selection and quantity input
        record_sale(1, 5)  # Example: Medicine ID 1, Quantity 5
        self.accept()