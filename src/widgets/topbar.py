from PyQt5.QtWidgets import QWidget, QHBoxLayout, QLabel, QPushButton, QSizePolicy, QSpacerItem
from PyQt5.QtCore import Qt, pyqtSignal, QTimer
from datetime import datetime

class Topbar(QWidget):
    add_product_clicked = pyqtSignal()
    logout_clicked = pyqtSignal()

    def __init__(self, user, parent=None):
        super().__init__(parent)
        self.user = user

        self.setStyleSheet("""
            background: #f5f6fa;
            border-bottom: 1px solid #e0e0e0;
        """)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Greeting & time/date label in a card-like look
        self.greeting_card = QWidget()
        self.greeting_card.setStyleSheet("""
            background: #fff;
            border-radius: 9px;
            margin-top: 14px;
            margin-bottom: 14px;
            padding: 5px 22px 5px 18px;
            box-shadow: 0 2px 12px rgba(24,90,157,.09);
        """)
        card_layout = QHBoxLayout(self.greeting_card)
        card_layout.setContentsMargins(0, 0, 0, 0)
        card_layout.setSpacing(8)

        self.greeting_label = QLabel()
        self.greeting_label.setStyleSheet("""
            QLabel {
                color: #1565c0;
                font-size: 20px;
                font-weight: bold;
            }
        """)
        card_layout.addWidget(self.greeting_label)

        self.datetime_label = QLabel()
        self.datetime_label.setStyleSheet("""
            QLabel {
                color: #444;
                font-size: 14px;
                font-weight: 500;
            }
        """)
        card_layout.addWidget(self.datetime_label)
        layout.addWidget(self.greeting_card)

        # Update greeting and time right away and every 30 seconds
        self.update_greeting_and_time()
        timer = QTimer(self)
        timer.timeout.connect(self.update_greeting_and_time)
        timer.start(30000)  # 30 seconds

        layout.addItem(QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum))

        # Add Product (admin only)
        self.add_product_btn = QPushButton("  Add Product")
        self.add_product_btn.setCursor(Qt.PointingHandCursor)
        self.add_product_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #43cea2, stop:1 #185a9d);
                color: white;
                border-radius: 8px;
                padding: 7px 24px 7px 14px;
                font-weight: bold;
                font-size: 16px;
                border: none;
                margin-right: 12px;
                letter-spacing: 0.5px;
                box-shadow: 0 2px 8px rgba(24, 90, 157, .08);
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #185a9d, stop:1 #43cea2);
                color: #fff;
            }
        """)
        self.add_product_btn.setText("⎚ Add Product")
        self.add_product_btn.clicked.connect(self.add_product_clicked.emit)
        if user['role'] != 'admin':
            self.add_product_btn.hide()
        layout.addWidget(self.add_product_btn)

        # Switch Account / Logout
        self.logout_btn = QPushButton("  Switch Account")
        self.logout_btn.setCursor(Qt.PointingHandCursor)
        self.logout_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #ff9966, stop:1 #ff5e62);
                color: white;
                border-radius: 8px;
                padding: 7px 24px 7px 14px;
                font-weight: bold;
                font-size: 16px;
                border: none;
                margin-left: 8px;
                letter-spacing: 0.5px;
                box-shadow: 0 2px 8px rgba(255, 94, 98, .08);
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #ff5e62, stop:1 #ff9966);
                color: #fff;
            }
        """)
        self.logout_btn.setText("🦄 Switch Account")
        self.logout_btn.clicked.connect(self.logout_clicked.emit)
        layout.addWidget(self.logout_btn)

    def update_greeting_and_time(self):
        now = datetime.now()
        hour = now.hour

        if 5 <= hour < 12:
            greet = "Good morning"
        elif 12 <= hour < 17:
            greet = "Good afternoon"
        elif 17 <= hour < 21:
            greet = "Good evening"
        else:
            greet = "Good night"

        # Show one role/name (not "Receptionist Receptionist One") and use a modern emoji
        if self.user["role"] == "admin":
            role_icon = "🛡️"
            role_label = "Admin"
        else:
            role_icon = "🧑"
            role_label = "Receptionist"

        # Remove double role name: only show full_name if it's not a duplicate of role
        name = self.user.get("full_name", "").strip()
        # Remove extra whitespace and compare lowercased
        if name.lower() == role_label.lower():
            display = f"{role_icon} {role_label}"
        elif name.lower().startswith(role_label.lower()):
            # For 'Receptionist One' or 'Receptionist Sarah'
            display = f"{role_icon} {name}"
        else:
            display = f"{role_icon} {role_label} {name}" if name else f"{role_icon} {role_label}"

        # Greeting with icon and bold blue
        self.greeting_label.setText(
            f"<span style='color:#1565c0; font-size:20px; font-weight:700;'>"
            f"{greet}, {display}!</span>"
        )
        date_str = now.strftime("%A, %d %b %Y")
        time_str = now.strftime("%I:%M %p")
        self.datetime_label.setText(
            f"<span style='color:#444;'>{date_str}, {time_str}</span>"
        )