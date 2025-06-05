import json, sys
import os
from PyQt5.QtWidgets import (
    QApplication, QSystemTrayIcon, QMenu, QAction, QWidget, QLabel, QVBoxLayout
)
from PyQt5.QtGui import QIcon, QCursor
from PyQt5.QtCore import Qt
from services.detection_loop_scheduler import EmotionScheduler
from main_window import MainWindow
from ui.dashboard import DashboardWidget
from utils.resource_path import resource_path

icon_path = resource_path("assets/icon.png")


class BackgroundApp(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("VibeSync App")
        self.setGeometry(300, 300, 300, 100)

        layout = QVBoxLayout()
        self.label = QLabel("Status: Stopped")
        layout.addWidget(self.label)
        self.setLayout(layout)
        self.scheduler = EmotionScheduler()
        self.dashboard = DashboardWidget()
        self.main_window = None

        self.create_tray_icon()
        self.auto_start_status = self.load_settings()

        # 🔁 Auto-start logic
        if self.auto_start_status:
            print("[INFO] Auto-start is enabled. Starting detection...")
            self.toggle_from_tray()
        else:
            print("[INFO] Auto-start is disabled. Waiting for manual start.")

    def load_settings(self):
        with open("settings.json") as f:
            settings = json.load(f)
        # Extract auto_start_detection setting
        self.auto_start_value = settings.get("auto_start", "disable")
        print(f"[DEBUG] Auto-start detection enabled: {self.auto_start_value}")
        return self.if_auto_start_enabled(self.auto_start_value)
    
    def if_auto_start_enabled(self, auto_start_value):
        auto_start_value = auto_start_value.lower().strip()
        if auto_start_value == "enable":
            return True
        else:
            return False

    def create_tray_icon(self):
        icon_path = os.path.join(os.path.dirname(__file__), "..", "assets", "icon.png")
        self.tray_icon = QSystemTrayIcon(QIcon(icon_path), parent=self)
        self.tray_icon.setToolTip("🟢 VibeSync Running" if self.dashboard.start_status else "🔴 VibeSync Paused")

        self.menu = QMenu()

        # Toggle Start/Pause
        self.toggle_action = QAction("Start")
        self.toggle_action.triggered.connect(self.toggle_from_tray)
        self.menu.addAction(self.toggle_action)

        # View app window
        self.view_action = QAction("View App")
        self.view_action.triggered.connect(self.view_app_menu)
        self.menu.addAction(self.view_action)

        # Quit
        self.quit_action = QAction("Quit")
        self.quit_action.triggered.connect(self.quit_app)
        self.menu.addAction(self.quit_action)

        print("[DEBUG] Tray icon menu is set up.")
        self.tray_icon.activated.connect(self.on_tray_icon_activated)
        self.tray_icon.show()

    def toggle_from_tray(self):
        print("[DEBUG] Toggled from tray.")
        self.dashboard.toggle_functionality()

        # Update tray label and tooltip to stay in sync with dashboard state
        if self.dashboard.start_status:
            self.toggle_action.setText("Pause")
            self.tray_icon.setToolTip("🟢 VibeSync Running")   
        else:
            self.toggle_action.setText("Start")
            self.tray_icon.setToolTip("🔴 VibeSync Paused")

    def view_app_menu(self):
        if self.main_window is None:
            self.main_window = MainWindow(dashboard_widget=self.dashboard)  # pass existing dashboard instance

        self.main_window.showNormal()
        self.main_window.activateWindow()
        self.main_window.raise_()


    def quit_app(self):
        print("[DEBUG] Quitting app...")
        self.scheduler.stop()
        self.dashboard.start_status = True
        self.dashboard.toggle_functionality()
        self.tray_icon.hide()  # ✅ Hide the tray icon before quitting
        QApplication.quit()

    def on_tray_icon_activated(self, reason):
        # Reasons: https://doc.qt.io/qt-5/qsystemtrayicon.html#ActivationReason-enum
        if reason == QSystemTrayIcon.Trigger:  # Left click
            print("[DEBUG] Tray icon left-clicked.")
            # Show the menu on left-click as well, or toggle theme directly
            # To show menu:
            self.menu.exec_(QCursor.pos())  # Show menu at cursor position

            # OR to toggle functionality directly on left click, comment above line and uncomment:
            # self.toggle_from_tray()

        elif reason == QSystemTrayIcon.Context:  # Right click
            print("[DEBUG] Tray icon right-clicked.")
            # Default context menu is shown automatically, but you can force it:
            self.menu.exec_(QCursor.pos())




