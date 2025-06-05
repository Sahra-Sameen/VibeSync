import json
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QComboBox, QPushButton, QFrame, QLineEdit, QMessageBox)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon

class QuoteWidget(QWidget):  
    def __init__(self):
        super().__init__()
        self.setup_ui()

    def setup_ui(self):
        # Main layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 20, 30, 20)
        layout.setSpacing(20)

        # Title Label
        title = QLabel("Add Quote")
        title.setStyleSheet("font-weight: bold; font-size: 16px; margin-left:-20px;")
        # title.setFont(QFont("Helvetica", 16))
        layout.addWidget(title)

        # Motivational Quotes section (Card-like layout)
        frame = QFrame()
        frame.setStyleSheet("""
            QFrame {
                background: white;
                border-radius: 10px;
                padding: 20px;
                border: 1px solid #ddd;
            }
        """)
        frame_layout = QVBoxLayout(frame)
        frame_layout.setSpacing(15)

        # Custom Quote input area
        self.custom_quote_input = QLineEdit()
        self.custom_quote_input.setPlaceholderText("Enter your custom motivational quote...")
        self.custom_quote_input.setStyleSheet("""
            QLineEdit {
                padding: 10px;
                border-radius: 4px;
                border: 1px solid #ddd;
                min-width: 300px;
            }
        """)
        frame_layout.addWidget(self.custom_quote_input)

        # Category selection dropdown
        category_layout = QHBoxLayout()
        category_layout.addWidget(QLabel("Select Category"))
        category_layout.itemAt(0).widget().setStyleSheet("QLabel { border: none; background: transparent; font-size: 14px;}")


        self.category_combo = QComboBox()
        self.category_combo.addItems(["Happy", "Sad", "Angry", "Surprise", "Fear", "Disgust", "Neutral"])
        self.category_combo.setStyleSheet("""
            QComboBox {
                padding: 5px;
                border-radius: 4px;
                border: 1px solid #ddd;
                min-width: 150px;
            }
        """)
        category_layout.addWidget(self.category_combo)
        category_layout.addStretch()
        frame_layout.addLayout(category_layout)

        # Add Custom Quote button
        add_btn = QPushButton("Add Custom Quote")
        add_btn.setStyleSheet("""
            QPushButton {
                background: #2e7d32;
                color: white;
                border: none;
                padding: 12px 30px;
                border-radius: 4px;
                font-size: 14px;
                height: 22px;
            }
            QPushButton:hover {
                background-color: #388e3c;
            }

            QPushButton:pressed {
                background-color: #00600f;
            }
        """)
        add_btn.setFixedWidth(200)
        add_btn.clicked.connect(self.add_custom_quote)
        frame_layout.addWidget(add_btn, alignment=Qt.AlignCenter)

        layout.addWidget(frame)
        layout.addStretch()

    def add_custom_quote(self):
        """Save the custom quote to a JSON file."""
        custom_quote = self.custom_quote_input.text().strip()
        selected_category = self.category_combo.currentText().lower()

        if not custom_quote:
            self.show_message("Error", "Please enter a quote.", QMessageBox.Critical)
            return

        # Define the JSON file to store quotes
        quotes_file = "quotes.json"

        # Load existing quotes from the JSON file if it exists
        try:
            with open(quotes_file, "r") as file:
                quotes_data = json.load(file)
        except (FileNotFoundError, json.JSONDecodeError):
            quotes_data = []

        # Add the new custom quote with selected category
        quotes_data.append({"quote": custom_quote, "category": selected_category, "author": "Custom"})

        # Save updated quotes back to the JSON file
        with open(quotes_file, "w") as file:
            json.dump(quotes_data, file, indent=4)

        self.custom_quote_input.clear()
        self.show_message("Success", "Custom quote added successfully!", QMessageBox.Information)

    def show_message(self, title, message, icon):
        """Show a message box."""
        msg = QMessageBox()
        msg.setWindowTitle(title)
        msg.setWindowIcon(QIcon("assets/icon.png"))
        msg.setText(message)
        msg.setIcon(icon)
        msg.exec_()

# Example usage
if __name__ == "__main__":
    from PyQt5.QtWidgets import QApplication
    import sys
    
    app = QApplication(sys.argv)
    window = QuoteWidget()
    window.setWindowTitle("Motivational Quotes")
    window.show()
    sys.exit(app.exec_())
