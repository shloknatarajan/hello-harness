"""Entry point — parse args, build system prompt, start the agent."""

from dotenv import load_dotenv

load_dotenv()

from src.cli import main

if __name__ == "__main__":
    main()
