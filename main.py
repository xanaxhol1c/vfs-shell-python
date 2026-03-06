import argparse
import sys
from src.context import VFSContext
from src.engine import ExecutionEngine
from src.formatter import OutputFormatter
from src.parser import InputParser
from src.exceptions import VFSBaseException

def process_line(
    raw_line: str,
    engine: ExecutionEngine,
    parser: InputParser,
    formatter: OutputFormatter,
    line_num: int
) -> None:
    """
    Combines parsing and execution. Acts as the glue between input and logic.
    Handles custom exceptions and prevents unhandled stack traces.
    """
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

    except VFSBaseException as e:
        # Handling known application exceptions
        error_type = e.__class__.__name__
        formatted_error = f"[{error_type}] - {str(e)} at line {line_num}."
        formatter.render_error(formatted_error)
        
    except Exception as e:
        # Fallback for completely unexpected system errors to prevent crash
        error_type = e.__class__.__name__
        formatted_error = f"[Unexpected_{error_type}] - {str(e)} at line {line_num}."
        formatter.render_error(formatted_error)


def start_interactive_mode(
    engine: ExecutionEngine,
    parser: InputParser,
    formatter: OutputFormatter,
    context: VFSContext
) -> None:
    """Starts an infinite loop for user command input."""
    print("\033[94mVFS Interactive Shell (MVP)\033[0m")
    print("Type 'exit' or 'quit' to exit.\n")

    line_num = 1
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

            process_line(user_input, engine, parser, formatter, line_num)
            line_num += 1

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
                line_num = 1
                for line in f:
                    process_line(line, engine, input_parser, formatter, line_num)
                    line_num += 1
        except FileNotFoundError:
            formatter.render_error(f"[FileSystemException] - File {args.script} not found at line 0.")
    else:
        # Otherwise, we go into live mode.
        start_interactive_mode(engine, input_parser, formatter, context)


if __name__ == "__main__":
    main()
