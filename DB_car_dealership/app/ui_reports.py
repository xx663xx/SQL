import tkinter as tk
from tkinter import messagebox, ttk

from .config import REPORTS, format_row_for_display
from .ui_tables import create_tree, setup_tree_columns


def run_report(conn, listbox, tree, param_entries):
    selection = listbox.curselection()
    if not selection:
        messagebox.showerror("Ошибка", "Выберите отчет")
        return

    report_name = listbox.get(selection[0])
    report = REPORTS[report_name]
    sql = report["sql"]
    params = []
    for entry, param in param_entries:
        value = entry.get().strip()
        if value == "":
            messagebox.showerror("Ошибка", f"Заполните параметр: {param['label']}")
            return
        if param.get("kind") == "number":
            value = value.replace(" ", "")
        params.append(value)

    try:
        cursor = conn.execute(sql, params)
        rows = cursor.fetchall()
        columns = [description[0] for description in cursor.description]

        for item in tree.get_children():
            tree.delete(item)

        setup_tree_columns(tree, columns)
        for row in rows:
            tree.insert("", "end", values=format_row_for_display(columns, row))
    except Exception as error:
        messagebox.showerror("Ошибка", str(error))


def open_reports_window(conn, root):
    window = tk.Toplevel(root)
    window.title("Отчёты")
    window.geometry("1150x620")

    left_frame = ttk.Frame(window)
    left_frame.pack(side="left", fill="y", padx=10, pady=10)

    report_list = tk.Listbox(left_frame, width=42, height=18)
    report_list.pack(fill="both", expand=True)

    for name in REPORTS:
        report_list.insert("end", name)

    param_frame = ttk.LabelFrame(left_frame, text="Параметры")
    param_frame.pack(fill="x", pady=(10, 0))
    param_entries = []

    def show_report_params(event=None):
        for child in param_frame.winfo_children():
            child.destroy()
        param_entries.clear()

        selection = report_list.curselection()
        if not selection:
            ttk.Label(param_frame, text="Выберите отчёт").pack(anchor="w", padx=8, pady=6)
            return

        report_name = report_list.get(selection[0])
        params = REPORTS[report_name].get("params", [])
        if not params:
            ttk.Label(param_frame, text="Параметры не требуются").pack(anchor="w", padx=8, pady=6)
            return

        for param in params:
            row = ttk.Frame(param_frame)
            row.pack(fill="x", padx=8, pady=4)
            ttk.Label(row, text=param["label"]).pack(anchor="w")
            entry = ttk.Entry(row)
            entry.pack(fill="x", pady=(2, 0))
            entry.insert(0, param.get("default", ""))
            param_entries.append((entry, param))

    tree = create_tree(window)

    report_list.bind("<<ListboxSelect>>", show_report_params)
    report_list.selection_set(0)
    show_report_params()

    run_button = ttk.Button(left_frame, text="Выполнить", command=lambda: run_report(conn, report_list, tree, param_entries))
    run_button.pack(fill="x", pady=10)
