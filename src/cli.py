"""CLI — REPL and user input handling."""

import os
from datetime import datetime

from src.messages import Conversation
from src.agent_loop import run_agent_loop

TRACES_DIR = os.path.join(os.path.dirname(__file__), "..", "traces")


def main(trace: bool = False):
    conversation = Conversation()
    if trace:
        os.makedirs(TRACES_DIR, exist_ok=True)
        print(f"Tracing enabled → {os.path.abspath(TRACES_DIR)}/")
    print("hello-harness (type 'quit' to exit)")
    print()

    turn = 0
    while True:
        try:
            user_input = input("> ")
        except (EOFError, KeyboardInterrupt):
            print()
            break

        if user_input.strip().lower() == "quit":
            break
        if not user_input.strip():
            continue

        turn += 1
        trace_file = None
        if trace:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            trace_file = os.path.join(TRACES_DIR, f"trace_{timestamp}_turn{turn}.md")

        conversation.add_user(user_input)
        run_agent_loop(conversation, trace_file=trace_file)

        if trace_file:
            print(f"[trace saved: {trace_file}]")
        print()
