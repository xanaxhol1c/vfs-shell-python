import argparse
import sys
from src.context import VFSContext
from src.engine import ExecutionEngine
from src.formatter import OutputFormatter
from src.parser import InputParser


def process_line(
    raw_line: str, engine: ExecutionEngine, parser: InputParser, formatter: OutputFormatter
) -> None:

    line = raw_line.strip()

    # Ignore empty lines
    if not line:
        return

    # skip comments
    if line.startswith("#"):
        formatter.render_comment(line)
        return

    try:
        # parse line into command
        command = parser.parse(line)

        # pass command to engine
        if command:
            engine.execute(command, line)

    except Exception as e:
        formatter.render_error(str(e))


def start_interactive_mode(
    engine: ExecutionEngine, parser: InputParser, formatter: OutputFormatter, context: VFSContext
) -> None:
    """Запускає нескінченний цикл для інтерактивного вводу користувача."""
    print("\033[94mVFS Interactive Shell (MVP)\033[0m")
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
                sys.exit(0)

            process_line(user_input, engine, parser, formatter)

        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye!")
            break


def main() -> None:
    arg_parser = argparse.ArgumentParser(description="VFS Shell Simulator")
    arg_parser.add_argument("script", nargs="?", help="Path to script.sh (Optional)")
    args = arg_parser.parse_args()

    # Creating the core of the system
    context = VFSContext()
    formatter = OutputFormatter()
    engine = ExecutionEngine(context, formatter)
    input_parser = InputParser()

    # If the path to the script is passed, execute it
    if args.script:
        print(f"\033[93mRunning script: {args.script}\033[0m")
        try:
            with open(args.script, "r", encoding="utf-8") as f:
                for line in f:
                    process_line(line, engine, input_parser, formatter)
        except FileNotFoundError:
            formatter.render_error(f"File {args.script} not found.")
    else:
        # Otherwise, we go into live mode.
        start_interactive_mode(engine, input_parser, formatter, context)


if __name__ == "__main__":
    main()
