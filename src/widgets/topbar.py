from PyQt5.QtWidgets import QWidget, QHBoxLayout, QLabel, QLineEdit, QPushButton
from PyQt5.QtCore import Qt, pyqtSignal

class Topbar(QWidget):
    add_product_clicked = pyqtSignal()

    def __init__(self, user=None, parent=None):
        super().__init__(parent)
        self.setFixedHeight(60)
        self.setObjectName("Topbar")
        self.user = user

        layout = QHBoxLayout(self)
        layout.setContentsMargins(18, 10, 18, 10)
        layout.setSpacing(20)

        # Greeting: show user's full name (or username if not present)
        if self.user:
            name = self.user.get("full_name") or self.user.get("username", "User")
            role = self.user.get("role", "").capitalize()
            greeting = QLabel(f"Hello, {name} ({role})!")
        else:
            greeting = QLabel("Hello, User!")
        greeting.setStyleSheet("font-size: 16px; font-weight: bold;")
        layout.addWidget(greeting)
        layout.addStretch()

        self.search = QLineEdit()
        self.search.setPlaceholderText("🔍  Search anything")
        self.search.setFixedWidth(220)
        self.search.setStyleSheet("""
            QLineEdit {
                background: #f5f6fa;
                border: 1.6px solid #e1e4ea;
                border-radius: 12px;
                padding: 7px 10px 7px 34px;
                font-size: 14px;
                color: #222;
            }
            QLineEdit:focus {
                border: 1.6px solid #3864fa;
                background: #fff;
            }
        """)
        layout.addWidget(self.search)

        self.add_btn = QPushButton("🆕 Add New Product")
        self.add_btn.setCursor(Qt.PointingHandCursor)
        self.add_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #3864fa, stop:1 #4fd1c5);
                color: white;
                border-radius: 12px;
                padding: 8px 22px;
                font-size: 15px;
                font-weight: bold;
                letter-spacing: 0.5px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #4fd1c5, stop:1 #3864fa);
            }
        """)
        layout.addWidget(self.add_btn)
        self.add_btn.clicked.connect(self.add_product_clicked.emit)

        # Profile: show user's full name and email if available
        if self.user:
            profile_name = self.user.get("full_name") or self.user.get("username", "User")
            email = self.user.get("email", "No email")
            profile = QLabel(f"{profile_name}\n{email}")
        else:
            profile = QLabel("User\nuser@email")
        profile.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        profile.setStyleSheet("color: #444; font-size: 13px;")
        layout.addWidget(profile)