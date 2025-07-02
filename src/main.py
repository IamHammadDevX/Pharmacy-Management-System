import sys
from PyQt5.QtWidgets import QApplication
from widgets.login_dialog import LoginDialog
from ui.main_window import MainWindow
from db import init_db

if __name__ == "__main__":
    init_db()
    app = QApplication(sys.argv)
    login = LoginDialog()
    if login.exec_() == login.Accepted:
        user = login.result
        window = MainWindow(user)  # Pass user dict
        window.show()
        sys.exit(app.exec_())