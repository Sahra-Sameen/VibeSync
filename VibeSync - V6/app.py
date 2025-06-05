from tray_icon.tray import BackgroundApp
import sys
from PyQt5.QtWidgets import QApplication
from main_window import MainWindow

def run_app():
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)
    main_window = MainWindow()
    window = BackgroundApp()

    try:
        with open("assets/styles.qss", "r") as f:
            app.setStyleSheet(f.read())
    except Exception as e:
        print("Error loading stylesheet:", e)

    sys.exit(app.exec_())
