import json
import os

# Define the path to the settings file
SETTINGS_FILE_PATH = os.path.join(os.path.dirname(__file__), 'data', 'settings.json')

class ConfigService:
    def __init__(self):
        # Ensure the settings file exists
        if not os.path.exists(SETTINGS_FILE_PATH):
            self.initialize_default_settings()

    def initialize_default_settings(self):
        """Create a default settings file if it doesn't exist."""
        default_settings = {
            "monitoring_schedule": "30 minutes",
            "notification_style": "Popup",
            "popup_size": "Medium",
        }
        self.save_settings(default_settings)

    def load_settings(self):
        """Load the settings from the settings.json file."""
        with open(SETTINGS_FILE_PATH, 'r') as file:
            settings = json.load(file)
        return settings

    def save_settings(self, settings):
        """Save the given settings to the settings.json file."""
        with open(SETTINGS_FILE_PATH, 'w') as file:
            json.dump(settings, file, indent=4)

    def update_settings(self, new_settings):
        """Update specific settings in the settings.json file."""
        current_settings = self.load_settings()
        current_settings.update(new_settings)
        self.save_settings(current_settings)

