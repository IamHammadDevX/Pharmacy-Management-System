import sys
import os

# Fix module search path for PyInstaller bundle
if getattr(sys, 'frozen', False):
    # Running as a bundled .exe
    current_dir = sys._MEIPASS  # PyInstaller temp dir
else:
    # Running as a normal script
    current_dir = os.path.dirname(os.path.abspath(__file__))

sys.path.insert(0, current_dir)
sys.path.insert(0, os.path.join(current_dir, 'widgets'))
sys.path.insert(0, os.path.join(current_dir, 'ui'))

from PyQt5.QtWidgets import QApplication
from widgets.login_dialog import LoginDialog
from ui.main_window import MainWindow
from db import init_db

def main():
    init_db()  # Initialize database on app start
    app = QApplication(sys.argv)
    login = LoginDialog()
    if login.exec_() == login.Accepted:
        user = login.result
        window = MainWindow(user)
        window.show()
        sys.exit(app.exec_())

if __name__ == "__main__":
    main()
