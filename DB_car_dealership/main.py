import tkinter as tk
from tkinter import messagebox, ttk

from app.database import connect_db, init_db
from app.ui_reports import open_reports_window
from app.ui_tables import open_table_window


def create_menu_section(parent, title, buttons, columns=2):
    section = ttk.LabelFrame(parent, text=title, padding=(10, 8))
    section.pack(fill="x", padx=18, pady=6)

    for column in range(columns):
        section.columnconfigure(column, weight=1)

    for index, (button_text, command) in enumerate(buttons):
        row = index // columns
        column = index % columns
        button = ttk.Button(section, text=button_text, command=command)
        button.grid(row=row, column=column, sticky="ew", padx=5, pady=4)


def close_app():
    conn.close()
    root.destroy()


conn = connect_db()

root = tk.Tk()
root.title("Автосалон")
root.geometry("640x610")
root.protocol("WM_DELETE_WINDOW", close_app)

try:
    init_db(conn)
except Exception as error:
    messagebox.showerror("Ошибка", str(error))

title_label = ttk.Label(root, text="База данных автосалона", font=("Arial", 16))
title_label.pack(pady=(18, 10))

menu_frame = ttk.Frame(root)
menu_frame.pack(fill="both", expand=True, padx=12, pady=(0, 12))

create_menu_section(
    menu_frame,
    "Основные операции",
    [
        ("Продать автомобиль", lambda: open_table_window(conn, root, "Автомобили")),
        ("Забронировать автомобиль", lambda: open_table_window(conn, root, "Брони")),
        ("Сформировать договор", lambda: open_table_window(conn, root, "Продажи")),
        ("Записать тест-драйв", lambda: open_table_window(conn, root, "Тест-драйвы")),
        ("Оформить сервис", lambda: open_table_window(conn, root, "Сервис")),
    ],
)

create_menu_section(
    menu_frame,
    "Справочники и учет",
    [
        ("Автомобили", lambda: open_table_window(conn, root, "Автомобили")),
        ("Клиенты", lambda: open_table_window(conn, root, "Клиенты")),
        ("Сотрудники", lambda: open_table_window(conn, root, "Сотрудники")),
        ("Поставщики", lambda: open_table_window(conn, root, "Поставщики")),
    ],
)

create_menu_section(
    menu_frame,
    "История и документы",
    [
        ("Продажи", lambda: open_table_window(conn, root, "Продажи")),
        ("Брони", lambda: open_table_window(conn, root, "Брони")),
        ("Тест-драйвы", lambda: open_table_window(conn, root, "Тест-драйвы")),
        ("Сервис", lambda: open_table_window(conn, root, "Сервис")),
    ],
)

create_menu_section(
    menu_frame,
    "Аналитика",
    [("Отчёты", lambda: open_reports_window(conn, root))],
    columns=1,
)

root.mainloop()
