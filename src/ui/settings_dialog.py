from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel

class SettingsDialog(QDialog):
    def __init__(self, user=None, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Settings")
        layout = QVBoxLayout()
        layout.addWidget(QLabel("Settings Options"))
        self.setLayout(layout)