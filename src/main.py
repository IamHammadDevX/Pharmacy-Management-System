import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QHBoxLayout, QWidget
from widgets.login_dialog import LoginDialog
from ui.main_window import MainWindow
from db import init_db
from ui.dashboard import Dashboard

def main():
    init_db()  # Initialize database on app start
    app = QApplication(sys.argv)
    login = LoginDialog()
    if login.exec_() == login.Accepted:
        user = login.result
        window = MainWindow(user)
        window.show()
        app.exec_()

if __name__ == "__main__":
    main()