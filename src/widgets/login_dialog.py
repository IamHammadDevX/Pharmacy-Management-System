from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QComboBox, QLineEdit, QPushButton, QHBoxLayout, QMessageBox
)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt
from db import get_user_list, validate_login

class LoginDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Login | Pharmacy Management")
        self.setFixedSize(360, 260)
        self.setStyleSheet("background: #f5f6fa;")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 32, 24, 24)
        layout.setSpacing(20)

        title = QLabel("Pharmacy Login")
        title.setFont(QFont("Arial", 18, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        # User dropdown
        user_row = QHBoxLayout()
        user_label = QLabel("👤 User:")
        user_label.setFont(QFont("Arial", 12))
        self.user_box = QComboBox()
        self.user_box.setFont(QFont("Arial", 12))
        user_row.addWidget(user_label)
        user_row.addWidget(self.user_box, 1)
        layout.addLayout(user_row)

        # Password
        pass_row = QHBoxLayout()
        pass_label = QLabel("🔒 Password:")
        pass_label.setFont(QFont("Arial", 12))
        self.pass_edit = QLineEdit()
        self.pass_edit.setFont(QFont("Arial", 12))
        self.pass_edit.setEchoMode(QLineEdit.Password)
        self.pass_edit.setPlaceholderText("Enter password")
        pass_row.addWidget(pass_label)
        pass_row.addWidget(self.pass_edit, 1)
        layout.addLayout(pass_row)

        # Login Button
        self.login_btn = QPushButton("Login →")
        self.login_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0,y1:0,x2:1,y2:0, stop:0 #43cea2, stop:1 #185a9d);
                color: white;
                border-radius: 10px;
                padding: 10px 0;
                font-size: 15px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0,y1:0,x2:1,y2:0, stop:0 #185a9d, stop:1 #43cea2);
            }
        """)
        self.login_btn.clicked.connect(self.handle_login)
        layout.addWidget(self.login_btn)

        self.result = None

        # Load users after login_btn is created for proper error handling
        self.load_users()

    def load_users(self):
        self.user_box.clear()
        try:
            users = get_user_list()
            for user in users:
                # user tuple: (username, full_name, role)
                full_name = user[1] if user[1] else user[0]
                role = user[2] if len(user) > 2 and user[2] else "user"
                display = f"{full_name} ({role.capitalize()})"
                self.user_box.addItem(display, user[0])
            if not users:
                self.user_box.addItem("No users found", "")
                self.login_btn.setEnabled(False)
        except Exception as e:
            self.user_box.addItem("DB Error", "")
            self.login_btn.setEnabled(False)

    def handle_login(self):
        username = self.user_box.currentData()
        password = self.pass_edit.text()
        if not username or not password:
            QMessageBox.warning(self, "Login Failed", "Please select user and enter password.")
            return
        try:
            user = validate_login(username, password)
            if user:
                self.result = user
                self.accept()
            else:
                QMessageBox.critical(self, "Login Failed", "Incorrect password. Please try again.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred during login:\n{str(e)}")