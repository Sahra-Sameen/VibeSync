import os, sys
import json
from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QComboBox,
    QFrame,
    QSpacerItem,
    QSizePolicy,
    QPushButton,
    QMessageBox,
    QHBoxLayout,
    QApplication,
)
from PyQt5.QtCore import QSize, Qt

# Define the file name to store settings
SETTINGS_FILE = "settings.json"

class SettingsWidget(QWidget):
    def __init__(self, dashboard_instance=None):
        super().__init__()
        self.dashboard_instance = dashboard_instance
        self.selected_schedule = None
        self.selected_notification_theme = None
        self.selected_popup_size = None
        self.setup_ui()
        self.load_settings()


    def setup_ui(self):
        # Main Layout
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(15, 15, 15, 15)
        self.main_layout.setSpacing(15)

        # Title Label
        title = QLabel("Application Settings")
        title.setStyleSheet("font-weight: bold;font-size:16px; margin-left: -20px;")
        # title.setFont(QFont("Helvetica", 16))
        self.main_layout.addWidget(title)

        # Settings Frame
        frame = QFrame()
        frame.setStyleSheet(
            """
            QFrame {
                background: #f9f9f9;
                border-radius: 10px;
                padding: 15px;
            }
            QLabel {
                color: #333;
                font-size: 14px;
                font-weight: bold;
            }
        """
        )
        layout = QVBoxLayout(frame)
        layout.setSpacing(10)

        # ComboBox Styles
        combo_style = """
        QComboBox {
            font-size: 14px;
            background-color: #ffffff;
            border: 1px solid #cccccc;
            border-radius: 6px;
            padding: 6px 30px 6px 12px;
            color: #333;
        }

        QComboBox:hover {
            border: 1px solid #888888;
        }

        QComboBox:focus {
            border: 1px solid #0078d7;
            outline: none;
        }

        QComboBox::drop-down {
            subcontrol-origin: padding;
            subcontrol-position: top right;
            width: 28px;
            border-left: 1px solid #ccc;
            background-color: #FFFFFF;
        }

        QComboBox::down-arrow {
            image: url("assets/dropArrow.png");
            width: 12px;
            height: 12px;
        }
        """

        # Monitoring Schedule ComboBox
        label = QLabel("Monitoring Schedule")
        label.setContentsMargins(0, 0, 0, 0)
        label.setIndent(0)
        label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        label.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Preferred)
        layout.addWidget(label)
        self.schedule_combo = QComboBox()
        self.schedule_combo.setStyleSheet(combo_style)

        # Add items with display text and corresponding minute values
        self.schedule_combo.addItems(["Every 30 seconds", "Every 1 minute", "Every 2 minutes", "Every 4 minutes", "Every 30 minutes", "Hourly", "Every 2 hours", "Every 3 hours"])
        self.schedule_combo.currentIndexChanged.connect(self.update_schedule)  # trigger on index change
        layout.addWidget(self.schedule_combo)


        # Notification Theme ComboBox
        label = QLabel("Notification Theme")
        label.setContentsMargins(0, 0, 0, 0)
        label.setIndent(0)
        label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        label.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Preferred)
        layout.addWidget(label)
        self.notify_combo = QComboBox()
        self.notify_combo.setStyleSheet(combo_style)
        self.notify_combo.addItems(["Dark", "Light"])
        self.notify_combo.currentTextChanged.connect(self.update_notification)
        layout.addWidget(self.notify_combo)

        tooltip_label = QLabel(
            "Note: Notification style follows your Windows system theme automatically."
        )
        tooltip_label.setStyleSheet("font-size: 12px; color: gray; font-style: italic;")
        layout.addWidget(tooltip_label)


        # Auto Start ComboBox
        label = QLabel("Start Detection on Boot")
        label.setContentsMargins(0, 0, 0, 0)
        label.setIndent(0)
        label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        label.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Preferred)
        layout.addWidget(label)
        self.auto_start_combo = QComboBox()
        self.auto_start_combo.setStyleSheet(combo_style)
        self.auto_start_combo.addItems(["Enable", "Disable"])
        self.auto_start_combo.currentTextChanged.connect(self.update_auto_start)
        layout.addWidget(self.auto_start_combo)

        # Save Button Style
        save_button_style = """
        QPushButton {
            background-color: #2e7d32;
            color: white;
            border: none;
            border-radius: 6px;
            padding: 12px 30px;
            font-size: 14px;
            height: 22px;
        }

        QPushButton:hover {
            background-color: #388e3c;
        }

        QPushButton:pressed {
            background-color: #00600f;
        }
        """

        # Reset Button Style
        reset_button_style = """
        QPushButton {
            background-color: #D32F2F;
            color: white;
            border: none;
            border-radius: 6px;
            padding: 12px 30px;
            font-size: 14px;
            height: 22px;
        }

        QPushButton:hover {
            background-color: #E53935;
        }

        QPushButton:pressed {
            background-color: #B71C1C;
        }
        """
        # Spacer
        spacer = QSpacerItem(20, 20, QSizePolicy.Minimum, QSizePolicy.Fixed)
        layout.addItem(spacer)

        # Save Button
        self.save_button = QPushButton("Save Settings")
        self.save_button.setStyleSheet(save_button_style)
        self.save_button.clicked.connect(self.save_settings)

        # Reset Button
        self.reset_button = QPushButton("Reset Settings")
        self.reset_button.setStyleSheet(reset_button_style)
        self.reset_button.clicked.connect(self.reset_settings)

        button_layout = QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(self.reset_button)
        button_layout.addWidget(self.save_button)
        button_layout.addStretch() 

        layout.addLayout(button_layout)

        # Spacer
        spacer = QSpacerItem(20, 20, QSizePolicy.Minimum, QSizePolicy.Expanding)
        layout.addItem(spacer)
        # Add frame to main layout
        self.main_layout.addWidget(frame)

    def save_settings(self):
        # Store current user selections
        settings = {
            "monitoring_schedule": self.schedule_combo.currentText(),
            "notification_theme": self.notify_combo.currentText(),
            "auto_start": self.auto_start_combo.currentText(),
        }

        # Print saved settings (For debugging purposes)
        # print("🔧 Settings Saved:", self.user_preferences)

        # Save these settings to a JSON file
        try:
            with open(SETTINGS_FILE, "w") as f:
                json.dump(settings, f, indent=4)
            # Trigger a confirmation message after saving
            self.show_message("Settings Saved", "Your settings have been successfully saved.")
            print("Settings successfully written to", SETTINGS_FILE)
        except Exception as e:
            print("Error writing settings:", e)

        if self.dashboard_instance:
            self.dashboard_instance.refresh_dashboard()

    
    def load_settings(self):
        if os.path.exists(SETTINGS_FILE):
            try:
                with open(SETTINGS_FILE, "r") as f:
                    saved_settings = json.load(f)
                    self.schedule_combo.setCurrentText(saved_settings.get("monitoring_schedule"))
                    self.notify_combo.setCurrentText(saved_settings.get("notification_theme"))
                    self.auto_start_combo.setCurrentText(saved_settings.get("auto_start"))
            except Exception as e:
                print("❌ Error loading settings:", e)

    def reset_settings(self):
        # Define default settings
        default_settings = {
            "monitoring_schedule": "Every 1 minute",
            "notification_theme": "Light",
            "auto_start": "Disable"
        }

        # Reset UI elements
        self.schedule_combo.setCurrentText(default_settings["monitoring_schedule"])
        self.notify_combo.setCurrentText(default_settings["notification_theme"])
        self.auto_start_combo.setCurrentText(default_settings["auto_start"])

        # Save default settings to file
        try:
            with open(SETTINGS_FILE, "w") as f:
                json.dump(default_settings, f, indent=4)
            self.show_message("Settings Reset", "All settings have been reset to default values.")
            print("✅ Settings reset to defaults.")
        except Exception as e:
            print("❌ Error resetting settings:", e)

        if self.dashboard_instance:
            self.dashboard_instance.refresh_dashboard()

    def show_message(self, title, message):
        msg = QMessageBox(self)
        msg.setWindowTitle(title)
        msg.setText(message)
        msg.setIcon(QMessageBox.Information)
        msg.exec_()

    # Handlers
    def update_schedule(self, text): self.selected_schedule = text
    def update_notification(self, text): self.selected_notification_theme = text
    def update_auto_start(self, text): self.selected_auto_start = text

    # Public Getters
    def get_selected_schedule(self): return self.selected_schedule
    def get_selected_notification(self): return self.selected_notification_theme
    def get_auto_start_preference(self): return self.selected_auto_start

    def sizeHint(self):
        return QSize(500, 400)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SettingsWidget()
    window.resize(400, 300)
    window.show()
    sys.exit(app.exec_())