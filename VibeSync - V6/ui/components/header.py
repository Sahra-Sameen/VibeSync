from PyQt5.QtWidgets import QWidget, QLabel, QHBoxLayout, QPushButton
from PyQt5.QtGui import QIcon

class Header(QWidget):
    def __init__(self):
        super().__init__()
        layout = QHBoxLayout()

        app_name = QLabel("VibeSync")
        app_name.setStyleSheet("font-weight: bold; font-size: 18px;")

        # Right-side icons
        minimize_btn = QPushButton()
        minimize_btn.setIcon(QIcon("assets/images/minimize.png"))
        close_btn = QPushButton()
        close_btn.setIcon(QIcon("assets/images/close.png"))

        layout.addWidget(app_name)
        layout.addStretch()
        layout.addWidget(minimize_btn)
        layout.addWidget(close_btn)

        self.setLayout(layout)
