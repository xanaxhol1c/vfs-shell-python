import sys
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
            # Малюємо запрошення (prompt), показуючи поточний шлях
            current_path = context.current_directory.get_path()
            user_input = input(f"\033[96mvfs:{current_path}$\033[0m ").strip()

            if not user_input:
                continue

            if user_input.lower() in ['exit', 'quit']:
                print("👋 До зустрічі!")
                break

            engine.run(user_input)

        except EOFError: # Обробка Ctrl+D
            break
        except KeyboardInterrupt: # Обробка Ctrl+C
            print("\nВикористовуйте 'exit' для виходу.")
            continue

def main():
    parser = argparse.ArgumentParser(description="VFS Shell Simulator")
    parser.add_argument("script", nargs="?", help="Шлях до script.sh (опціонально)")
    args = parser.parse_args()

    # Створюємо ядро системи
    context = VFSContext()
    formatter = OutputFormatter()
    engine = ExecutionEngine(context, formatter)

    # Якщо передано шлях до скрипта — виконуємо його
    if args.script:
        print(f"📂 Виконання скрипта: {args.script}")
        try:
            with open(args.script, 'r', encoding='utf-8') as f:
                for line in f:
                    engine.run(line)
        except FileNotFoundError:
            print(f"❌ Помилка: Файл {args.script} не знайдено.")
    else:
        # Інакше — заходимо в лайв-режим
        start_interactive_mode(engine, context)

if __name__ == "__main__":
    main()