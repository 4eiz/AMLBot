import aiosqlite
import os
from dotenv import load_dotenv

load_dotenv()

async def script():
    name_file = "data/create_tables.sql"

    try:
        # Асинхронное подключение к базе данных
        async with aiosqlite.connect("data/base/base.db") as sqlite_connection:
            try:
                # Чтение SQL скрипта из файла
                with open(name_file, 'r', encoding='utf-8') as file:
                    sql_script = file.read()

                    try:
                        # Используем executescript для выполнения нескольких SQL-запросов
                        await sqlite_connection.executescript(sql_script)
                        await sqlite_connection.commit()
                        print("Скрипт выполнен успешно.")
                    except aiosqlite.Error as error:
                        # Логируем ошибку выполнения SQL-запросов
                        print("Ошибка при выполнении SQL-запросов:", error)
            except Exception as error:
                # Логируем ошибку при чтении файла
                print("Ошибка при чтении файла или выполнении скрипта:", error)
    except aiosqlite.Error as error:
        # Логируем ошибку подключения к базе данных
        print("Ошибка при подключении к SQLite:", error)
    finally:
        print("Соединение с SQLite закрыто.")
