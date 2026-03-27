"""Read file tool — reads a file from disk and returns its contents."""

import os

SCHEMA = {
    "type": "function",
    "function": {
        "name": "read_file",
        "description": "Read a file from the local filesystem. Returns the file contents.",
        "parameters": {
            "type": "object",
            "properties": {
                "file_path": {
                    "type": "string",
                    "description": "The absolute path to the file to read.",
                },
            },
            "required": ["file_path"],
        },
    },
}


def run(file_path: str) -> str:
    if not os.path.isabs(file_path):
        return f"Error: path must be absolute, got: {file_path}"
    if not os.path.exists(file_path):
        return f"Error: file not found: {file_path}"
    if os.path.isdir(file_path):
        return f"Error: path is a directory, not a file: {file_path}"
    try:
        with open(file_path) as f:
            return f.read()
    except Exception as e:
        return f"Error reading file: {e}"
