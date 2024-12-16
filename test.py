import json
import os

def convert_to_utf8(directory):
    for filename in os.listdir(directory):
        file_path = os.path.join(directory, filename)
        try:
            with open(file_path, 'r', encoding='utf-16', errors='replace') as file:
                content = file.read()
            
            with open(file_path, 'w', encoding='utf-8') as file:
                file.write(content)

        except Exception as e:
            print("Failed")

def apply_merged_settings(file_to_update, merged_settings_file):
    json_to_update = load_json(file_to_update)

    merged_json = load_json(merged_settings_file)

    if not file_to_update or not merged_json:
        print("Error: One or both files could not be loaded")
        return
    
    merged_settings = merged_json.get("settings", None)
    
    if not isinstance(merged_settings, list):
        print(f"Error 'settings' in {merged_settings_file} is not a list")

    # Updating settings in file
    json_to_update["settings"] = merged_settings
    json_to_update["settingCount"] = len(json_to_update["settings"])

    try:
        with open(file_to_update, 'w', encoding='utf-8') as file:
            json.dump(json_to_update, file, indent=4)
        print("Updated Settings")
    except Exception as e:
        print(f"Failed to update {file_to_update} : {e}")

def load_json(file_path):
    """Load JSON data from a file."""
    if not os.path.exists(file_path):
        print(f"File{file_path} does not exist.")
        return None
    try:
        with open(file_path,'r',encoding='utf-8') as file:
            raw_content = file.read()
            print(f"Raw content of {file_path}:")
            print(raw_content)
            data = json.loads(raw_content)
            print(f"Parsed JSON data from {file_path} : {data}")
            return data
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON from {file_path} : {e}")
        return None
    except Exception as e:
        print(f"Unexpected error while loading {file_path} : {e}")
        return None

def merge_and_renumber(file1,file2,output_file):
    """Merging settings lists"""
    # Load JSON files
    json1 = load_json(file1)
    json2 = load_json(file2)

    if not json1 or not json2:
        print("One or both files could not be loaded")
        return
    
    settings1 = json1.get("settings", [])
    settings2 = json2.get("settings", [])

    if not isinstance(settings1,list) or not isinstance(settings2,list):
        print("Settings attribute must be a list in both files")
        return
    
    # Merging settings and renumbering "id"
    merged_settings = settings1 + settings2
    for index, setting in enumerate(merged_settings):
        if isinstance(setting, dict):
            setting["id"] = index

    # Create a new merged JSON object
    merged_json = {
        "settings" : merged_settings
    }

    # Write the merged json to the output file
    with open(output_file, 'w',encoding='utf-8') as file:
        json.dump(merged_json, file, indent=4)
    print(f"Merged JSON saved to {output_file}")



def merge_all_settings_in_directory(directory, output_file):
    json_files = [os.path.join(directory, f) for f in os.listdir(directory) if f.endswith('.json')]

    if len(json_files) < 2:
        print("Need at least two JSON files")
        return
    
    base_file = json_files[0]
    merged_settings_file = base_file

    for next_file in json_files[1:]:
        merge_and_renumber(merged_settings_file, next_file, output_file)
        merged_settings_file = output_file


def deduplicate_settings(json_data):
    """
    Removes duplicates from the 'settings' list according to specified rules,
    asking the user which 'choiceSettingValue.value' to keep in case of conflicts
    or allowing a new, separate object to be added.
    """
    unique_settings = []

    def find_existing_setting(setting_definition_id):
        """Find an existing object in 'unique_settings' based on 'settingDefinitionId'."""
        for unique_setting in unique_settings:
            if unique_setting.get("settingInstance", {}).get("settingDefinitionId") == setting_definition_id:
                return unique_setting
        return None

    def format_settings(settings):
        """
        Formats information about settings for display to the user.
        """
        formatted = []
        for setting in settings:
            setting_id = setting.get("settingDefinitionId", "N/A")
            setting_values = [
                grandchild.get("simpleSettingValue", {}).get("value", "N/A")
                for group in setting.get("groupSettingCollectionValue", [])
                for grandchild in group.get("children", [])
            ]
            formatted.append(f"- {setting_id}: {', '.join(setting_values) if setting_values else 'No values'}")
        return "\n".join(formatted)

    def merge_children(existing_children, new_children):
        """Merge children from two lists."""
        for new_child in new_children:
            existing_child = next(
                (child for child in existing_children if child.get("settingDefinitionId") == new_child.get("settingDefinitionId")), None)
            if existing_child:
                merge_group_settings(existing_child.get("groupSettingCollectionValue", []), new_child.get("groupSettingCollectionValue", []))
            else:
                existing_children.append(new_child)

    def merge_group_settings(existing_group_settings, new_group_settings):
        """Merge 'groupSettingCollectionValue' from two lists."""
        for new_group in new_group_settings:
            existing_group = next(
                (group for group in existing_group_settings if group.get("settingDefinitionId") == new_group.get("settingDefinitionId")), None)
            if existing_group:
                merge_group_children(existing_group.get("children", []), new_group.get("children", []))
            else:
                existing_group_settings.append(new_group)

    def merge_group_children(existing_group_children, new_group_children):
        """Merge 'children' in 'groupSettingCollectionValue'."""
        for new_child in new_group_children:
            existing_child = next(
                (
                    child
                    for child in existing_group_children
                    if child.get("settingDefinitionId") == new_child.get("settingDefinitionId")
                    and child.get("simpleSettingValue", {}).get("value") == new_child.get("simpleSettingValue", {}).get("value")
                ),
                None,
            )
            if not existing_child:
                existing_group_children.append(new_child)

    for setting in json_data.get("settings", []):
        setting_instance = setting.get("settingInstance", {})
        setting_definition_id = setting_instance.get("settingDefinitionId")
        choice_value = setting_instance.get("choiceSettingValue", {}).get("value", "")
        children = setting_instance.get("choiceSettingValue", {}).get("children", [])

        existing_setting = find_existing_setting(setting_definition_id)

        if not existing_setting:
            unique_settings.append(setting)
        else:
            existing_choice_value = existing_setting.get("settingInstance", {}).get("choiceSettingValue", {}).get("value", "")
            existing_children = existing_setting.get("settingInstance", {}).get("choiceSettingValue", {}).get("children", [])

            if choice_value != existing_choice_value:
                print(f"\nDetected conflict for settingDefinitionId: {setting_definition_id}")
                print(f"Existing value: {existing_choice_value}")
                print(f"Settings of existing value:\n{format_settings(existing_children) if existing_children else 'No settings'}")
                print(f"New value: {choice_value}")
                print(f"Settings of new value:\n{format_settings(children) if children else 'No settings'}")
                print("Options:")
                print("1: Keep existing value")
                print("2: Use new value")
                print("3: Add as a new setting")
                user_choice = input("Enter 1, 2, or 3: ").strip()

                if user_choice == "2":
                    existing_setting["settingInstance"]["choiceSettingValue"]["value"] = choice_value
                    existing_setting["settingInstance"]["choiceSettingValue"]["children"] = children
                elif user_choice == "3":
                    unique_settings.append(setting)
            elif not children and not existing_children:
                continue
            else:
                merge_children(existing_children, children)

    json_data["settings"] = unique_settings
    print("\nDeduplication complete with user input.")

def renumber_settings_and_update_count(json_data):
    """
    Renumbers the 'id' field in the 'settings' list and updates 'settingsCount'.
    """
    if "settings" not in json_data:
        print("No 'settings' field found in JSON data.")
        return

    # Renumber IDs
    for index, setting in enumerate(json_data["settings"]):
        setting["id"] = index

    # Update settingsCount
    json_data["settingsCount"] = len(json_data["settings"])
    print(f"Settings renumbered and settingsCount updated to {json_data['settingsCount']}.")

# Load the input JSON file
def load_json(file_path):
    """Loads JSON from a file."""
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            return json.load(file)
    except Exception as e:
        print(f"Error loading JSON: {e}")
        return None

# Save the output JSON file
def save_json(file_path, data):
    """Saves JSON to a file."""
    try:
        with open(file_path, "w", encoding="utf-8") as file:
            json.dump(data, file, indent=4)
        print(f"JSON saved to {file_path}")
    except Exception as e:
        print(f"Error saving JSON: {e}")


""" TO ZMIENIAMY NA PLIK KTÓRY BĘDZIE NASZYM FINALNYM CONFIGIEM """
file_to_update = "Policies/becmw-confprof-std-bsl-mdm-connectivity-device-v1"

# Converting files to utf-8
convert_to_utf8("Policies")

policies_directory = "Policies"
output_file = "Policies/merged.json"

merge_all_settings_in_directory(policies_directory, output_file)

input_file = "Policies\merged.json"  # Input file path
output_file = "Policies\deduplicated_example.json"  # Output file path

    # Load input JSON
json_data = load_json(input_file)

if json_data:
    # Run the deduplication process
    deduplicate_settings(json_data)

    # Renumber IDs and update settingsCount
    renumber_settings_and_update_count(json_data)

    # Save the resulting JSON
    save_json(output_file, json_data)

apply_merged_settings(file_to_update, output_file)
