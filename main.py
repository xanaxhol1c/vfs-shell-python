import argparse
from src.context import VFSContext
from src.engine import ExecutionEngine
from src.formatter import OutputFormatter


def start_interactive_mode(engine: ExecutionEngine, context: VFSContext) -> None:
    """Starts an infinite loop for user command input."""
    print("VFS Interactive Shell (MVP)")
    print("Type 'exit' or 'quit' to exit.\n")

    while True:
        try:
            # Draw an invitation (prompt) showing the current path
            current_path = context.current_directory.get_path()
            user_input = input(f"\033[96mvfs:{current_path}$\033[0m ").strip()

            if not user_input:
                continue

            if user_input.lower() in ["exit", "quit"]:
                print("Goodbye!")
                break

            engine.run(user_input)

        except EOFError:  # Processing Ctrl+D
            break
        except KeyboardInterrupt:  # Processing Ctrl+C
            print("\nUse 'exit' to exit.")
            continue


def main() -> None:
    parser = argparse.ArgumentParser(description="VFS Shell Simulator")
    parser.add_argument("script", nargs="?", help="Path to script.sh (Optional)")
    args = parser.parse_args()

    # Creating the core of the system
    context = VFSContext()
    formatter = OutputFormatter()
    engine = ExecutionEngine(context, formatter)

    # If the path to the script is passed, execute it
    if args.script:
        print(f"Running script: {args.script}")
        try:
            with open(args.script, "r", encoding="utf-8") as f:
                for line in f:
                    engine.run(line)
        except FileNotFoundError:
            print(f"Error: File {args.script} not found.")
    else:
        # Otherwise, we go into live mode.
        start_interactive_mode(engine, context)


if __name__ == "__main__":
    main()
