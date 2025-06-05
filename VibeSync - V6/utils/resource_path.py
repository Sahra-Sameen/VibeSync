import sys
import os

def resource_path(relative_path):
    """
    Return an absolute path to a resource, whether running in dev (python)
    or inside a PyInstaller‐bundled onefile executable.

    - When PyInstaller runs, it extracts everything into a temp folder, _MEIPASS.
    - Otherwise, we compute paths relative to the location of this script (utils/).
    """
    # If running as a onefile PyInstaller exe, _MEIPASS is where it unpacks.
    if hasattr(sys, "_MEIPASS"):
        base_path = sys._MEIPASS
    else:
        # __file__ is utils/resource_path.py → go up one level to emotion_app/
        base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    return os.path.join(base_path, relative_path)
