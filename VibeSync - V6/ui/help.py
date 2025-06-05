from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QLabel, 
                            QPushButton,QHBoxLayout, QFrame, QDialog, QDialogButtonBox)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QIcon
import os
from PyQt5.QtWidgets import QTextEdit
from utils.resource_path import resource_path

class HelpPopup(QDialog):
    def __init__(self, title, content, parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setWindowIcon(QIcon(resource_path("assets/icon.png")))
        self.setFixedSize(500, 400)
        self.setWindowModality(Qt.ApplicationModal)
        self.setStyleSheet("""
            QDialog {
                background-color: #ffffff;
                border-radius: 14px;
                padding: 20px;
            }
            QTextEdit {
                color: #2c3e50;
                font-size: 14px;
                padding: 10px;
                border: none;
                background: #fff;
            }
            QPushButton#closeButton {
                background-color: #F44336;
                color: white;
                padding: 12px 25px;
                font-size: 13px;
                border: 3px solid #424242;
                font-weight: bold;
                border-radius: 10px;
            }
            QPushButton#closeButton:hover {
                background-color: #D32F2F;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(25, 25, 25, 25)
        layout.setSpacing(20)

        content_edit = QTextEdit()
        content_edit.setReadOnly(True)
        content_edit.setText(content)
        content_edit.setFont(QFont("Segoe UI", 10))
        layout.addWidget(content_edit)

        button_layout = QHBoxLayout()
        button_layout.addStretch()

        close_btn = QPushButton("Close")
        close_btn.setObjectName("closeButton")
        close_btn.clicked.connect(self.close)

        button_layout.addWidget(close_btn)
        layout.addLayout(button_layout)

        # Escape key to close
        from PyQt5.QtGui import QKeySequence
        from PyQt5.QtWidgets import QShortcut
        shortcut = QShortcut(QKeySequence("Escape"), self)
        shortcut.activated.connect(self.close)

class HelpWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setup_ui()

    def setup_ui(self):
        # Main layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 20, 30, 20)
        layout.setSpacing(20)

        # Help & Support section
        frame = QFrame()
        frame.setStyleSheet("""
            QFrame {
                background: white;
                border-radius: 10px;
                padding: 20px;
            }
        """)
        frame_layout = QVBoxLayout(frame)
        frame_layout.setSpacing(15)

        # Section title
        title = QLabel("")
        # Title Label
        title = QLabel("Help & Support")
        title.setStyleSheet("font-weight: bold; font-size:16px; margin-left:-20px;")
        # title.setFont(QFont("Helvetica", 16))
        layout.addWidget(title)

        # Help card frame
        frame = QFrame()
        frame.setStyleSheet("""
            QFrame {
                background: white;
                border-radius: 10px;
                padding: 20px;
            }
        """)
        frame_layout = QVBoxLayout(frame)
        frame_layout.setSpacing(15)

        # Help buttons
        buttons = [
            ("FAQs", self.show_faqs),
            ("Contact Support", self.contact_support),
            ("Tutorials", self.show_tutorials)
        ]

        for text, callback in buttons:
            btn = QPushButton(text)
            btn.setStyleSheet("""
                QPushButton {
                    background: #f8f9fa;
                    color: #2c3e50;
                    border: 1px solid #ddd;
                    padding: 12px 20px;
                    border-radius: 6px;
                    text-align: left;
                    font-size: 14px;
                }
                QPushButton:hover {
                    background: #e9ecef;
                }
            """)
            btn.clicked.connect(callback)
            frame_layout.addWidget(btn)

        layout.addWidget(frame)
        layout.addStretch()

    def show_faqs(self):
        content = (
            "Q: How do I get started with VibeSync?\n"
            "A: Simply launch the application and follow the step-by-step instructions displayed on the welcome screen.\n\n"
            "Q: Can I add or customize the motivational quotes?\n"
            "A: Yes, you can add your own quotes by navigating to the \"Quotes\" section and selecting the \"Add New Quote\" option.\n\n"
            "Q: How does the emotion detection feature work?\n"
            "A: The app analyzes your facial expressions using your webcam and adjusts the displayed motivational quotes accordingly.\n\n"
            "Q: Is my data stored securely?\n"
            "A: Absolutely. All your personal data and preferences are stored locally and are not shared with any third parties.\n\n"
            "Q: What should I do if the emotion detection is not working correctly?\n"
            "A: Ensure your webcam is properly connected and has granted the app permission to access it. Restart the app if necessary.\n\n"
            "Q: How can I contact customer support?\n"
            "A: You can reach out to our support team via the \"Contact Support\" button in the Help section or email us at support@vibesync.com.\n\n"
            "Q: Are there tutorials available for learning how to use VibeSync?\n"
            "A: Yes, comprehensive tutorials can be accessed by clicking the \"Tutorials\" button in the Help section."
        )
        HelpPopup("FAQs", content, self).exec_()

    def contact_support(self):
        content = """
        <div style='font-family: Segoe UI; font-size: 16px; color: #333; line-height: 1.6; text-align: center;'>
            <p><b>You can reach us at:</b></p>
            <p>📧 <span style="font-weight: 600;">Email:</span> 
            <a href='mailto:support@vibesync.com' style='color: #1565c0; text-decoration: none;'>support@vibesync.com</a></p>

            <p>📞 <span style="font-weight: 600;">Phone:</span> 
            <span style="color: #444;">+1-234-567-890</span></p>

            <p>🌐 <span style="font-weight: 600;">Website:</span> 
            <a href='http://www.vibesync.com/support' style='color: #1565c0; text-decoration: none;'>vibesync.com/support</a></p>
        </div>
        """
        HelpPopup("Contact Support", content, self).exec_()

    def show_tutorials(self):
        content = """
        <div style='font-family: Segoe UI; font-size: 16px; color: #333; text-align: center; line-height: 1.8;'>
            <p><b>Available Tutorials:</b></p>
            <ol style='margin: 0 auto; padding: 0; list-style-position: inside; text-align: left; display: inline-block;'>
                <li>Getting Started with VibeSync</li>
                <li>Adding Custom Quotes</li>
                <li>Managing Your Profile</li>
                <li>Understanding Emotion Detection</li>
            </ol>
        </div>
        """
        HelpPopup("Tutorials", content, self).exec_()

# Example usage:
if __name__ == "__main__":
    from PyQt5.QtWidgets import QApplication
    import sys
    
    app = QApplication(sys.argv)
    window = HelpWidget()
    window.setWindowTitle("VibeSync Help")
    window.resize(500, 400)
    window.show()
    sys.exit(app.exec_())