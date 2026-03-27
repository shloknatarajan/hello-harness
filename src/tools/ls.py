"""Ls tool — lists directory contents with optional glob pattern matching."""

import os
import glob as globmod

SCHEMA = {
    "type": "function",
    "function": {
        "name": "ls",
        "description": "List files and directories. Supports glob patterns (e.g. '**/*.py') for recursive file matching.",
        "parameters": {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "Directory to list or glob pattern to match (e.g. 'src/**/*.py'). Defaults to current directory.",
                },
                "recursive": {
                    "type": "boolean",
                    "description": "If true with a glob pattern, match recursively. Defaults to false.",
                },
            },
        },
    },
}


def run(path: str = ".", recursive: bool = False) -> str:
    # If path contains glob characters, use glob matching
    if any(c in path for c in ("*", "?", "[")):
        matches = sorted(globmod.glob(path, recursive=recursive))
        if not matches:
            return "No files matched the pattern."
        return "\n".join(matches)

    # Otherwise, list directory contents
    if not os.path.exists(path):
        return f"Error: path not found: {path}"
    if not os.path.isdir(path):
        return f"Error: not a directory: {path}"

    try:
        entries = sorted(os.listdir(path))
        lines = []
        for entry in entries:
            full = os.path.join(path, entry)
            suffix = "/" if os.path.isdir(full) else ""
            lines.append(f"{entry}{suffix}")
        return "\n".join(lines) if lines else "(empty directory)"
    except Exception as e:
        return f"Error listing directory: {e}"
