import os
import tkinter as tk
from tkinter import messagebox

from .config import BASE_DIR, CONTRACTS_DIR, CONTRACT_TEMPLATE_PATH, format_integer, format_money


def safe_contract_filename(value):
    allowed = []
    for char in value:
        if char.isalnum() or char in ("-", "_"):
            allowed.append(char)
        else:
            allowed.append("_")
    return "".join(allowed).strip("_") or "contract"


def get_sale_contract_data(conn, sale_id):
    cursor = conn.execute(
        """
        SELECT
            s.sale_id,
            s.sale_date,
            COALESCE(s.contract_number, printf('ДП-%04d', s.sale_id)) AS contract_number,
            s.sale_price,
            COALESCE(s.payment_status, '') AS payment_status,
            COALESCE(s.payment_method, '') AS payment_method,
            COALESCE(s.payment_date, '') AS payment_date,
            c.car_id,
            c.brand,
            c.model,
            c.year,
            c.mileage,
            c.color,
            c.price,
            cl.name AS client_name,
            cl.phone AS client_phone,
            COALESCE(cl.email, '') AS client_email,
            e.name AS employee_name,
            e.position AS employee_position
        FROM sales s
        JOIN cars c ON s.car_id = c.car_id
        JOIN clients cl ON s.client_id = cl.client_id
        JOIN employees e ON s.employee_id = e.employee_id
        WHERE s.sale_id = ?
        """,
        (sale_id,),
    )
    row = cursor.fetchone()
    if row is None:
        return None
    columns = [description[0] for description in cursor.description]
    data = dict(zip(columns, row))
    data["sale_price_text"] = format_money(data["sale_price"])
    data["car_price_text"] = format_money(data["price"])
    data["mileage_text"] = format_integer(data["mileage"])
    return data


def render_contract(data):
    with open(CONTRACT_TEMPLATE_PATH, "r", encoding="utf-8") as file:
        template = file.read()
    return template.format(**data)


def show_contract_preview(title, text):
    preview = tk.Toplevel()
    preview.title(title)
    preview.geometry("760x620")

    text_box = tk.Text(preview, wrap="word")
    text_box.pack(fill="both", expand=True, padx=10, pady=10)
    text_box.insert("1.0", text)
    text_box.configure(state="disabled")


def generate_contract_for_sale(conn, tree, get_selected_values, refresh_sales):
    record = get_selected_values(tree)
    if record is None:
        return

    try:
        sale_id = record[0]
        data = get_sale_contract_data(conn, sale_id)
        if data is None:
            messagebox.showerror("Ошибка", "Продажа не найдена")
            return

        contract_text = render_contract(data)
        os.makedirs(CONTRACTS_DIR, exist_ok=True)
        filename = f"{safe_contract_filename(data['contract_number'])}.txt"
        contract_path = os.path.join(CONTRACTS_DIR, filename)
        with open(contract_path, "w", encoding="utf-8") as file:
            file.write(contract_text)

        relative_path = os.path.relpath(contract_path, BASE_DIR)
        conn.execute("UPDATE sales SET contract_file = ? WHERE sale_id = ?", (relative_path, sale_id))
        conn.commit()
        refresh_sales()
        show_contract_preview(f"Договор {data['contract_number']}", contract_text)
        messagebox.showinfo("Готово", f"Договор сохранён: {relative_path}")
    except Exception as error:
        messagebox.showerror("Ошибка", str(error))
