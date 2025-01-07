import json
import os
import argparse

import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFileDialog, QListWidget, QWidget
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QDragEnterEvent, QDropEvent
import os
import json


# Your backend functions like `merge_and_renumber`, `load_json`, etc., remain the same.


class DragDropList(QListWidget):
    """Custom QListWidget to handle drag-and-drop."""
    def __init__(self, parent=None, allow_multiple=True):
        super().__init__(parent)
        self.allow_multiple = allow_multiple
        self.setAcceptDrops(True)
        self.set



def convert_to_utf8(directory):
    """Converts all files in a directory to UTF-8 encoding."""
    for filename in os.listdir(directory):
        file_path = os.path.join(directory, filename)
        try:
            with open(file_path, 'r', encoding='utf-16', errors='replace') as file:
                content = file.read()
            
            with open(file_path, 'w', encoding='utf-8') as file:
                file.write(content)

        except Exception as e:
            print(f"Failed to convert {file_path} to UTF-8: {e}")

def apply_merged_settings(file_to_update, merged_settings_file):
    """Applies merged settings to a specific file."""
    json_to_update = load_json(file_to_update)
    merged_json = load_json(merged_settings_file)

    if not json_to_update or not merged_json:
        print("Error: One or both files could not be loaded")
        return
    
    merged_settings = merged_json.get("settings", [])
    if not isinstance(merged_settings, list):
        print(f"Error: 'settings' in {merged_settings_file} is not a list.")
        return

    # Update the settings in the file
    json_to_update["settings"] = merged_settings

    try:
        with open(file_to_update, 'w', encoding='utf-8') as file:
            json.dump(json_to_update, file, indent=4)
        print(f"Updated settings in {file_to_update}")
    except Exception as e:
        print(f"Failed to update {file_to_update}: {e}")

def load_json(file_path):
    """Load JSON data from a file."""
    if not os.path.exists(file_path):
        print(f"File {file_path} does not exist.")
        return None
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return json.load(file)
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON from {file_path}: {e}")
        return None
    except Exception as e:
        print(f"Unexpected error while loading {file_path}: {e}")
        return None

def save_json(file_path, data):
    """Saves JSON data to a file."""
    try:
        with open(file_path, 'w', encoding='utf-8') as file:
            json.dump(data, file, indent=4)
        print(f"JSON saved to {file_path}")
    except Exception as e:
        print(f"Error saving JSON to {file_path}: {e}")

def merge_and_renumber(file1, file2, output_file):
    """Merges two JSON files and renumbers their settings."""
    json1 = load_json(file1)
    json2 = load_json(file2)

    if not json1 or not json2:
        print("One or both files could not be loaded.")
        return

    settings1 = json1.get("settings", [])
    settings2 = json2.get("settings", [])

    if not isinstance(settings1, list) or not isinstance(settings2, list):
        print("Settings attribute must be a list in both files.")
        return

    # Merge and renumber settings
    merged_settings = settings1 + settings2
    for index, setting in enumerate(merged_settings):
        if isinstance(setting, dict):
            setting["id"] = index

    # Create a new JSON object
    merged_json = {
        "settings": merged_settings
    }

    # Write the merged JSON to the output file
    save_json(output_file, merged_json)

def merge_all_settings_in_directory(directory, output_file):
    """Merges all JSON files in a directory."""
    json_files = [os.path.join(directory, f) for f in os.listdir(directory) if f.endswith('.json')]

    if len(json_files) < 2:
        print("Need at least two JSON files to merge.")
        return

    base_file = json_files[0]
    merged_settings_file = base_file

    for next_file in json_files[1:]:
        merge_and_renumber(merged_settings_file, next_file, output_file)
        merged_settings_file = output_file

def deduplicate_settings(json_data):
    """Removes duplicate settings based on specified rules."""
    unique_settings = []

    def find_existing_setting(setting_definition_id):
        """Find an existing setting by 'settingDefinitionId'."""
        for unique_setting in unique_settings:
            if unique_setting.get("settingInstance", {}).get("settingDefinitionId") == setting_definition_id:
                return unique_setting
        return None

    for setting in json_data.get("settings", []):
        setting_instance = setting.get("settingInstance", {})
        setting_definition_id = setting_instance.get("settingDefinitionId")

        existing_setting = find_existing_setting(setting_definition_id)

        if not existing_setting:
            unique_settings.append(setting)
        else:
            # Handle conflicts (e.g., merge children, resolve choiceSettingValue conflicts)
            pass  # Add your conflict handling logic here

    json_data["settings"] = unique_settings
    print("Deduplication complete.")

def renumber_settings(json_data):
    """Renumbers the 'id' field in the 'settings' list."""
    for index, setting in enumerate(json_data.get("settings", [])):
        setting["id"] = index
    print("Settings renumbered.")

def update_settings_count(json_data):
    """Updates the 'settingsCount' field."""
    json_data["settingsCount"] = len(json_data.get("settings", []))
    print(f"SettingsCount updated to {json_data['settingsCount']}.")


TEMP_FILE = "temp_merged.json"  # Temporary file for intermediate results


class JSONProcessorApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("JSON Processor - Unified Workflow")
        self.setGeometry(100, 100, 800, 400)
        self.init_ui()

    def init_ui(self):
        # Create the main layout
        layout = QVBoxLayout()

        # Folder and File Selection Layout
        selection_layout = QHBoxLayout()

        # Left: Folder selection for processing
        left_layout = QVBoxLayout()

        left_header = QLabel("LEFT: Folder Selection for Processing")
        left_header.setAlignment(Qt.AlignCenter)
        left_header.setStyleSheet("font-weight: bold; font-size: 14px;")
        left_layout.addWidget(left_header)

        self.folder_label = QLabel("Selected Folder: None")
        self.folder_label.setAlignment(Qt.AlignCenter)
        left_layout.addWidget(self.folder_label)

        self.browse_folder_button = QPushButton("Browse Folder")
        self.browse_folder_button.clicked.connect(self.select_folder)
        left_layout.addWidget(self.browse_folder_button)

        selection_layout.addLayout(left_layout)

        # Right: File selection for applying settings
        right_layout = QVBoxLayout()

        right_header = QLabel("RIGHT: File Selection for Applying Settings")
        right_header.setAlignment(Qt.AlignCenter)
        right_header.setStyleSheet("font-weight: bold; font-size: 14px;")
        right_layout.addWidget(right_header)

        self.file_label = QLabel("Selected File: None")
        self.file_label.setAlignment(Qt.AlignCenter)
        right_layout.addWidget(self.file_label)

        self.browse_file_button = QPushButton("Browse File")
        self.browse_file_button.clicked.connect(self.select_file)
        right_layout.addWidget(self.browse_file_button)

        selection_layout.addLayout(right_layout)

        layout.addLayout(selection_layout)

        # Unified Workflow Button
        self.start_button = QPushButton("Start Full Workflow")
        self.start_button.setStyleSheet("font-weight: bold; font-size: 14px; padding: 10px;")
        self.start_button.clicked.connect(self.start_full_workflow)
        layout.addWidget(self.start_button)

        # Create a container widget and set it as the central widget
        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        # Add a status bar for feedback
        self.statusBar().showMessage("Ready")

    def select_folder(self):
        """Handles folder selection."""
        folder = QFileDialog.getExistingDirectory(self, "Select Folder")
        if folder:
            self.folder_label.setText(f"Selected Folder: {folder}")
            self.selected_folder = folder
        else:
            self.statusBar().showMessage("No folder selected.")

    def select_file(self):
        """Handles file selection."""
        file_path, _ = QFileDialog.getOpenFileName(self, "Select File to Apply Settings", filter="JSON Files (*.json)")
        if file_path:
            self.file_label.setText(f"Selected File: {file_path}")
            self.selected_file = file_path
        else:
            self.statusBar().showMessage("No file selected.")

    def process_folder(self):
        """Processes the folder by converting, merging, deduplicating, and renumbering."""
        if hasattr(self, "selected_folder"):
            try:
                # Step 1: Convert to UTF-8
                convert_to_utf8(self.selected_folder)
                self.statusBar().showMessage("Step 1: Converted all files to UTF-8.")

                # Step 2: Merge all JSON files into the temporary file
                merge_all_settings_in_directory(self.selected_folder, TEMP_FILE)
                self.statusBar().showMessage("Step 2: Merged all settings into a temporary file.")

                # Step 3: Deduplicate settings
                json_data = load_json(TEMP_FILE)
                if json_data:
                    deduplicate_settings(json_data)
                    renumber_settings(json_data)
                    save_json(TEMP_FILE, json_data)
                    self.statusBar().showMessage("Step 3: Deduplicated and renumbered settings.")
            except Exception as e:
                self.statusBar().showMessage(f"Error during folder processing: {e}")
        else:
            self.statusBar().showMessage("Please select a folder first.")

    def process_file(self):
        """Processes the output file by applying merged settings and updating settings count."""
        if hasattr(self, "selected_file"):
            try:
                # Step 1: Convert the output file to UTF-8
                convert_to_utf8(os.path.dirname(self.selected_file))
                self.statusBar().showMessage("Step 1: Converted output file to UTF-8.")

                # Step 2: Apply merged settings
                apply_merged_settings(self.selected_file, TEMP_FILE)
                self.statusBar().showMessage("Step 2: Applied merged settings.")

                # Step 3: Update settings count
                json_data = load_json(self.selected_file)
                if json_data:
                    update_settings_count(json_data)
                    save_json(self.selected_file, json_data)
                    self.statusBar().showMessage("Step 3: Updated settings count in the output file.")
            except Exception as e:
                self.statusBar().showMessage(f"Error during file processing: {e}")
        else:
            self.statusBar().showMessage("Please select a file first.")

    def start_full_workflow(self):
        """Starts the full workflow: process folder and then process file."""
        self.statusBar().showMessage("Starting full workflow...")
        if hasattr(self, "selected_folder") and hasattr(self, "selected_file"):
            self.process_folder()
            self.process_file()
            self.statusBar().showMessage("Full workflow completed.")
        else:
            self.statusBar().showMessage("Please select both a folder and a file before starting the workflow.")


# Main Execution
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = JSONProcessorApp()
    window.show()
    sys.exit(app.exec_())