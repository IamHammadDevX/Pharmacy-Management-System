from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel

class HelpSupport(QDialog):
    def __init__(self, user=None, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Help & Support")
        layout = QVBoxLayout()
        layout.addWidget(QLabel("Help & Support Content"))
        self.setLayout(layout)