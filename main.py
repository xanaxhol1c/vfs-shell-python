import argparse
from src.context import VFSContext
from src.engine import ExecutionEngine
from src.formatter import OutputFormatter

def start_interactive_mode(engine: ExecutionEngine, context: VFSContext):
    """Запускає нескінченний цикл для введення команд користувачем."""
    print("🌟 VFS Interactive Shell (MVP)")
    print("Введіть 'exit' або 'quit' для виходу.\n")

    while True:
        try:
            # Draw an invitation (prompt) showing the current path  
            current_path = context.current_directory.get_path()
            user_input = input(f"\033[96mvfs:{current_path}$\033[0m ").strip()

            if not user_input:
                continue

            if user_input.lower() in ['exit', 'quit']:
                print("👋 До зустрічі!")
                break

            engine.run(user_input)

        except EOFError: # Processing Ctrl+D
            break
        except KeyboardInterrupt: # Processing Ctrl+C
            print("\nВикористовуйте 'exit' для виходу.")
            continue

def main():
    parser = argparse.ArgumentParser(description="VFS Shell Simulator")
    parser.add_argument("script", nargs="?", help="Шлях до script.sh (опціонально)")
    args = parser.parse_args()

    # Creating the core of the system
    context = VFSContext()
    formatter = OutputFormatter()
    engine = ExecutionEngine(context, formatter)

    # If the path to the script is passed, execute it
    if args.script:
        print(f"📂 Виконання скрипта: {args.script}")
        try:
            with open(args.script, 'r', encoding='utf-8') as f:
                for line in f:
                    engine.run(line)
        except FileNotFoundError:
            print(f"❌ Помилка: Файл {args.script} не знайдено.")
    else:
        # Otherwise, we go into live mode.
        start_interactive_mode(engine, context)

if __name__ == "__main__":
    main()