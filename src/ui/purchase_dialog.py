from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton
from db import record_purchase, get_all_medicines

class PurchaseDialog(QDialog):
    def __init__(self, user=None, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Purchase")
        layout = QVBoxLayout()
        layout.addWidget(QLabel("Purchase a Medicine"))
        medicines = get_all_medicines()
        if medicines:
            layout.addWidget(QLabel(f"Available Medicines: {len(medicines)}"))
        btn = QPushButton("Record Purchase")
        btn.clicked.connect(self.record)
        layout.addWidget(btn)
        self.setLayout(layout)

    def record(self):
        # Placeholder: Implement medicine selection and quantity input
        record_purchase(1, 10)  # Example: Medicine ID 1, Quantity 10
        self.accept()