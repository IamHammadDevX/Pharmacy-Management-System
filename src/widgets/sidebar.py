from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel, QSizePolicy
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt

class Sidebar(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedWidth(200)
        self.setObjectName("Sidebar")

        layout = QVBoxLayout()
        layout.setContentsMargins(10, 20, 10, 10)
        layout.setSpacing(15)

        # App/Logo label
        app_label = QLabel("Phermo")
        app_label.setStyleSheet("font-weight: bold; font-size: 22px; margin-bottom: 40px;")
        layout.addWidget(app_label)

        # Navigation buttons (icons can be added)
        buttons = [
            ("Dashboard", "🏠"),
            ("Purchase", "🛒"),
            ("Sale", "💵"),
            ("Product", "💊"),
            ("Suppliers", "🏭"),
            ("Customer", "👤"),
            ("Medicine", "🧪"),
            ("Invoice", "🧾"),
            ("Orders", "📦"),
            ("Sales Report", "📈"),
            ("Help & Support", "❓"),
            ("Settings", "⚙️"),
        ]
        for text, icon in buttons:
            btn = QPushButton(f"{icon}  {text}")
            btn.setStyleSheet("text-align: left; padding: 8px 12px; border-radius: 8px;")
            btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
            btn.setCursor(Qt.PointingHandCursor)
            layout.addWidget(btn)

        layout.addStretch()
        self.setLayout(layout)