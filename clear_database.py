import sqlite3
import os
import shutil
from datetime import datetime

DB_PATH = "database.db"
BACKUP_DIR = "backups"


def get_confirmation(prompt):
    while True:
        user_input = input(f"{prompt} (y / n or Enter): ").strip().lower()
        if user_input in ("y", "n", ""):
            return user_input


def main():
    print("=" * 50)
    print("Очистка базы данных SQLite")
    print("=" * 50)

    if not os.path.exists(DB_PATH):
        print(f"ОШИБКА: База данных {DB_PATH} не найдена!")
        input("\nНажмите Enter для выхода...")
        return

    confirmation = get_confirmation("Действительно ли вы хотите очистить базу данных")
    if confirmation != "y":
        print("Операция отменена пользователем.")
        input("\nНажмите Enter для выхода...")
        return

    print("\n" + "-" * 50)

    keep_employees = get_confirmation(
        "Хотите ли вы очистить таблицу с сотрудниками (employees)"
    )
    if keep_employees == "n" or keep_employees == "":
        keep_employees = True
    else:
        keep_employees = False

    print("\n" + "-" * 50)

    keep_stop_words = get_confirmation(
        "Хотите ли вы очистить таблицу со стоп-словами (stop_words)"
    )
    if keep_stop_words == "n" or keep_stop_words == "":
        keep_stop_words = True
    else:
        keep_stop_words = False

    print("\n" + "-" * 50)
    print("Начинаю резервное копирование...")

    if not os.path.exists(BACKUP_DIR):
        os.makedirs(BACKUP_DIR)

    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    backup_filename = f"db_backup_{timestamp}.db"
    backup_path = os.path.join(BACKUP_DIR, backup_filename)

    try:
        shutil.copy2(DB_PATH, backup_path)
        print(f"Резервная копия сохранена: {backup_path}")
    except Exception as e:
        print(f"ОШИБКА при создании резервной копии: {e}")
        input("\nНажмите Enter для выхода...")
        return

    print("\n" + "-" * 50)
    print("Начинаю очистку базы данных...")

    tables_to_clear = ["contractors", "invoices", "acts"]
    if not keep_employees:
        tables_to_clear.append("employees")
    if not keep_stop_words:
        tables_to_clear.append("stop_words")

    tables_info = []
    if keep_employees:
        tables_info.append("employees (сотрудники)")
    if keep_stop_words:
        tables_info.append("stop_words (стоп-слова)")

    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        for table in tables_to_clear:
            cursor.execute(f"DELETE FROM {table}")
            print(f"  - Таблица '{table}' очищена")

        conn.commit()
        conn.close()

        print("\n" + "=" * 50)
        print("База данных успешно очищена!")
        print("=" * 50)
        print(f"\nРезервная копия: {backup_path}")
        print(f"Сохранены таблицы: {', '.join(tables_info) if tables_info else 'None'}")
        print(f"Очищены таблицы: {', '.join(tables_to_clear)}")

    except Exception as e:
        print(f"ОШИБКА при очистке базы данных: {e}")
        print("Попробуйте восстановить из резервной копии...")

    input("\nНажмите Enter для выхода...")


if __name__ == "__main__":
    main()
