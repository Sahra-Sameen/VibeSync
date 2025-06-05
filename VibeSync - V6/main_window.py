from PyQt5.QtWidgets import QMainWindow, QWidget, QLabel, QHBoxLayout, QVBoxLayout, QPushButton, QStackedWidget
from PyQt5.QtCore import Qt
from ui.dashboard import DashboardWidget
from ui.settings import SettingsWidget
from ui.quote_page import QuoteWidget  
from ui.help import HelpWidget
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QSize
import sys
from PyQt5.QtWidgets import QApplication

import sys
import os
from utils.resource_path import resource_path

class MainWindow(QMainWindow):
    def __init__(self, dashboard_widget=None):
        super().__init__()
        self.setWindowTitle("VibeSync")
        self.setWindowIcon(QIcon(resource_path("assets/icon.png")))
        self.setGeometry(100, 100, 1000, 700)

        # Central widget
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        # self.central_widget.setStyleSheet("background-color: #f4f3f2;")

        # Main layout
        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(10, 10, 10, 10)  # Add some padding around whole window
        self.layout.setSpacing(5)  
        self.central_widget.setLayout(self.layout)

        if dashboard_widget is None:
            self.dashboard_page = DashboardWidget()
        else:
            self.dashboard_page = dashboard_widget

        # Initialize the header, menu, and pages
        self.init_header()
        self.init_menu()
        self.init_pages()

    def init_header(self):
        # Header layout
        header = QHBoxLayout()
        header.setContentsMargins(0, 0, 0, 0)
        header.setSpacing(10)

        # App label
        app_label = QLabel("VibeSync")
        app_label.setStyleSheet("font-weight: bold; font-size: 24px;")
        header.addWidget(app_label)

        header.addStretch()

        # Add top-right icons (notification, help, settings buttons)
        # Notification button
        notif_btn = QPushButton()
        notif_btn.setIcon(QIcon(resource_path("assets/bell.png")))  # Replace with your monochrome bell icon path
        notif_btn.setIconSize(QSize(20, 20))
        notif_btn.setFlat(True)  # Optional: removes button border
        header.addWidget(notif_btn)

        # Dark/Light Mode toggle button
        theme_btn = QPushButton()
        theme_btn.setIcon(QIcon(resource_path("assets/theme.png")))  # Replace with a sun/moon or toggle icon
        theme_btn.setIconSize(QSize(20, 20))
        theme_btn.setFlat(True)
        header.addWidget(theme_btn)

        # Settings button
        settings_btn = QPushButton()
        settings_btn.setIcon(QIcon(resource_path("assets/settings.png")))  # Replace with gear icon path
        settings_btn.setIconSize(QSize(20, 20))
        settings_btn.setFlat(True)
        header.addWidget(settings_btn)

        self.layout.addLayout(header)

    def init_menu(self):
        # Menu layout
        menu = QHBoxLayout()
        menu.setContentsMargins(0, 0, 0, 0)
        menu.setSpacing(10)

        # Menu buttons for navigation
        self.dashboard_btn = QPushButton("Dashboard")
        self.settings_btn = QPushButton("Settings")
        self.quote_btn = QPushButton("Quotes")
        self.help_btn = QPushButton("Help")

        for btn in [self.dashboard_btn, self.settings_btn, self.quote_btn, self.help_btn]:
            btn.setCheckable(True)
            btn.clicked.connect(self.handle_menu_click)

            btn.setStyleSheet("""
                QPushButton {
                    background-color: #f0f0f0;
                    border: none;
                    padding: 8px 16px;
                    font-size: 14px;
                }
                QPushButton:hover {
                    background-color: #9E9E9E;  /* Light purple hover */
                }
                QPushButton:checked {
                    background-color: #000000;  /* Darker color for active */
                    color: white;
                    font-weight: bold;
                }
            """)

            menu.addWidget(btn)

        self.layout.addLayout(menu)

    def init_pages(self):
        # Stacked widget to display pages
        self.stack = QStackedWidget()
        self.stack.setContentsMargins(0, 0, 0, 0)

        self.settings_page = SettingsWidget(self.dashboard_page)
        self.quote_page = QuoteWidget()
        self.help_page = HelpWidget()

        # Add pages to the stack
        self.stack.addWidget(self.dashboard_page)
        self.stack.addWidget(self.settings_page)
        self.stack.addWidget(self.quote_page)
        self.stack.addWidget(self.help_page)

        # Add stacked widget to the layout
        self.layout.addWidget(self.stack)

        # Set default page (Dashboard)
        self.dashboard_btn.setChecked(True)
        self.stack.setCurrentIndex(0)

    def handle_menu_click(self):
        # Deselect all buttons
        sender = self.sender()
        self.dashboard_btn.setChecked(False)
        self.settings_btn.setChecked(False)
        self.quote_btn.setChecked(False)
        self.help_btn.setChecked(False)

        # Highlight the selected button
        sender.setChecked(True)

        # Navigate to the selected page
        if sender == self.dashboard_btn:
            self.stack.setCurrentWidget(self.dashboard_page)
        elif sender == self.settings_btn:
            self.stack.setCurrentWidget(self.settings_page)
        elif sender == self.quote_btn:
            self.stack.setCurrentWidget(self.quote_page)
        elif sender == self.help_btn:
            self.stack.setCurrentWidget(self.help_page)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())