import json

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

# Main execution
if __name__ == "__main__":
    input_file = "example.json"  # Input file path
    output_file = "deduplicated_example.json"  # Output file path

    # Load input JSON
    json_data = load_json(input_file)

    if json_data:
        # Run the deduplication process
        deduplicate_settings(json_data)

        # Renumber IDs and update settingsCount
        renumber_settings_and_update_count(json_data)

        # Save the resulting JSON
        save_json(output_file, json_data)
