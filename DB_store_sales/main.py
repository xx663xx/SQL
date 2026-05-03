import csv
import sqlite3
from pathlib import Path
from tkinter import Tk, Frame, Label, Entry, Button, ttk, StringVar, END, messagebox
from datetime import datetime

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / 'store.db'


class StoreApp:
    def __init__(self, root):
        self.root = root
        self.root.title('Учет товаров и продаж')
        self.root.geometry('1360x620')

        self.conn = sqlite3.connect(DB_PATH)
        self.conn.row_factory = sqlite3.Row
        self.create_tables()
        self.seed_if_empty()

        self.report_date_var = StringVar(value=datetime.now().strftime('%Y-%m-%d'))
        self.cart_qty_var = StringVar(value='1')
        self.cart_total_var = StringVar(value='0.00')
        self.cashier_var = StringVar()
        self.cashiers = {}
        self.current_receipt_items = {}

        self.build_ui()
        self.refresh_all()

    def create_tables(self):
        cursor = self.conn.cursor()
        cursor.executescript('''
        PRAGMA foreign_keys = ON;

        CREATE TABLE IF NOT EXISTS categories (
            id_category INTEGER PRIMARY KEY AUTOINCREMENT,
            name_category TEXT NOT NULL UNIQUE
        );

        CREATE TABLE IF NOT EXISTS products (
            id_product INTEGER PRIMARY KEY AUTOINCREMENT,
            name_of_product TEXT NOT NULL,
            price REAL NOT NULL CHECK (price >= 0),
            id_category INTEGER NOT NULL,
            quantity_at_storage INTEGER NOT NULL DEFAULT 0 CHECK (quantity_at_storage >= 0),
            FOREIGN KEY (id_category) REFERENCES categories(id_category)
        );

        CREATE TABLE IF NOT EXISTS jobs_titles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS employees (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            surname TEXT NOT NULL,
            id_job_title INTEGER NOT NULL,
            FOREIGN KEY (id_job_title) REFERENCES jobs_titles(id)
        );

        CREATE TABLE IF NOT EXISTS receipts (
            id_check INTEGER PRIMARY KEY AUTOINCREMENT,
            created_at TEXT NOT NULL,
            id_cashier INTEGER,
            total REAL NOT NULL DEFAULT 0 CHECK (total >= 0),
            FOREIGN KEY (id_cashier) REFERENCES employees(id)
        );

        CREATE TABLE IF NOT EXISTS sale_items (
            id_sale_item INTEGER PRIMARY KEY AUTOINCREMENT,
            id_check INTEGER NOT NULL,
            id_product INTEGER NOT NULL,
            quantity INTEGER NOT NULL CHECK (quantity > 0),
            price_at_sale REAL NOT NULL CHECK (price_at_sale >= 0),
            FOREIGN KEY (id_check) REFERENCES receipts(id_check) ON DELETE CASCADE,
            FOREIGN KEY (id_product) REFERENCES products(id_product)
        );
        ''')

        columns = cursor.execute('PRAGMA table_info(receipts)').fetchall()
        column_names = [column[1] for column in columns]
        if 'id_cashier' not in column_names:
            cursor.execute('ALTER TABLE receipts ADD COLUMN id_cashier INTEGER')

        self.conn.commit()

    def read_csv(self, filename):
        with open(BASE_DIR / filename, encoding='utf-8') as file:
            return list(csv.DictReader(file, delimiter=';'))

    def seed_if_empty(self):
        cursor = self.conn.cursor()
        categories_count = cursor.execute('SELECT COUNT(*) FROM categories').fetchone()[0]
        if categories_count == 0:
            rows = []
            for row in self.read_csv('categories.csv'):
                rows.append((int(row['id_category']), row['name_category']))
            cursor.executemany('INSERT INTO categories VALUES (?, ?)', rows)

        jobs_count = cursor.execute('SELECT COUNT(*) FROM jobs_titles').fetchone()[0]
        if jobs_count == 0:
            rows = []
            for row in self.read_csv('jobs_titles.csv'):
                rows.append((int(row['id']), row['name']))
            cursor.executemany('INSERT INTO jobs_titles VALUES (?, ?)', rows)

        employees_count = cursor.execute('SELECT COUNT(*) FROM employees').fetchone()[0]
        if employees_count == 0:
            rows = []
            for row in self.read_csv('employees.csv'):
                rows.append((
                    int(row['id']),
                    row['name'],
                    row['surname'],
                    int(row['id_job_title'])
                ))
            cursor.executemany('INSERT INTO employees VALUES (?, ?, ?, ?)', rows)

        products_count = cursor.execute('SELECT COUNT(*) FROM products').fetchone()[0]
        if products_count == 0:
            rows = []
            for row in self.read_csv('products.csv'):
                rows.append((
                    int(row['id_product']),
                    row['name_of_product'],
                    float(row['price']),
                    int(row['id_category']),
                    int(row['quantity_at_storage'])
                ))
            cursor.executemany('INSERT INTO products VALUES (?, ?, ?, ?, ?)', rows)
        self.conn.commit()

    def build_ui(self):
        main = Frame(self.root, padx=10, pady=10)
        main.pack(fill='both', expand=True)

        top = Frame(main)
        top.pack(fill='x', anchor='w')

        left = Frame(top)
        left.pack(side='left', anchor='n')

        self.products_tree = ttk.Treeview(
            left,
            columns=('id', 'name', 'category', 'price', 'qty'),
            show='headings',
            height=14
        )
        for col, text, width in [
            ('id', 'ID', 50),
            ('name', 'Название', 300),
            ('category', 'Категория', 160),
            ('price', 'Цена', 90),
            ('qty', 'Остаток', 75),
        ]:
            self.products_tree.heading(col, text=text)
            self.products_tree.column(col, width=width)
        self.products_tree.grid(row=0, column=0, columnspan=5, sticky='nsew')

        scrollbar = ttk.Scrollbar(left, orient='vertical', command=self.products_tree.yview)
        self.products_tree.configure(yscroll=scrollbar.set)
        scrollbar.grid(row=0, column=5, sticky='ns')

        control_frame = Frame(left)
        control_frame.grid(row=1, column=0, columnspan=6, sticky='w', pady=(10, 0))

        Label(control_frame, text='Количество (целое число)').grid(row=0, column=0, sticky='w')
        self.sell_qty_entry = Entry(control_frame, width=10, textvariable=self.cart_qty_var)
        self.sell_qty_entry.grid(row=0, column=1, sticky='w', padx=8)
        Button(control_frame, text='Добавить в чек', command=self.add_to_cart).grid(row=0, column=2, sticky='w', padx=5)
        Button(control_frame, text='Убрать из чека', command=self.remove_from_cart).grid(row=0, column=3, sticky='w', padx=5)
        Button(control_frame, text='Очистить чек', command=self.clear_cart).grid(row=0, column=4, sticky='w', padx=5)

        cart_frame = Frame(top, padx=15)
        cart_frame.pack(side='left', anchor='n')

        Label(cart_frame, text='Текущий чек').grid(row=0, column=0, sticky='w')
        self.cart_tree = ttk.Treeview(
            cart_frame,
            columns=('id', 'name', 'price', 'qty', 'sum'),
            show='headings',
            height=8
        )
        for col, text, width in [
            ('id', 'ID', 50),
            ('name', 'Товар', 240),
            ('price', 'Цена', 90),
            ('qty', 'Кол-во', 75),
            ('sum', 'Сумма', 95),
        ]:
            self.cart_tree.heading(col, text=text)
            self.cart_tree.column(col, width=width)
        self.cart_tree.grid(row=1, column=0, columnspan=5, sticky='nsew', pady=8)

        Label(cart_frame, text='Итого по чеку:').grid(row=2, column=0, sticky='w')
        Label(cart_frame, textvariable=self.cart_total_var).grid(row=2, column=1, sticky='w')
        Label(cart_frame, text='Кассир').grid(row=3, column=0, sticky='w', pady=(8, 0))
        self.cashier_box = ttk.Combobox(cart_frame, textvariable=self.cashier_var, state='readonly', width=22)
        self.cashier_box.grid(row=3, column=1, columnspan=2, sticky='w', pady=(8, 0))
        Button(cart_frame, text='Оформить чек', command=self.checkout).grid(row=3, column=4, sticky='e', pady=(8, 0))

        bottom = Frame(main, pady=10)
        bottom.pack(fill='x', anchor='w')

        Label(bottom, text='Дата отчета (ГГГГ-ММ-ДД)').grid(row=0, column=0, sticky='w')
        Entry(bottom, textvariable=self.report_date_var, width=15).grid(row=0, column=1, padx=5)
        Button(bottom, text='Показать отчет', command=self.load_report).grid(row=0, column=2, padx=5)

        self.report_tree = ttk.Treeview(
            bottom,
            columns=('product', 'sold'),
            show='headings',
            height=8
        )
        self.report_tree.heading('product', text='Товар')
        self.report_tree.heading('sold', text='Продано')
        self.report_tree.column('product', width=320)
        self.report_tree.column('sold', width=120)
        self.report_tree.grid(row=1, column=0, columnspan=3, sticky='nsew', pady=10)

        self.revenue_label = Label(bottom, text='Выручка: 0.00')
        self.revenue_label.grid(row=2, column=0, sticky='w')

        self.receipts_tree = ttk.Treeview(
            bottom,
            columns=('check', 'date', 'cashier', 'items', 'total'),
            show='headings',
            height=8
        )
        self.receipts_tree.heading('check', text='Чек')
        self.receipts_tree.heading('date', text='Дата')
        self.receipts_tree.heading('cashier', text='Кассир')
        self.receipts_tree.heading('items', text='Перечень купленного')
        self.receipts_tree.heading('total', text='Сумма')
        self.receipts_tree.column('check', width=80)
        self.receipts_tree.column('date', width=170)
        self.receipts_tree.column('cashier', width=130)
        self.receipts_tree.column('items', width=360)
        self.receipts_tree.column('total', width=100)
        self.receipts_tree.grid(row=1, column=3, columnspan=3, sticky='nsew', padx=(20, 0), pady=10)

    def load_products(self):
        for item in self.products_tree.get_children():
            self.products_tree.delete(item)

        rows = self.conn.execute('''
            SELECT p.id_product, p.name_of_product, c.name_category, p.price, p.quantity_at_storage
            FROM products p
            JOIN categories c ON c.id_category = p.id_category
            ORDER BY p.id_product
        ''').fetchall()

        for row in rows:
            self.products_tree.insert('', END, values=(
                row['id_product'],
                row['name_of_product'],
                row['name_category'],
                f"{row['price']:.2f}",
                row['quantity_at_storage']
            ))

    def load_receipts(self):
        for item in self.receipts_tree.get_children():
            self.receipts_tree.delete(item)

        rows = self.conn.execute('''
            SELECT r.id_check,
                   r.created_at,
                   r.total,
                   COALESCE(e.name || ' ' || e.surname, '') AS cashier,
                   COALESCE(GROUP_CONCAT(p.name_of_product || ' x' || si.quantity, ', '), '') AS items
            FROM receipts r
            LEFT JOIN employees e ON e.id = r.id_cashier
            LEFT JOIN sale_items si ON si.id_check = r.id_check
            LEFT JOIN products p ON p.id_product = si.id_product
            GROUP BY r.id_check, r.created_at, r.total, cashier
            ORDER BY r.id_check DESC
        ''').fetchall()

        for row in rows:
            self.receipts_tree.insert('', END, values=(
                row['id_check'], row['created_at'], row['cashier'], row['items'], f"{row['total']:.2f}"
            ))

    def load_cashiers(self):
        rows = self.conn.execute('''
            SELECT id, name || ' ' || surname AS cashier
            FROM employees
            ORDER BY id
        ''').fetchall()

        self.cashiers = {}
        for row in rows:
            self.cashiers[row['cashier']] = row['id']

        names = list(self.cashiers.keys())
        self.cashier_box['values'] = names
        if names and self.cashier_var.get() not in names:
            self.cashier_var.set(names[0])

    def load_report(self):
        for item in self.report_tree.get_children():
            self.report_tree.delete(item)

        report_date = self.report_date_var.get().strip()
        try:
            datetime.strptime(report_date, '%Y-%m-%d')
        except ValueError:
            messagebox.showerror('Ошибка', 'Дата должна быть в формате ГГГГ-ММ-ДД')
            return

        rows = self.conn.execute('''
            SELECT p.name_of_product, SUM(si.quantity) AS total_sold
            FROM sale_items si
            JOIN receipts r ON r.id_check = si.id_check
            JOIN products p ON p.id_product = si.id_product
            WHERE DATE(r.created_at) = ?
            GROUP BY p.name_of_product
            ORDER BY p.name_of_product
        ''', (report_date,)).fetchall()

        for row in rows:
            self.report_tree.insert('', END, values=(row['name_of_product'], row['total_sold']))

        revenue = self.conn.execute('''
            SELECT COALESCE(SUM(si.quantity * si.price_at_sale), 0)
            FROM sale_items si
            JOIN receipts r ON r.id_check = si.id_check
            WHERE DATE(r.created_at) = ?
        ''', (report_date,)).fetchone()[0]

        self.revenue_label.config(text=f'Выручка: {revenue:.2f}')

    def add_to_cart(self):
        selected = self.products_tree.selection()
        if not selected:
            messagebox.showwarning('Предупреждение', 'Выберите товар в таблице')
            return

        try:
            qty = int(self.sell_qty_entry.get().strip())
        except ValueError:
            messagebox.showerror('Ошибка', 'Количество должно быть целым числом')
            return

        if qty <= 0:
            messagebox.showerror('Ошибка', 'Количество должно быть больше нуля')
            return

        values = self.products_tree.item(selected[0], 'values')
        product_id = int(values[0])
        product = self.conn.execute(
            'SELECT id_product, name_of_product, price, quantity_at_storage FROM products WHERE id_product = ?',
            (product_id,)
        ).fetchone()

        current_qty = self.current_receipt_items.get(product_id, {}).get('quantity', 0)
        new_qty = current_qty + qty
        if new_qty > product['quantity_at_storage']:
            messagebox.showerror('Ошибка', 'Нельзя добавить больше, чем есть на складе')
            return

        self.current_receipt_items[product_id] = {
            'name': product['name_of_product'],
            'price': float(product['price']),
            'quantity': new_qty,
        }
        self.sell_qty_entry.delete(0, END)
        self.sell_qty_entry.insert(0, '1')
        self.refresh_cart()

    def remove_from_cart(self):
        selected = self.cart_tree.selection()
        if not selected:
            messagebox.showwarning('Предупреждение', 'Выберите позицию в текущем чеке')
            return

        values = self.cart_tree.item(selected[0], 'values')
        product_id = int(values[0])
        if product_id in self.current_receipt_items:
            del self.current_receipt_items[product_id]
        self.refresh_cart()

    def clear_cart(self):
        self.current_receipt_items.clear()
        self.refresh_cart()

    def refresh_cart(self):
        for item in self.cart_tree.get_children():
            self.cart_tree.delete(item)

        total = 0.0
        for product_id, item in self.current_receipt_items.items():
            line_total = item['price'] * item['quantity']
            total += line_total
            self.cart_tree.insert('', END, values=(
                product_id,
                item['name'],
                f"{item['price']:.2f}",
                item['quantity'],
                f"{line_total:.2f}"
            ))

        self.cart_total_var.set(f'{total:.2f}')

    def checkout(self):
        if not self.current_receipt_items:
            messagebox.showwarning('Предупреждение', 'Чек пустой')
            return

        for product_id, item in self.current_receipt_items.items():
            stock = self.conn.execute(
                'SELECT quantity_at_storage FROM products WHERE id_product = ?',
                (product_id,)
            ).fetchone()['quantity_at_storage']
            if item['quantity'] > stock:
                messagebox.showerror('Ошибка', f"Недостаточно товара на складе: {item['name']}")
                return

        created_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        total = sum(item['price'] * item['quantity'] for item in self.current_receipt_items.values())
        cashier_id = self.cashiers.get(self.cashier_var.get())
        if cashier_id is None:
            messagebox.showerror('Ошибка', 'Выберите кассира')
            return

        cursor = self.conn.cursor()
        cursor.execute(
            'INSERT INTO receipts (created_at, id_cashier, total) VALUES (?, ?, ?)',
            (created_at, cashier_id, total)
        )
        receipt_id = cursor.lastrowid

        for product_id, item in self.current_receipt_items.items():
            cursor.execute(
                '''
                INSERT INTO sale_items (id_check, id_product, quantity, price_at_sale)
                VALUES (?, ?, ?, ?)
                ''',
                (receipt_id, product_id, item['quantity'], item['price'])
            )
            cursor.execute(
                'UPDATE products SET quantity_at_storage = quantity_at_storage - ? WHERE id_product = ?',
                (item['quantity'], product_id)
            )

        self.conn.commit()
        self.current_receipt_items.clear()
        self.refresh_all()
        messagebox.showinfo('Успех', f'Чек №{receipt_id} оформлен')

    def refresh_all(self):
        self.load_products()
        self.load_cashiers()
        self.load_receipts()
        self.load_report()
        self.refresh_cart()


if __name__ == '__main__':
    root = Tk()
    app = StoreApp(root)
    root.mainloop()
