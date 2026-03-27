"""Agent loop — send messages, handle tool calls, repeat until text response."""

import json
import litellm

from src.prompt import SYSTEM_PROMPT
from src.messages import Conversation
from src.tools import get_schemas, run_tool

MODEL = "anthropic/claude-sonnet-4-20250514"


def run_agent_loop(conversation: Conversation):
    while True:
        response = litellm.completion(
            model=MODEL,
            max_tokens=4096,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                *conversation.messages,
            ],
            tools=get_schemas(),
        )

        message = response.choices[0].message

        # Save the assistant message
        conversation.add_assistant(message)

        # Print any text content
        if message.content:
            print(message.content)

        # If no tool calls, we're done with this turn
        if not message.tool_calls:
            break

        # Execute each tool call and add results
        for tool_call in message.tool_calls:
            name = tool_call.function.name
            arguments = json.loads(tool_call.function.arguments)
            print(f"[tool: {name}({arguments})]")
            result = run_tool(name, arguments)
            conversation.add_tool_result(tool_call.id, result)
