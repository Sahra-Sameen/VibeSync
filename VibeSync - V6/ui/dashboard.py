import json, os
from PyQt5.QtWidgets import (
     QWidget, QVBoxLayout, QLabel, QGridLayout,
    QGroupBox, QFrame, QSizePolicy
)
from PyQt5.QtCore import QTimer, Qt
from ui.settings import SettingsWidget
import threading
from datetime import datetime
from services.detection_loop_scheduler import EmotionScheduler
from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QFont


class DashboardWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Emotion Motivator Dashboard")
        self.setGeometry(100, 100, 800, 500)
        self.setStyleSheet("font-family: Segoe UI; font-size: 14px;")
        self.start_status = False  # False = Inactive, True = Active
        self.scheduler_thread = None
        self.is_running = False
        self.cam_thread = None
        self.scheduler = None

        self.next_trigger_timer = QTimer(self)
        self.next_trigger_timer.timeout.connect(self.update_next_trigger_time)

        # Load settings from JSON file
        self.load_settings()
        # Initialize UI
        self.initUI()

    def load_settings(self):
        try:
            with open('settings.json', 'r') as file:
                settings = json.load(file)
                self.selected_schedule = settings.get('monitoring_schedule')
                self.selected_notification_theme = settings.get('notification_theme')
                self.selected_auto_start = settings.get('auto_start')
                # print(f"Loaded settings: {self.selected_schedule}, {self.selected_notification}, {self.selected_popup_size}")
        except FileNotFoundError:
            print("Settings file not found. Using default settings.")
            self.selected_schedule = 'Hourly'
            self.selected_notification_theme = 'light'
            self.selected_auto_start = 'disable'
            # print(f"Default settings applied: {self.selected_schedule}, {self.selected_notification}, {self.selected_popup_size}")

    def initUI(self):
        self.setWindowTitle("VibeSync Dashboard")
        self.setMinimumSize(800, 600)

        self.main_layout = QVBoxLayout()
        grid = QGridLayout()
        grid.setSpacing(15)

        # Title Label
        title = QLabel("VibeSync Dashboard")
        title.setStyleSheet("font-weight: bold; font-family: 'Segoe UI'; font-size: 16px; margin-left:-20px;")
        # title.setFont(QFont("Helvetica", 24))
        self.main_layout.addWidget(title)

        def styled_group_box(title, widget):
            box = QGroupBox(title)
            layout = QVBoxLayout()
            layout.addWidget(widget)
            box.setLayout(layout)
            box.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            box.setStyleSheet("""
                QGroupBox {
                    background-color: white;
                    border: 1px solid #dcdcdc;
                    border-radius: 5px;
                    padding: 10px;
                }
                QGroupBox:title {
                    color: #000000;
                    font-weight: bold;
                    font-size: 20px;
                }
            """)
            return box
        
        # 🟢 App Status
        self.status_label = QLabel()
        self.status_layout = QVBoxLayout()
        self.status_layout.addWidget(self.status_label)
        self.status_frame = QWidget()
        self.status_frame.setLayout(self.status_layout)
        self.update_status_card()
        status_box = styled_group_box("🟢 App Status", self.status_frame)
        grid.addWidget(status_box, 0, 0)

        # 💬 Last Quote
        quote_container = QWidget()
        quote_layout = QVBoxLayout()

        # Inner box with border for the quote itself
        inner_quote_box = QFrame()
        inner_quote_box.setFrameShape(QFrame.StyledPanel)
        inner_quote_box.setStyleSheet("""
            QFrame {
                border: 1px solid #ccc;
                border-radius: 8px;
                background-color: #ffffff;
                padding: 10px;
            }
        """)

        self.quote_label = self.fetch_last_displayed_quote()
        self.quote_label.setWordWrap(True)
        self.quote_label.setAlignment(Qt.AlignCenter)
        self.quote_label.setStyleSheet("font-size: 13px; color: #333;")
        # Place the label inside the inner box
        inner_layout = QVBoxLayout()
        inner_layout.addWidget(self.quote_label)
        inner_quote_box.setLayout(inner_layout)

        # Add the inner box to the main quote section layout
        quote_layout.addWidget(inner_quote_box)
        quote_container.setLayout(quote_layout)

        # Now create the styled group box around the whole thing
        quote_box = styled_group_box("💬 Last Quote", quote_container)
        grid.addWidget(quote_box, 0, 1)

        # ⚠️ Warnings Box
        warnings_widget = self.create_disclaimer_widget()
        warnings_box = styled_group_box("⚠️ Warnings", warnings_widget)
        grid.addWidget(warnings_box, 1, 0)

        # ⚙️ Current Settings
        settings_widget = self.create_settings_display()
        settings_box = styled_group_box("⚙️ Current Settings", settings_widget)
        grid.addWidget(settings_box, 1, 1)

        # Set stretch factors for grid rows and columns for even scaling
        grid.setColumnStretch(0, 1)
        grid.setColumnStretch(1, 1)
        grid.setRowStretch(0, 1)
        grid.setRowStretch(1, 1)

        # Add grid to the main layout
        self.main_layout.addLayout(grid)
        self.setLayout(self.main_layout)

    def create_disclaimer_widget(self):
        group = QGroupBox()
        layout = QVBoxLayout()
        text = QLabel("""
        This system helps remote workers by detecting emotions and providing motivational quotes.
        • Camera access is only active when needed and disabled during video meetings.
        • User can set interval and auto start while system boots, using settings.
        • No personal data is sent externally.
        """)
        text.setWordWrap(True)
        layout.addWidget(text)
        group.setLayout(layout)
        return group

    def open_settings(self):
        self.settings_widget = SettingsWidget()
        self.settings_widget.settings_saved.connect(self.update_from_settings)
        self.settings_widget.show()

    def create_settings_display(self):
        group = QGroupBox()
        layout = QVBoxLayout()

        # Store labels as instance variables for dynamic updates
        self.schedule_label = QLabel()
        self.notification_theme_label = QLabel()
        self.auto_start_label = QLabel()
        self.next_schedule_label = QLabel()


        layout.addWidget(self.schedule_label)
        layout.addWidget(self.notification_theme_label)
        layout.addWidget(self.auto_start_label)
        layout.addWidget(self.next_schedule_label)

        group.setLayout(layout)
        self.update_settings_display()  # Set initial values
        return group

    def refresh_dashboard(self):
        print(">>> Dashboard refresh triggered")
        # Reload settings
        self.load_settings()
        
        # print("Settings after loading:", self.selected_schedule, self.selected_notification, self.selected_popup_size)
        self.update_status_card()
        self.update_settings_display()
        self.main_layout.update()  # Force the main layout to update
        self.update()

    def update_settings_display(self):
        # Update the settings labels with the new settings
        # print(f"Updating settings display with: {self.selected_schedule}, {self.selected_notification}, {self.selected_popup_size}")
        self.schedule_label.setText(f"⏱️ Interval Time: {self.selected_schedule}")
        self.notification_theme_label.setText(f"🔔 Notification Theme: {self.selected_notification_theme}")
        self.auto_start_label.setText(f"🖥️ Auto Start: {self.selected_auto_start}")
        if self.scheduler and hasattr(self.scheduler, 'get_next_trigger_time'):
            next_trigger = self.scheduler.get_next_trigger_time()
            self.next_schedule_label.setText(f"📷 Next Detection: {next_trigger}")
        else:
            self.next_schedule_label.setText("📷 Next Detection: Not scheduled yet")

        # Force the UI to update
        self.repaint()

    def toggle_functionality(self):
        self.start_status = not self.start_status
        print(f"Status : {self.start_status}")
        self.update_status_card()

        if self.start_status:
            self.is_running = True

            ## Set the global start time
            global start_time
            start_time = datetime.now()

            # Create instance of EmotionScheduler with the required functions
            self.scheduler = EmotionScheduler()
            # Start the new scheduler loop in a separate thread
            self.scheduler_thread = threading.Thread(target=self.scheduler.start_emotion_scheduler)
            self.scheduler_thread.start()

            # Start periodic updates for next trigger time
            self.next_trigger_timer.start(5000)

        else:
            self.is_running = False
            # Stop the scheduler by canceling all pending timers
            # This part requires adding a control flag in schedule_loop to check if running
            self.stop_scheduler()

            # Stop periodic updates
            self.next_trigger_timer.stop()
            self.next_schedule_label.setText("📷 Next Detection: Not scheduled yet")

    def stop_scheduler(self):
        if self.scheduler:
            self.scheduler.stop()  # Properly stop the EmotionScheduler
            print(f"[{datetime.now().strftime('%H:%M:%S')}] Scheduler stopped by user.")

    def update_status_card(self):
        print(f"Updating status: {self.start_status}")
        if self.start_status:
            # ACTIVE
            # print(f"Hi Active...")
            bg_color = "#e8f5e9"  # light green
            dot_color = "green"
            status_text = "🟢 Current Status: Active"
        else:
            # INACTIVE
            bg_color = "#fdecea"  # light red
            dot_color = "red"
            status_text = "🔴 Current Status: Inactive"

        self.status_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {bg_color};
                border: 1px solid #ccc;
                border-radius: 10px;
                padding: 12px;
            }}
            QLabel {{
                font-weight: bold;
                font-size: 14px;
                color: #333;
            }}
        """)
        self.status_label.setText(status_text)
        
        self.status_frame.update()
        self.status_frame.repaint()

    def update_from_settings(self):
        self.refresh_dashboard()

    def update_next_trigger_time(self):
        if self.scheduler and hasattr(self.scheduler, 'get_next_trigger_time'):
            next_trigger = self.scheduler.get_next_trigger_time()
            self.next_schedule_label.setText(f"📷 Next Detection: {next_trigger}")
        else:
            self.next_schedule_label.setText("📷 Next Detection: Not scheduled yet")

    def fetch_last_displayed_quote(self):
        # Define the path to the JSON file
        quote_file_path = os.path.join('data', 'last_quote.json')

        try:
            # Open the JSON file and load its content
            with open(quote_file_path, 'r') as file:
                quote_data = json.load(file)

                quote = quote_data.get('quote', 'No quote found')  # Default if 'quote' is not found

                # Format the quote (you can also include timestamp if needed)
                quote_label = QLabel(f"“{quote}”")
                return quote_label

        except Exception as e:
            print(f"Error reading the quote file: {e}")
            error_label = QLabel("Error loading the quote.")
            return error_label


