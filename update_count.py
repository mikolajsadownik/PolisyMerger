def update_final_settings_count(file_path):
    """
    Updates the 'settingsCount' field in the final JSON file based on the length of the 'settings' list.
    """
    try:
        # Load JSON from the file
        with open(file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)

        # Ensure 'settings' is a list
        if "settings" in data and isinstance(data["settings"], list):
            data["settingsCount"] = len(data["settings"])
            print(f"Updated settingsCount to {data['settingsCount']} in {file_path}.")
        else:
            print("No valid 'settings' list found in the JSON file.")
            return

        # Save the updated JSON back to the file
        with open(file_path, 'w', encoding='utf-8') as file:
            json.dump(data, file, indent=4)
        print(f"Final file updated and saved to {file_path}.")
    
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON from {file_path}: {e}")
    except Exception as e:
        print(f"Error processing file {file_path}: {e}")
