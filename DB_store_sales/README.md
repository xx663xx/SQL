# Отчет по заданию

## Возможности программы

1) просмотр списка товаров
2) формирование одного чека из нескольких товаров
3) добавление нескольких одинаковых единиц товара в один чек
4) автоматическое уменьшение остатков
5) просмотр чеков
6) отчет за выбранную дату по количеству продаж и выручке

## Файлы с данными

Начальные данные загружаются из CSV-файлов.
Файлы читаются при первом запуске, если таблицы еще пустые.

## Таблицы базы данных

### categories
Содержит категории товаров.
- `id_category` - идентификатор категории
- `name_category` - название категории

### products
Содержит список товаров.
- `id_product` - идентификатор товара
- `name_of_product` - название товара
- `price` - цена за единицу
- `id_category` - категория товара
- `quantity_at_storage` - количество на складе

### receipts
Содержит чеки.
- `id_check` - идентификатор чека
- `created_at` - дата и время продажи
- `id_cashier` - кассир
- `total` - сумма чека
- в интерфейсе для чека также выводится перечень купленных товаров и их количество

### sale_items
Содержит позиции в чеке.
- `id_sale_item` - идентификатор записи
- `id_check` - ссылка на чек
- `id_product` - ссылка на товар
- `quantity` - количество проданного товара
- `price_at_sale` - цена товара на момент продажи

### jobs_titles
Содержит должности сотрудников.
- `id` - идентификатор должности
- `name` - название должности

### employees
Содержит сотрудников магазина.
- `id` - идентификатор сотрудника
- `name` - имя
- `surname` - фамилия
- `id_job_title` - должность

## Схема базы данных

```sql
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
```

## Основные запросы

Вывод товаров:

```sql
SELECT p.id_product, p.name_of_product, c.name_category, p.price, p.quantity_at_storage
FROM products p
JOIN categories c ON c.id_category = p.id_category
ORDER BY p.id_product;
```

Создание чека:

```sql
INSERT INTO receipts (created_at, id_cashier, total)
VALUES (?, ?, ?);
```

Добавление товара в чек:

```sql
INSERT INTO sale_items (id_check, id_product, quantity, price_at_sale)
VALUES (?, ?, ?, ?);
```

Уменьшение остатка товара на складе:

```sql
UPDATE products
SET quantity_at_storage = quantity_at_storage - ?
WHERE id_product = ?;
```

Вывод списка чеков:

```sql
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
ORDER BY r.id_check DESC;
```

Количество каждого проданного товара за выбранную дату:

```sql
SELECT p.name_of_product, SUM(si.quantity) AS total_sold
FROM sale_items si
JOIN receipts r ON r.id_check = si.id_check
JOIN products p ON p.id_product = si.id_product
WHERE DATE(r.created_at) = ?
GROUP BY p.name_of_product
ORDER BY p.name_of_product;
```

Выручка за выбранную дату:

```sql
SELECT COALESCE(SUM(si.quantity * si.price_at_sale), 0)
FROM sale_items si
JOIN receipts r ON r.id_check = si.id_check
WHERE DATE(r.created_at) = ?;
```