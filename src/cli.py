"""CLI — REPL and user input handling."""

from src.messages import Conversation
from src.agent_loop import run_agent_loop


def main():
    conversation = Conversation()
    print("hello-harness (type 'quit' to exit)")
    print()

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

        conversation.add_user(user_input)
        run_agent_loop(conversation)
        print()
