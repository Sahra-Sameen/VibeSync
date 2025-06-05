from PyQt5.QtWidgets import QWidget, QHBoxLayout, QPushButton

class MenuTabs(QWidget):
    def __init__(self, on_nav_click):
        super().__init__()
        layout = QHBoxLayout()

        buttons = {
            "Dashboard": "dashboard",
            "Settings": "settings",
            "Quote": "quote",
            "Help": "help"
        }

        for label, page in buttons.items():
            btn = QPushButton(label)
            btn.clicked.connect(lambda checked, p=page: on_nav_click(p))
            layout.addWidget(btn)

        self.setLayout(layout)
