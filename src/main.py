import sys
from PyQt5.QtWidgets import QApplication
from widgets.login_dialog import LoginDialog
from ui.main_window import MainWindow
from db import init_db

def main():
    init_db()
    app = QApplication(sys.argv)
    login = LoginDialog()
    if login.exec_() == login.Accepted:
        user = login.result
        window = MainWindow(user)
        window.show()
        app.exec_()
    # If window is closed via X, app exits. If switch account, handled inside MainWindow.

if __name__ == "__main__":
    main()