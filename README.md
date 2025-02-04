# Intune JSON Policy Merger

A PyQt5-based GUI application designed for merging, deduplicating, and renumbering JSON configuration policies in **Microsoft Intune**. This tool simplifies working with JSON policy files, ensuring consistency and correctness.

## Features

✅ Convert JSON policy files to UTF-8 encoding  
✅ Merge multiple JSON policies from a directory  
✅ Deduplicate and renumber policy settings  
✅ Apply merged settings to a selected JSON policy  
✅ Update the `settingCount` field automatically  
✅ Drag-and-drop support for file selection  

## Usage

### 1. Select a Folder
Click **"Browse Folder"** to choose a directory containing **Microsoft Intune JSON policy files**.

### 2. Select a File
Click **"Browse File"** to choose an existing policy file where the merged settings will be applied.

### 3. Start Processing
Click **"Start Full Workflow"**, and the application will perform the following steps:

- **Convert JSON files to UTF-8** if necessary.
- **Merge all policy settings** from multiple JSON files into a temporary file.
- **Deduplicate settings** to remove redundant entries.
- **Renumber settings** to ensure proper sequence.
- **Apply merged settings** to the selected policy file.
- **Update the `settingCount` field** in the JSON policy.

### 4. Error Handling
- If an error occurs, a message will be displayed in the **status bar**.
- **Backup copies** of JSON files are automatically created before modification.

