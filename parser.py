import json
import os
import argparse

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

# Main execution
if __name__ == "__main__":
    # Parse arguments
    parser = argparse.ArgumentParser(description="Process JSON files in a directory.")
    parser.add_argument("--directory", required=True, help="Directory containing JSON files.")
    parser.add_argument("--output", required=True, help="Output file for merged and deduplicated settings.")
    parser.add_argument("--update_file", required=True, help="File to update with final settings.")
    args = parser.parse_args()

    # Convert files to UTF-8
    convert_to_utf8(args.directory)

    # Merge all JSON files in the directory
    merge_all_settings_in_directory(args.directory, args.output)

    # Load merged JSON
    json_data = load_json(args.output)

    if json_data:
        # Deduplicate settings
        deduplicate_settings(json_data)

        # Renumber settings
        renumber_settings(json_data)

        # Update settingsCount
        update_settings_count(json_data)

        # Save the deduplicated and renumbered JSON
        save_json(args.output, json_data)

        # Apply merged settings to the specified file
        apply_merged_settings(args.update_file, args.output)
