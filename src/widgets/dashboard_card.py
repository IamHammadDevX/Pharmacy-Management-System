from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QSpacerItem, QSizePolicy
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt

class DashboardCard(QWidget):
    def __init__(self, title, value, subtitle, color="#3864fa", parent=None):
        super().__init__(parent)
        self.setFixedHeight(150) # Increased height to accommodate the button
        self.setStyleSheet(f"""
            background: white;
            border-radius: 14px;
            box-shadow: 0px 2px 10px rgba(56,100,250,0.08);
            border: 1px solid #f1f2f6;
        """)

        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(18, 8, 18, 8)
        self.layout.setSpacing(3)

        self.title_label = QLabel(title)
        self.title_label.setFont(QFont("Segoe UI", 11, QFont.Bold))
        self.title_label.setStyleSheet("color: #4d5e80;")
        self.layout.addWidget(self.title_label)

        self.value_label = QLabel(str(value))
        self.value_label.setFont(QFont("Segoe UI", 24, QFont.Bold))
        self.value_label.setStyleSheet(f"color: {color}; margin-top: 5px;")
        self.layout.addWidget(self.value_label)

        self.subtitle_label = QLabel(subtitle)
        self.subtitle_label.setFont(QFont("Segoe UI", 9))
        self.subtitle_label.setStyleSheet("color: #8b9eb7;")
        self.layout.addWidget(self.subtitle_label)

        # Spacer to push content to the top and button to the bottom
        self.layout.addItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))

        # This will hold the button when it's added
        self.button_container_layout = QVBoxLayout()
        self.button_container_layout.setContentsMargins(0, 0, 0, 0)
        self.layout.addLayout(self.button_container_layout)

        self.setLayout(self.layout)

    def set_value(self, value):
        """Updates the value displayed on the card."""
        self.value_label.setText(str(value))

    def add_button(self, button: QPushButton):
        """Adds a QPushButton to the bottom of the card."""
        # Style the button for consistency with the card's aesthetic
        button.setStyleSheet("""
            QPushButton {
                background-color: #f0f0f0;
                border: 1px solid #d0d0d0;
                border-radius: 5px;
                padding: 5px 10px;
                font-size: 12px;
                color: #4d5e80;
            }
            QPushButton:hover {
                background-color: #e0e0e0;
            }
            QPushButton:pressed {
                background-color: #d0d0d0;
            }
        """)
        self.button_container_layout.addWidget(button, alignment=Qt.AlignRight)