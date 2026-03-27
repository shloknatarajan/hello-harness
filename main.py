"""Entry point — parse args, build system prompt, start the agent."""

import argparse

from dotenv import load_dotenv

load_dotenv()

from src.cli import main

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="hello-harness coding agent")
    parser.add_argument(
        "--trace", action="store_true", help="Save LLM call traces to traces/"
    )
    args = parser.parse_args()
    main(trace=args.trace)
