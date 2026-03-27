"""Agent loop — send messages, handle tool calls, repeat until text response."""

import json
import litellm

from src.prompt import SYSTEM_PROMPT
from src.messages import Conversation
from src.tools import get_schemas, run_tool

MODEL = "anthropic/claude-sonnet-4-20250514"


def run_agent_loop(conversation: Conversation, trace_file: str | None = None):
    trace = []
    step = 0

    while True:
        step += 1
        request_messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            *conversation.messages,
        ]
        tool_schemas = get_schemas()

        response = litellm.completion(
            model=MODEL,
            max_tokens=4096,
            messages=request_messages,
            tools=tool_schemas,
        )

        message = response.choices[0].message
        usage = response.usage

        # Record this LLM call
        entry = {
            "step": step,
            "request": {
                "model": MODEL,
                "messages": request_messages,
                "tools": tool_schemas,
            },
            "response": {
                "content": message.content,
                "tool_calls": [
                    {
                        "id": tc.id,
                        "function": tc.function.name,
                        "arguments": json.loads(tc.function.arguments),
                    }
                    for tc in (message.tool_calls or [])
                ],
            },
            "usage": {
                "prompt_tokens": usage.prompt_tokens,
                "completion_tokens": usage.completion_tokens,
                "total_tokens": usage.total_tokens,
            },
        }
        trace.append(entry)

        # Save the assistant message
        conversation.add_assistant(message)

        # Print any text content
        if message.content:
            print(message.content)

        # If no tool calls, we're done with this turn
        if not message.tool_calls:
            break

        # Execute each tool call and add results
        tool_results = []
        for tool_call in message.tool_calls:
            name = tool_call.function.name
            arguments = json.loads(tool_call.function.arguments)
            print(f"[tool: {name}({arguments})]")
            result = run_tool(name, arguments)
            conversation.add_tool_result(tool_call.id, result)
            tool_results.append(
                {
                    "tool_call_id": tool_call.id,
                    "name": name,
                    "arguments": arguments,
                    "result": result,
                }
            )

        entry["tool_executions"] = tool_results

    # Write trace to markdown
    if trace_file:
        _write_trace_markdown(trace, trace_file)

    return trace


def _write_trace_markdown(trace: list[dict], path: str):
    lines = ["# Agent Trace\n"]

    for entry in trace:
        step = entry["step"]
        lines.append(f"## Step {step}\n")

        lines.append("### Input\n")
        lines.append("```json")
        lines.append(
            json.dumps(
                {
                    "model": entry["request"]["model"],
                    "messages": entry["request"]["messages"],
                    "tools": entry["request"]["tools"],
                },
                indent=2,
            )
        )
        lines.append("```\n")

        lines.append("### Output\n")
        lines.append("```json")
        lines.append(
            json.dumps(
                {
                    "content": entry["response"]["content"],
                    "tool_calls": entry["response"]["tool_calls"],
                    "usage": entry["usage"],
                },
                indent=2,
            )
        )
        lines.append("```\n")

        lines.append("---\n")

    with open(path, "w") as f:
        f.write("\n".join(lines))
