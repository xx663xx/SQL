import os


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "data", "dealership.db")
SEED_PATH = os.path.join(BASE_DIR, "sql", "seed_data.sql")
SCHEMA_PATH = os.path.join(BASE_DIR, "sql", "schema.sql")
CONTRACT_TEMPLATE_PATH = os.path.join(BASE_DIR, "templates", "contract_template.txt")
CONTRACTS_DIR = os.path.join(BASE_DIR, "contracts")


TABLES = {
    "Поставщики": {
        "table": "suppliers",
        "pk": "supplier_id",
        "pk_label": "ID",
        "fields": ["name", "contact"],
        "labels": ["Название", "Контакт"],
    },
    "Автомобили": {
        "table": "cars",
        "pk": "car_id",
        "pk_label": "ID",
        "fields": ["supplier_id", "brand", "model", "year", "mileage", "color", "price", "status"],
        "labels": ["ID поставщика", "Марка", "Модель", "Год", "Пробег", "Цвет", "Цена", "Статус"],
    },
    "Клиенты": {
        "table": "clients",
        "pk": "client_id",
        "pk_label": "ID",
        "fields": ["name", "phone", "email"],
        "labels": ["Имя", "Телефон", "Email"],
    },
    "Сотрудники": {
        "table": "employees",
        "pk": "employee_id",
        "pk_label": "ID",
        "fields": ["name", "position", "salary"],
        "labels": ["Имя", "Должность", "Зарплата"],
    },
    "Продажи": {
        "table": "sales",
        "pk": "sale_id",
        "pk_label": "ID",
        "fields": [
            "car_id",
            "client_id",
            "employee_id",
            "sale_date",
            "contract_number",
            "sale_price",
            "payment_status",
            "payment_method",
            "payment_date",
            "contract_file",
        ],
        "labels": [
            "ID машины",
            "ID клиента",
            "ID сотрудника",
            "Дата",
            "Номер договора",
            "Цена продажи",
            "Статус оплаты",
            "Способ оплаты",
            "Дата оплаты",
            "Файл договора",
        ],
    },
    "Брони": {
        "table": "reservations",
        "pk": "reservation_id",
        "pk_label": "ID",
        "fields": ["car_id", "client_id", "employee_id", "reservation_date", "valid_until", "status"],
        "labels": ["ID машины", "ID клиента", "ID сотрудника", "Дата брони", "Действует до", "Статус"],
    },
    "Тест-драйвы": {
        "table": "test_drives",
        "pk": "test_drive_id",
        "pk_label": "ID",
        "fields": ["car_id", "client_id", "employee_id", "test_drive_date", "result"],
        "labels": ["ID машины", "ID клиента", "ID сотрудника", "Дата", "Результат"],
    },
    "Сервис": {
        "table": "service_orders",
        "pk": "service_order_id",
        "pk_label": "ID",
        "fields": ["car_id", "description", "cost", "status"],
        "labels": ["ID машины", "Описание", "Стоимость", "Статус"],
    },
}


REPORTS = {
    "Доступные автомобили": {
        "sql": """
        SELECT car_id, brand, model, year, mileage, color, price
        FROM cars
        WHERE status = 'доступна'
        ORDER BY price
        """,
    },
    "Клиенты по имени": {
        "sql": """
        SELECT client_id, name, phone, email
        FROM clients
        ORDER BY name
        """,
    },
    "Сотрудники с зарплатой выше 90 000": {
        "sql": """
        SELECT employee_id, name, position, salary
        FROM employees
        WHERE salary > 90000
        """,
    },
    "Поставщики по названию": {
        "sql": """
        SELECT supplier_id, name, contact
        FROM suppliers
        ORDER BY name
        """,
    },
    "Сервисные заявки в работе": {
        "sql": """
        SELECT service_order_id, car_id, description, cost, status
        FROM service_orders
        WHERE status = 'в работе'
        """,
    },
    "Активные брони": {
        "sql": """
        SELECT reservation_id, car_id, client_id, employee_id, reservation_date, valid_until, status
        FROM reservations
        WHERE status = 'активна'
        ORDER BY reservation_date
        """,
    },
    "Количество машин по статусам": {
        "sql": """
        SELECT status, COUNT(*) AS car_count
        FROM cars
        GROUP BY status
        """,
    },
    "Количество проданных автомобилей": {
        "sql": """
        SELECT COUNT(*) AS sold_cars_count
        FROM sales
        """,
    },
    "Общая сумма продаж": {
        "sql": """
        SELECT SUM(sale_price) AS total_sales_amount
        FROM sales
        """,
    },
    "Средняя цена доступных автомобилей": {
        "sql": """
        SELECT AVG(price) AS average_available_car_price
        FROM cars
        WHERE status = 'доступна'
        """,
    },
    "Сводка сервисных заявок": {
        "sql": """
        SELECT status, COUNT(*) AS order_count, SUM(cost) AS total_service_cost, AVG(cost) AS average_service_cost
        FROM service_orders
        GROUP BY status
        """,
    },
    "Автомобили по марке": {
        "sql": """
        SELECT car_id, brand, model, year, mileage, color, price, status
        FROM cars
        WHERE brand = ?
        """,
        "params": [
            {"label": "Марка", "default": "Toyota", "kind": "text"},
        ],
    },
    "Автомобили по диапазону цены": {
        "sql": """
        SELECT car_id, brand, model, year, mileage, color, price, status
        FROM cars
        WHERE price BETWEEN ? AND ?
        """,
        "params": [
            {"label": "Цена от", "default": "2000000", "kind": "number"},
            {"label": "Цена до", "default": "5000000", "kind": "number"},
        ],
    },
    "Клиент по телефону": {
        "sql": """
        SELECT client_id, name, phone, email
        FROM clients
        WHERE phone = ?
        """,
        "params": [
            {"label": "Телефон", "default": "+7-902-111-10-01", "kind": "text"},
        ],
    },
    "Продажи за период": {
        "sql": """
        SELECT sale_id, car_id, client_id, employee_id, sale_date, contract_number,
               sale_price, payment_status, payment_method, payment_date
        FROM sales
        WHERE sale_date BETWEEN ? AND ?
        """,
        "params": [
            {"label": "Дата от", "default": "2026-01-01", "kind": "text"},
            {"label": "Дата до", "default": "2026-05-31", "kind": "text"},
        ],
    },
    "Сервисные заявки по статусу": {
        "sql": """
        SELECT service_order_id, car_id, description, cost, status
        FROM service_orders
        WHERE status = ?
        """,
        "params": [
            {"label": "Статус", "default": "в работе", "kind": "text"},
        ],
    },
    "Продажи с клиентами и сотрудниками": {
        "sql": """
        SELECT
            sales.sale_id,
            cars.brand,
            cars.model,
            clients.name AS client_name,
            employees.name AS employee_name,
            sales.sale_date,
            sales.contract_number,
            sales.sale_price,
            sales.payment_status,
            sales.payment_method,
            sales.payment_date
        FROM sales
        JOIN cars ON sales.car_id = cars.car_id
        JOIN clients ON sales.client_id = clients.client_id
        JOIN employees ON sales.employee_id = employees.employee_id
        """,
    },
    "Брони с клиентами и автомобилями": {
        "sql": """
        SELECT
            reservations.reservation_id,
            cars.brand,
            cars.model,
            clients.name AS client_name,
            employees.name AS employee_name,
            reservations.reservation_date,
            reservations.valid_until,
            reservations.status
        FROM reservations
        JOIN cars ON reservations.car_id = cars.car_id
        JOIN clients ON reservations.client_id = clients.client_id
        JOIN employees ON reservations.employee_id = employees.employee_id
        ORDER BY reservations.reservation_date
        """,
    },
    "История тест-драйвов": {
        "sql": """
        SELECT td.test_drive_id, c.brand, c.model, cl.name AS client_name,
               e.name AS employee_name, td.test_drive_date, td.result
        FROM test_drives td
        JOIN cars c ON td.car_id = c.car_id
        JOIN clients cl ON td.client_id = cl.client_id
        JOIN employees e ON td.employee_id = e.employee_id
        ORDER BY td.test_drive_date
        """,
    },
    "Сервисные заявки с автомобилями": {
        "sql": """
        SELECT
            service_orders.service_order_id,
            cars.brand,
            cars.model,
            service_orders.description,
            service_orders.cost,
            service_orders.status
        FROM service_orders
        JOIN cars ON service_orders.car_id = cars.car_id
        """,
    },
    "Продажи по способу оплаты": {
        "sql": """
        SELECT
            payment_method,
            COUNT(*) AS sales_count,
            SUM(sale_price) AS total_sales_amount,
            AVG(sale_price) AS average_sale_price
        FROM sales
        GROUP BY payment_method
        ORDER BY total_sales_amount DESC
        """,
    },
    "Продажи без сформированного договора": {
        "sql": """
        SELECT sale_id, contract_number, car_id, client_id, employee_id,
               sale_date, sale_price, payment_method
        FROM sales
        WHERE contract_file IS NULL OR contract_file = ''
        ORDER BY sale_date
        """,
    },
    "Сформированные договоры": {
        "sql": """
        SELECT sale_id, contract_number, sale_date, sale_price, payment_method, contract_file
        FROM sales
        WHERE contract_file IS NOT NULL AND contract_file <> ''
        ORDER BY sale_date
        """,
    },
    "Активные брони с истекающим сроком": {
        "sql": """
        SELECT reservation_id, car_id, client_id, employee_id, reservation_date, valid_until, status
        FROM reservations
        WHERE status = 'активна'
          AND valid_until BETWEEN ? AND ?
        ORDER BY valid_until
        """,
        "params": [
            {"label": "Дата от", "default": "2026-03-01", "kind": "text"},
            {"label": "Дата до", "default": "2026-03-31", "kind": "text"},
        ],
    },
    "Конверсия броней в продажи": {
        "sql": """
        SELECT status AS reservation_status, COUNT(*) AS reservations_count
        FROM reservations
        GROUP BY status
        ORDER BY reservations_count DESC
        """,
    },
    "Продажи по менеджерам": {
        "sql": """
        SELECT
            employees.employee_id,
            employees.name AS employee_name,
            COUNT(sales.sale_id) AS sales_count,
            SUM(sales.sale_price) AS total_sales_amount,
            AVG(sales.sale_price) AS average_sale_price
        FROM sales
        JOIN employees ON sales.employee_id = employees.employee_id
        GROUP BY employees.employee_id, employees.name
        ORDER BY total_sales_amount DESC
        """,
    },
    "Популярные марки по продажам": {
        "sql": """
        SELECT
            cars.brand,
            COUNT(sales.sale_id) AS sales_count,
            SUM(sales.sale_price) AS total_sales_amount,
            AVG(sales.sale_price) AS average_sale_price
        FROM sales
        JOIN cars ON sales.car_id = cars.car_id
        GROUP BY cars.brand
        ORDER BY sales_count DESC, total_sales_amount DESC
        """,
    },
    "Автомобили в наличии по ценовым сегментам": {
        "sql": """
        SELECT
            CASE
                WHEN price < 3000000 THEN 'до 3 млн'
                WHEN price <= 5000000 THEN '3-5 млн'
                ELSE 'выше 5 млн'
            END AS price_segment,
            COUNT(*) AS car_count,
            AVG(price) AS average_available_car_price
        FROM cars
        WHERE status = 'доступна'
        GROUP BY price_segment
        ORDER BY average_available_car_price
        """,
    },
    "Тест-драйвы без продажи": {
        "sql": """
        SELECT
            test_drives.test_drive_id,
            cars.brand,
            cars.model,
            clients.name AS client_name,
            employees.name AS employee_name,
            test_drives.test_drive_date,
            test_drives.result
        FROM test_drives
        JOIN cars ON test_drives.car_id = cars.car_id
        JOIN clients ON test_drives.client_id = clients.client_id
        JOIN employees ON test_drives.employee_id = employees.employee_id
        LEFT JOIN sales
            ON sales.car_id = test_drives.car_id
           AND sales.client_id = test_drives.client_id
        WHERE sales.sale_id IS NULL
        ORDER BY test_drives.test_drive_date
        """,
    },
    "Сервисные затраты по проданным автомобилям": {
        "sql": """
        SELECT
            sales.sale_id,
            cars.brand,
            cars.model,
            clients.name AS client_name,
            sales.sale_price,
            COALESCE(SUM(service_orders.cost), 0) AS total_service_cost
        FROM sales
        JOIN cars ON sales.car_id = cars.car_id
        JOIN clients ON sales.client_id = clients.client_id
        LEFT JOIN service_orders ON service_orders.car_id = cars.car_id
        GROUP BY sales.sale_id, cars.brand, cars.model, clients.name, sales.sale_price
        ORDER BY total_service_cost DESC
        """,
    },
}


MONEY_COLUMNS = {
    "price",
    "salary",
    "sale_price",
    "cost",
    "total_sales",
    "total_sales_amount",
    "average_available_car_price",
    "average_sale_price",
    "total_service_cost",
    "average_service_cost",
}
INTEGER_COLUMNS = {"year", "mileage"}

COLUMN_LABELS = {
    "car_id": "ID машины",
    "supplier_id": "ID поставщика",
    "client_id": "ID клиента",
    "employee_id": "ID сотрудника",
    "sale_id": "ID продажи",
    "test_drive_id": "ID тест-драйва",
    "service_order_id": "ID заявки",
    "reservation_id": "ID брони",
    "brand": "Марка",
    "model": "Модель",
    "year": "Год",
    "mileage": "Пробег",
    "color": "Цвет",
    "price": "Цена",
    "status": "Статус",
    "name": "Имя",
    "contact": "Контакт",
    "phone": "Телефон",
    "email": "Email",
    "position": "Должность",
    "salary": "Зарплата",
    "sale_date": "Дата продажи",
    "contract_number": "Номер договора",
    "sale_price": "Цена продажи",
    "payment_status": "Статус оплаты",
    "payment_method": "Способ оплаты",
    "payment_date": "Дата оплаты",
    "contract_file": "Файл договора",
    "reservation_date": "Дата брони",
    "valid_until": "Действует до",
    "test_drive_date": "Дата тест-драйва",
    "result": "Результат",
    "description": "Описание",
    "cost": "Стоимость",
    "client_name": "Клиент",
    "employee_name": "Сотрудник",
    "sales_count": "Количество продаж",
    "total_sales": "Сумма продаж",
    "car_count": "Количество машин",
    "sold_cars_count": "Продано машин",
    "total_sales_amount": "Общая сумма продаж",
    "average_available_car_price": "Средняя цена доступных",
    "average_sale_price": "Средняя цена продажи",
    "order_count": "Количество заявок",
    "total_service_cost": "Общая стоимость сервиса",
    "average_service_cost": "Средняя стоимость сервиса",
    "reservations_count": "Количество броней",
    "reservation_status": "Статус брони",
    "price_segment": "Ценовой сегмент",
}


def value_from_entry(text, field=None):
    text = text.strip()
    if text == "":
        return None
    if field in MONEY_COLUMNS or field in INTEGER_COLUMNS:
        return text.replace(" ", "")
    return text


def format_money(value):
    if value is None:
        return ""
    try:
        number = float(value)
    except ValueError:
        return value
    if number.is_integer():
        return f"{int(number):,}".replace(",", " ")
    return f"{number:,.2f}".replace(",", " ")


def format_integer(value):
    if value is None:
        return ""
    try:
        return f"{int(value):,}".replace(",", " ")
    except ValueError:
        return value


def format_row_for_display(columns, row):
    result = []
    for column, value in zip(columns, row):
        if column in MONEY_COLUMNS:
            result.append(format_money(value))
        elif column == "mileage":
            result.append(format_integer(value))
        elif value is None:
            result.append("")
        else:
            result.append(value)
    return result
