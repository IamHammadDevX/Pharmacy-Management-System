from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox, QFormLayout, QHBoxLayout, QStatusBar
from PyQt5.QtCore import Qt
from db import update_user_password, check_password, validate_login, is_strong_admin_password # Assuming update_user_password is new in db.py

class SettingsDialog(QDialog):
    def __init__(self, user=None, parent=None):
        super().__init__(parent)
        self.user = user
        if not self.user:
            QMessageBox.critical(self, "Error", "User not logged in. Cannot access settings.")
            self.reject()
            return

        self.setWindowTitle(f"Settings - {self.user.get('username', 'User')}")
        self.setMinimumSize(600, 400)

        self.setStyleSheet("""
            QDialog {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #f5f6fa, stop:1 #ffffff);
                border-radius: 12px;
            }
            QLabel#header_label {
                font-size: 28px;
                font-weight: bold;
                color: white;
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #6c5ce7, stop:1 #4834d4);
                padding: 15px;
                border-radius: 10px;
                text-align: center;
            }
            QLabel {
                font-size: 16px;
                color: #34495e;
            }
            QLineEdit {
                border: 1px solid #d0d0d0;
                border-radius: 5px;
                padding: 8px;
                font-size: 14px;
            }
            QLineEdit:focus {
                border: 1px solid #6c5ce7; /* Highlight on focus */
            }
            QPushButton {
                border-radius: 8px;
                padding: 10px 20px;
                min-width: 100px;
                font-weight: bold;
                border: none;
                color: white;
                font-size: 15px;
                background: #28a745; /* Green for Save */
                transition: background 0.3s ease;
            }
            QPushButton:hover {
                background: #218838;
            }
            QPushButton#cancel_btn {
                background: #e74c3c; /* Red for Cancel */
            }
            QPushButton#cancel_btn:hover {
                background: #c0392b;
            }
            QStatusBar {
                background: #ecf0f1;
                color: #2c3e50;
                font-size: 13px;
                border-top: 1px solid #ddd;
                border-bottom-left-radius: 12px;
                border-bottom-right-radius: 12px;
            }
        """)

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)

        header_label = QLabel("User Settings")
        header_label.setObjectName("header_label")
        main_layout.addWidget(header_label)

        form_layout = QFormLayout()
        form_layout.setSpacing(10)
        form_layout.setContentsMargins(0, 10, 0, 10)

        # Display Username
        self.username_label = QLabel(f"<b>Username:</b> {self.user.get('username', 'N/A')}")
        form_layout.addRow(self.username_label)
        
        # Display Role
        self.role_label = QLabel(f"<b>Role:</b> {self.user.get('role', 'N/A').capitalize()}")
        form_layout.addRow(self.role_label)

        # Password Change Section
        form_layout.addRow(QLabel("<b>Change Password:</b>"))
        
        self.current_password_input = QLineEdit()
        self.current_password_input.setEchoMode(QLineEdit.Password)
        self.current_password_input.setPlaceholderText("Current Password")
        form_layout.addRow("Current Password:", self.current_password_input)

        self.new_password_input = QLineEdit()
        self.new_password_input.setEchoMode(QLineEdit.Password)
        self.new_password_input.setPlaceholderText("New Password")
        form_layout.addRow("New Password:", self.new_password_input)

        self.confirm_password_input = QLineEdit()
        self.confirm_password_input.setEchoMode(QLineEdit.Password)
        self.confirm_password_input.setPlaceholderText("Confirm New Password")
        form_layout.addRow("Confirm New Password:", self.confirm_password_input)

        main_layout.addLayout(form_layout)

        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        save_btn = QPushButton("Save Changes")
        save_btn.setCursor(Qt.PointingHandCursor)
        save_btn.clicked.connect(self.save_settings)
        button_layout.addWidget(save_btn)

        cancel_btn = QPushButton("Cancel")
        cancel_btn.setObjectName("cancel_btn")
        cancel_btn.setCursor(Qt.PointingHandCursor)
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)

        main_layout.addLayout(button_layout)

        self.status_bar = QStatusBar()
        main_layout.addWidget(self.status_bar)

        self.setLayout(main_layout)

    def save_settings(self):
        """Handles saving user settings, specifically password changes."""
        current_pw = self.current_password_input.text()
        new_pw = self.new_password_input.text()
        confirm_pw = self.confirm_password_input.text()

        if not current_pw and not new_pw and not confirm_pw:
            self.status_bar.showMessage("No password changes to save.", 3000)
            return

        if new_pw or confirm_pw: # If user is trying to change password
            if not current_pw:
                self.status_bar.showMessage("Please enter your current password.", 3000)
                return
            if not new_pw:
                self.status_bar.showMessage("Please enter a new password.", 3000)
                return
            if new_pw != confirm_pw:
                self.status_bar.showMessage("New passwords do not match.", 3000)
                return
            if new_pw == current_pw:
                self.status_bar.showMessage("New password cannot be the same as current password.", 3000)
                return
            
            # Validate password strength for admin or if a strong policy is enforced for all users
            if self.user.get('role') == 'admin' or True: # Assuming strong password policy for all
                if not is_strong_admin_password(new_pw):
                    self.status_bar.showMessage("Password must be 8+ chars, include upper, lower, digit, and special char (@#$).", 7000)
                    return

            try:
                # First, verify current password
                # We can reuse validate_login to check current password without logging in again
                # This is a bit of a hack; a dedicated check_password_for_user function would be better
                # but given existing db.py, this reuses validate_login's capability.
                # It fetches user data, but we only care if it's not None (i.e., password is correct)
                if not validate_login(self.user['username'], current_pw):
                    self.status_bar.showMessage("Incorrect current password.", 3000)
                    return

                # If current password is correct, update to new password
                update_user_password(self.user['id'], new_pw)
                self.status_bar.showMessage("Password updated successfully!", 3000)
                self.current_password_input.clear()
                self.new_password_input.clear()
                self.confirm_password_input.clear()

            except ValueError as e:
                self.status_bar.showMessage(f"Error: {str(e)}", 5000)
            except Exception as e:
                self.status_bar.showMessage(f"An unexpected error occurred: {str(e)}", 5000)
        else:
            self.status_bar.showMessage("No changes detected.", 3000)

