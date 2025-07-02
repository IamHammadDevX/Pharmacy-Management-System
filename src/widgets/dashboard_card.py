from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt5.QtGui import QFont

class DashboardCard(QWidget):
    def __init__(self, title, value, subtitle, color="#3864fa", parent=None):
        super().__init__(parent)
        self.setFixedHeight(100)
        self.setStyleSheet(f"""
            background: white;
            border-radius: 14px;
            box-shadow: 0px 2px 10px rgba(56,100,250,0.08);
            border: 1px solid #f1f2f6;
        """)

        layout = QVBoxLayout()
        layout.setContentsMargins(18, 8, 18, 8)
        layout.setSpacing(3)

        self.title_label = QLabel(title)
        self.title_label.setFont(QFont("Segoe UI", 11, QFont.Bold))
        self.title_label.setStyleSheet("color: #4d5e80;")
        layout.addWidget(self.title_label)

        self.value_label = QLabel(str(value))
        self.value_label.setFont(QFont("Segoe UI", 24, QFont.Bold))
        self.value_label.setStyleSheet(f"color: {color}; margin-top: 5px;")
        layout.addWidget(self.value_label)

        self.subtitle_label = QLabel(subtitle)
        self.subtitle_label.setFont(QFont("Segoe UI", 9))
        self.subtitle_label.setStyleSheet("color: #8b9eb7;")
        layout.addWidget(self.subtitle_label)

        layout.addStretch()
        self.setLayout(layout)

    def set_value(self, value):
        self.value_label.setText(str(value))