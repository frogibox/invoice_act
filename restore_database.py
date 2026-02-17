import sqlite3
import os
import shutil
from datetime import datetime

DB_PATH = "database.db"
BACKUP_DIR = "backups"


def list_backups():
    if not os.path.exists(BACKUP_DIR):
        return []
    files = [f for f in os.listdir(BACKUP_DIR) if f.endswith(".db")]
    files.sort()
    return files


def get_table_choice(table_name):
    while True:
        print(f"\nТаблица: {table_name}")
        print("  1. Не восстанавливать данные из бекапа для этой таблицы")
        print("  2. Дописать данные из бекапа в таблицу")
        print("  3. Заменить данные в таблице данными из бекапа")
        choice = input("Выберите вариант (по умолчанию 1): ").strip()
        if choice == "":
            return 1
        try:
            choice_num = int(choice)
            if choice_num in (1, 2, 3):
                return choice_num
        except ValueError:
            pass
        print("Введите 1, 2 или 3")


def restore_table(cursor_main, cursor_backup, table, mode):
    cursor_backup.execute(f"SELECT * FROM {table}")
    backup_rows = cursor_backup.fetchall()

    if not backup_rows:
        print(f"  - Таблица '{table}' пуста в бекапе")
        return

    cursor_main.execute(f"PRAGMA table_info({table})")
    columns = [info[1] for info in cursor_main.fetchall()]
    placeholders = ",".join(["?"] * len(columns))
    insert_sql = f"INSERT INTO {table} ({','.join(columns)}) VALUES ({placeholders})"

    if mode == 1:
        print(f"  - Таблица '{table}': не восстанавливается (оставлены текущие данные)")
    elif mode == 2:
        cursor_main.executemany(insert_sql, backup_rows)
        print(f"  - Таблица '{table}': добавлено {len(backup_rows)} записей из бекапа")
    elif mode == 3:
        cursor_main.execute(f"DELETE FROM {table}")
        cursor_main.executemany(insert_sql, backup_rows)
        print(
            f"  - Таблица '{table}': заменено на {len(backup_rows)} записей из бекапа"
        )


def main():
    print("=" * 60)
    print("Восстановление базы данных SQLite из резервной копии")
    print("=" * 60)

    if not os.path.exists(DB_PATH):
        print(f"ОШИБКА: База данных {DB_PATH} не найдена!")
        input("\nНажмите Enter для выхода...")
        return

    backups = list_backups()

    if not backups:
        print("Нет доступных резервных копий в папке backups/")
        input("\nНажмите Enter для выхода...")
        return

    print(f"\nДоступные резервные копии:\n")
    for i, backup in enumerate(backups, 1):
        backup_path = os.path.join(BACKUP_DIR, backup)
        size = os.path.getsize(backup_path)
        size_kb = size / 1024
        print(f"  {i}. {backup} ({size_kb:.1f} KB)")

    print("\n" + "-" * 60)

    while True:
        try:
            choice = input("Выберите номер бекапа для восстановления: ").strip()
            if not choice:
                print("Операция отменена.")
                input("\nНажмите Enter для выхода...")
                return
            choice_num = int(choice)
            if 1 <= choice_num <= len(backups):
                selected_backup = backups[choice_num - 1]
                break
            else:
                print(f"Неверный номер. Введите число от 1 до {len(backups)}")
        except ValueError:
            print("Введите корректный номер")

    backup_path = os.path.join(BACKUP_DIR, selected_backup)
    print(f"\nВыбран бекап: {selected_backup}")
    print("-" * 60)

    employees_choice = get_table_choice("employees (сотрудники)")
    print("-" * 60)
    stop_words_choice = get_table_choice("stop_words (стоп-слова)")
    print("-" * 60)

    print("Восстановление таблиц contractors, invoices, acts...")

    try:
        conn_main = sqlite3.connect(DB_PATH)
        cursor_main = conn_main.cursor()

        for table in ["contractors", "invoices", "acts"]:
            cursor_main.execute(f"DELETE FROM {table}")
            print(f"  - Таблица '{table}' очищена")

        conn_main.commit()
        conn_main.close()

        shutil.copy2(backup_path, DB_PATH + ".temp")

        conn_temp = sqlite3.connect(DB_PATH + ".temp")
        conn_main = sqlite3.connect(DB_PATH)
        cursor_temp = conn_temp.cursor()
        cursor_main = conn_main.cursor()

        for table in ["contractors", "invoices", "acts"]:
            cursor_temp.execute(f"SELECT * FROM {table}")
            rows = cursor_temp.fetchall()

            if rows:
                cursor_main.execute(f"PRAGMA table_info({table})")
                columns = [info[1] for info in cursor_main.fetchall()]
                placeholders = ",".join(["?"] * len(columns))
                insert_sql = (
                    f"INSERT INTO {table} ({','.join(columns)}) VALUES ({placeholders})"
                )
                cursor_main.executemany(insert_sql, rows)
                print(f"  - Таблица '{table}' восстановлена ({len(rows)} записей)")
            else:
                print(f"  - Таблица '{table}' пуста в бекапе")

        print("\n" + "-" * 60)
        print("Восстановление таблиц employees и stop_words...")

        restore_table(cursor_main, cursor_temp, "employees", employees_choice)
        restore_table(cursor_main, cursor_temp, "stop_words", stop_words_choice)

        conn_temp.close()
        conn_main.commit()
        conn_main.close()

        os.remove(DB_PATH + ".temp")

    except Exception as e:
        print(f"ОШИБКА при восстановлении: {e}")
        if os.path.exists(DB_PATH + ".temp"):
            os.remove(DB_PATH + ".temp")
        input("\nНажмите Enter для выхода...")
        return

    print("\n" + "=" * 60)
    print("База данных успешно восстановлена!")
    print("=" * 60)
    print(f"Восстановлено из: {selected_backup}")

    input("\nНажмите Enter для выхода...")


if __name__ == "__main__":
    main()
