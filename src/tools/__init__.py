"""Tool registry — maps tool names to callables and provides schema definitions."""

from src.tools import read_file, grep, ls

TOOLS = {
    "read_file": read_file,
    "grep": grep,
    "ls": ls,
}


def get_schemas() -> list[dict]:
    return [tool.SCHEMA for tool in TOOLS.values()]


def run_tool(name: str, arguments: dict) -> str:
    tool = TOOLS.get(name)
    if tool is None:
        return f"Error: unknown tool '{name}'"
    return tool.run(**arguments)
