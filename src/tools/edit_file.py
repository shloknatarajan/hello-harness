"""Edit file tool — performs string replacements in files."""

import os

SCHEMA = {
    "type": "function",
    "function": {
        "name": "edit_file",
        "description": (
            "Perform an exact string replacement in a file. "
            "Provide old_string (the text to find) and new_string (the replacement). "
            "old_string must match exactly one location in the file. "
            "To create a new file, set old_string to an empty string and provide the full content in new_string."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "file_path": {
                    "type": "string",
                    "description": "The absolute path to the file to edit.",
                },
                "old_string": {
                    "type": "string",
                    "description": "The exact text to find and replace. Use empty string to create a new file.",
                },
                "new_string": {
                    "type": "string",
                    "description": "The text to replace old_string with.",
                },
            },
            "required": ["file_path", "old_string", "new_string"],
        },
    },
}


def run(file_path: str, old_string: str, new_string: str) -> str:
    if not os.path.isabs(file_path):
        return f"Error: path must be absolute, got: {file_path}"

    # Create new file when old_string is empty
    if old_string == "":
        if os.path.exists(file_path):
            return f"Error: file already exists: {file_path}. Use a non-empty old_string to edit it."
        try:
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            with open(file_path, "w") as f:
                f.write(new_string)
            return f"Created {file_path}"
        except Exception as e:
            return f"Error creating file: {e}"

    # Edit existing file
    if not os.path.exists(file_path):
        return f"Error: file not found: {file_path}"
    if os.path.isdir(file_path):
        return f"Error: path is a directory, not a file: {file_path}"

    try:
        with open(file_path) as f:
            content = f.read()
    except Exception as e:
        return f"Error reading file: {e}"

    count = content.count(old_string)
    if count == 0:
        return "Error: old_string not found in file."
    if count > 1:
        return f"Error: old_string appears {count} times. Provide more context to make it unique."

    new_content = content.replace(old_string, new_string, 1)
    try:
        with open(file_path, "w") as f:
            f.write(new_content)
    except Exception as e:
        return f"Error writing file: {e}"

    return f"Edited {file_path}"
