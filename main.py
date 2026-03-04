import sys
import argparse
from pathlib import Path

# Імпорти твоїх модулів (поки що уявимо, що вони є)
# from vfs.engine import ExecutionEngine
# from vfs.context import VFSContext

def main():
    # Налаштовуємо парсер аргументів командного рядка
    parser = argparse.ArgumentParser(description="VFS Shell Emulator")
    parser.add_argument("script_path", type=str, help="Path to the script file (e.g., script.sh)")
    args = parser.parse_args()

    file_path = Path(args.script_path)

    # Перевірка, чи файл існує
    if not file_path.is_file():
        print(f"Error: File '{file_path}' not found.")
        sys.exit(1)

    # Ініціалізація системи (MVP)
    # context = VFSContext()
    # engine = ExecutionEngine(context)

    # Читання та виконання
    with open(file_path, 'r', encoding='utf-8') as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            # Пропускаємо порожні рядки та коментарі
            if not line or line.startswith('#'):
                continue
            
            try:
                # engine.run(line)
                print(f"Executing [{line_num}]: {line}") # Тимчасовий прінт для тесту
            except Exception as e:
                print(f"Error on line {line_num}: {e}")

if __name__ == "__main__":
    main()