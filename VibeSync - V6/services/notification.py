from windows_toasts import Toast, WindowsToaster
import logging
import textwrap

# Setup logging
logging.basicConfig(level=logging.INFO)

def show_notification(title: str, message: str):
    try:
        # Format the message to ensure line breaks for readability
        wrapped_message = "\n".join(textwrap.wrap(message, width=50))

        toaster = WindowsToaster("VibeSync")
        toast = Toast()
        toast.text_fields = [title, wrapped_message]
        toast.on_activated = lambda _: logging.info("[Notification] User clicked the toast.")
        toaster.show_toast(toast)

        logging.info(f"[Notification] {title}: {wrapped_message}")
    except Exception as e:
        logging.error(f"[Notification Error] {e}")
