"""Grep tool — searches file contents using ripgrep (rg) or falls back to grep."""

import subprocess
import shutil

SCHEMA = {
    "type": "function",
    "function": {
        "name": "grep",
        "description": "Search file contents for a regex pattern. Returns matching file paths by default, or matching lines with context.",
        "parameters": {
            "type": "object",
            "properties": {
                "pattern": {
                    "type": "string",
                    "description": "The regex pattern to search for.",
                },
                "path": {
                    "type": "string",
                    "description": "File or directory to search in. Defaults to current working directory.",
                },
                "include": {
                    "type": "string",
                    "description": "Glob pattern to filter files (e.g. '*.py', '*.ts').",
                },
                "context_lines": {
                    "type": "integer",
                    "description": "Number of context lines to show before and after each match.",
                },
                "max_results": {
                    "type": "integer",
                    "description": "Maximum number of matching lines to return. Defaults to 200.",
                },
            },
            "required": ["pattern"],
        },
    },
}


def run(
    pattern: str,
    path: str = ".",
    include: str | None = None,
    context_lines: int = 0,
    max_results: int = 200,
) -> str:
    use_rg = shutil.which("rg") is not None

    if use_rg:
        cmd = ["rg", "--no-heading", "-n", pattern]
        if include:
            cmd += ["--glob", include]
        if context_lines:
            cmd += ["-C", str(context_lines)]
        cmd += ["--max-count", str(max_results)]
        cmd.append(path)
    else:
        cmd = ["grep", "-rn", pattern]
        if include:
            cmd += ["--include", include]
        if context_lines:
            cmd += ["-C", str(context_lines)]
        cmd.append(path)

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
            return result.stdout
        if result.returncode == 1:
            return "No matches found."
        return f"Error: {result.stderr.strip()}"
    except subprocess.TimeoutExpired:
        return "Error: search timed out after 30 seconds."
    except Exception as e:
        return f"Error running grep: {e}"
