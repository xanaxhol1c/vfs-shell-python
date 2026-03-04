import argparse
import sys
from pathlib import Path
from src.context import VFSContext
from src.engine import ExecutionEngine
from src.formatter import OutputFormatter

def main():
    parser = argparse.ArgumentParser(description="VFS Shell MVP")
    parser.add_argument("script", help="Шлях до script.sh")
    args = parser.parse_args()

    # Створюємо компоненти
    context = VFSContext()
    formatter = OutputFormatter()
    engine = ExecutionEngine(context, formatter)

    script_path = Path(args.script)
    if not script_path.exists():
        print(f"❌ Помилка: Файл '{args.script}' не знайдено.")
        sys.exit(1)

    print(f"🚀 Починаємо виконання скрипту: {args.script}")
    print("-" * 50)

    try:
        with open(script_path, 'r', encoding='utf-8') as f:
            for line in f:
                engine.run(line)
    except Exception as e:
        print(f"💥 Критична помилка під час читання: {e}")

    print("-" * 50)
    print("🏁 Виконання завершено.")

if __name__ == "__main__":
    main()