import tkinter as tk
from datetime import date
from tkinter import messagebox, ttk

from .config import COLUMN_LABELS, TABLES, format_row_for_display, value_from_entry
from .contracts import generate_contract_for_sale


def create_tree(parent):
    frame = ttk.Frame(parent)
    frame.pack(fill="both", expand=True, padx=10, pady=10)

    tree = ttk.Treeview(frame, show="headings")
    y_scroll = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
    x_scroll = ttk.Scrollbar(frame, orient="horizontal", command=tree.xview)
    tree.configure(yscrollcommand=y_scroll.set, xscrollcommand=x_scroll.set)

    tree.grid(row=0, column=0, sticky="nsew")
    y_scroll.grid(row=0, column=1, sticky="ns")
    x_scroll.grid(row=1, column=0, sticky="ew")
    frame.rowconfigure(0, weight=1)
    frame.columnconfigure(0, weight=1)

    return tree


def setup_tree_columns(tree, columns, labels=None):
    tree["columns"] = columns
    if labels is None:
        labels = [COLUMN_LABELS.get(column, column) for column in columns]
    for column, label in zip(columns, labels):
        tree.heading(column, text=label)
        tree.column(column, width=120, anchor="w")


def load_table_data(conn, tree, table, pk, fields):
    try:
        for item in tree.get_children():
            tree.delete(item)

        columns = [pk] + fields
        cursor = conn.execute(f"SELECT {', '.join(columns)} FROM {table}")
        for row in cursor.fetchall():
            tree.insert("", "end", values=format_row_for_display(columns, row))
    except Exception as error:
        messagebox.showerror("Ошибка", str(error))


def get_selected_values(tree):
    selected = tree.selection()
    if not selected:
        messagebox.showerror("Ошибка", "Выберите запись")
        return None
    return tree.item(selected[0], "values")


def next_contract_number(conn):
    last_id = conn.execute("SELECT COALESCE(MAX(sale_id), 0) FROM sales").fetchone()[0]
    return f"ДП-{last_id + 1:04d}"


def open_sale_form_for_car(conn, root, tree):
    record = get_selected_values(tree)
    if record is None:
        return

    status = record[8]
    if status != "доступна":
        messagebox.showerror("Ошибка", "Продать можно только автомобиль со статусом «доступна»")
        return

    today = date.today().isoformat()
    defaults = {
        "car_id": record[0],
        "sale_date": today,
        "contract_number": next_contract_number(conn),
        "sale_price": record[7],
        "payment_status": "оплачено",
        "payment_method": "банк",
        "payment_date": today,
        "contract_file": "",
    }
    open_record_form(conn, root, "Продать автомобиль", TABLES["Продажи"], tree, defaults=defaults)


def open_record_form(conn, root, title, config, tree, record=None, defaults=None):
    form = tk.Toplevel(root)
    form.title(title)
    form.geometry(f"430x{max(390, 70 + len(config['fields']) * 38)}")

    entries = []
    for i, label_text in enumerate(config["labels"]):
        label = ttk.Label(form, text=label_text)
        label.grid(row=i, column=0, padx=10, pady=6, sticky="w")

        entry = ttk.Entry(form, width=32)
        entry.grid(row=i, column=1, padx=10, pady=6, sticky="ew")

        field = config["fields"][i]
        if record is not None:
            entry.insert(0, record[i + 1])
        elif defaults is not None and field in defaults:
            entry.insert(0, defaults[field])

        entries.append(entry)

    form.columnconfigure(1, weight=1)

    def save_record():
        try:
            table = config["table"]
            pk = config["pk"]
            fields = config["fields"]
            values = [value_from_entry(entry.get(), field) for entry, field in zip(entries, fields)]

            if record is None:
                placeholders = ", ".join(["?"] * len(fields))
                sql = f"INSERT INTO {table} ({', '.join(fields)}) VALUES ({placeholders})"
                conn.execute(sql, values)
            else:
                set_part = ", ".join([f"{field} = ?" for field in fields])
                sql = f"UPDATE {table} SET {set_part} WHERE {pk} = ?"
                conn.execute(sql, values + [record[0]])

            conn.commit()
            if table == "sales" and title == "Продать автомобиль":
                load_table_data(conn, tree, "cars", "car_id", TABLES["Автомобили"]["fields"])
            else:
                load_table_data(conn, tree, table, pk, fields)
            form.destroy()
        except Exception as error:
            messagebox.showerror("Ошибка", str(error))

    save_button = ttk.Button(form, text="Сохранить", command=save_record)
    save_button.grid(row=len(config["fields"]), column=0, columnspan=2, padx=10, pady=12)


def delete_record(conn, config, tree):
    record = get_selected_values(tree)
    if record is None:
        return

    answer = messagebox.askyesno("Подтверждение", "Удалить выбранную запись?")
    if not answer:
        return

    try:
        table = config["table"]
        pk = config["pk"]
        conn.execute(f"DELETE FROM {table} WHERE {pk} = ?", (record[0],))
        conn.commit()
        load_table_data(conn, tree, table, pk, config["fields"])
    except Exception as error:
        messagebox.showerror("Ошибка", str(error))


def open_table_window(conn, root, title):
    config = TABLES[title]

    window = tk.Toplevel(root)
    window.title(title)
    window.geometry("1150x500")

    tree = create_tree(window)
    setup_tree_columns(tree, [config["pk"]] + config["fields"], [config["pk_label"]] + config["labels"])
    load_table_data(conn, tree, config["table"], config["pk"], config["fields"])

    buttons = ttk.Frame(window)
    buttons.pack(fill="x", padx=10, pady=(0, 10))

    add_button = ttk.Button(
        buttons,
        text="Добавить",
        command=lambda: open_record_form(conn, root, "Добавить", config, tree),
    )
    add_button.pack(side="left", padx=5)

    def edit_selected():
        record = get_selected_values(tree)
        if record is not None:
            open_record_form(conn, root, "Изменить", config, tree, record)

    edit_button = ttk.Button(buttons, text="Изменить", command=edit_selected)
    edit_button.pack(side="left", padx=5)

    delete_button = ttk.Button(buttons, text="Удалить", command=lambda: delete_record(conn, config, tree))
    delete_button.pack(side="left", padx=5)

    if title == "Автомобили":
        sell_button = ttk.Button(
            buttons,
            text="Продать выбранный автомобиль",
            command=lambda: open_sale_form_for_car(conn, root, tree),
        )
        sell_button.pack(side="left", padx=5)

    if title == "Продажи":
        contract_button = ttk.Button(
            buttons,
            text="Сформировать договор",
            command=lambda: generate_contract_for_sale(
                conn,
                tree,
                get_selected_values,
                lambda: load_table_data(conn, tree, "sales", "sale_id", TABLES["Продажи"]["fields"]),
            ),
        )
        contract_button.pack(side="left", padx=5)
