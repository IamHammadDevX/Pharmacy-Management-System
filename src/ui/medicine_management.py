from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel
from db import get_all_medicines

class MedicineManagement(QDialog):
    def __init__(self, user=None, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Medicine Management")
        layout = QVBoxLayout()
        layout.addWidget(QLabel("Manage Medicines"))
        medicines = get_all_medicines()
        if medicines:
            layout.addWidget(QLabel(f"Total Medicines: {len(medicines)}"))
        self.setLayout(layout)