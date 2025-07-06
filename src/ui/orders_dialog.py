from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel

class OrdersDialog(QDialog):
    def __init__(self, user=None, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Orders")
        layout = QVBoxLayout()
        layout.addWidget(QLabel("Manage Orders"))
        self.setLayout(layout)