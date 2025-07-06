from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel

class ProductManagement(QDialog):
    def __init__(self, user=None, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Product Management")
        layout = QVBoxLayout()
        layout.addWidget(QLabel("Manage Products Here"))
        self.setLayout(layout)