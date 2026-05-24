PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS suppliers (
    supplier_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    contact TEXT
);

CREATE TABLE IF NOT EXISTS cars (
    car_id INTEGER PRIMARY KEY AUTOINCREMENT,
    supplier_id INTEGER,
    brand TEXT NOT NULL,
    model TEXT NOT NULL,
    year INTEGER NOT NULL CHECK (year >= 1900),
    mileage INTEGER NOT NULL CHECK (mileage >= 0),
    color TEXT NOT NULL,
    price REAL NOT NULL CHECK (price >= 0),
    status TEXT NOT NULL DEFAULT 'доступна'
        CHECK (status IN ('доступна', 'продана', 'забронирована')),
    FOREIGN KEY (supplier_id) REFERENCES suppliers(supplier_id)
        ON UPDATE CASCADE
        ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS clients (
    client_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    phone TEXT NOT NULL UNIQUE,
    email TEXT UNIQUE
);

CREATE TABLE IF NOT EXISTS employees (
    employee_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    position TEXT NOT NULL,
    salary REAL NOT NULL CHECK (salary >= 0)
);

CREATE TABLE IF NOT EXISTS sales (
    sale_id INTEGER PRIMARY KEY AUTOINCREMENT,
    car_id INTEGER NOT NULL UNIQUE,
    client_id INTEGER NOT NULL,
    employee_id INTEGER NOT NULL,
    sale_date TEXT NOT NULL,
    contract_number TEXT,
    sale_price REAL NOT NULL CHECK (sale_price >= 0),
    payment_status TEXT NOT NULL DEFAULT 'оплачено'
        CHECK (payment_status IN ('ожидает оплаты', 'оплачено', 'отменена')),
    payment_method TEXT,
    payment_date TEXT,
    contract_file TEXT,
    FOREIGN KEY (car_id) REFERENCES cars(car_id)
        ON UPDATE CASCADE
        ON DELETE RESTRICT,
    FOREIGN KEY (client_id) REFERENCES clients(client_id)
        ON UPDATE CASCADE
        ON DELETE RESTRICT,
    FOREIGN KEY (employee_id) REFERENCES employees(employee_id)
        ON UPDATE CASCADE
        ON DELETE RESTRICT
);

CREATE TABLE IF NOT EXISTS reservations (
    reservation_id INTEGER PRIMARY KEY AUTOINCREMENT,
    car_id INTEGER NOT NULL,
    client_id INTEGER NOT NULL,
    employee_id INTEGER NOT NULL,
    reservation_date TEXT NOT NULL,
    valid_until TEXT,
    status TEXT NOT NULL DEFAULT 'активна'
        CHECK (status IN ('активна', 'завершена', 'отменена')),
    FOREIGN KEY (car_id) REFERENCES cars(car_id)
        ON UPDATE CASCADE
        ON DELETE RESTRICT,
    FOREIGN KEY (client_id) REFERENCES clients(client_id)
        ON UPDATE CASCADE
        ON DELETE RESTRICT,
    FOREIGN KEY (employee_id) REFERENCES employees(employee_id)
        ON UPDATE CASCADE
        ON DELETE RESTRICT
);

CREATE TABLE IF NOT EXISTS test_drives (
    test_drive_id INTEGER PRIMARY KEY AUTOINCREMENT,
    car_id INTEGER NOT NULL,
    client_id INTEGER NOT NULL,
    employee_id INTEGER NOT NULL,
    test_drive_date TEXT NOT NULL,
    result TEXT,
    FOREIGN KEY (car_id) REFERENCES cars(car_id)
        ON UPDATE CASCADE
        ON DELETE RESTRICT,
    FOREIGN KEY (client_id) REFERENCES clients(client_id)
        ON UPDATE CASCADE
        ON DELETE RESTRICT,
    FOREIGN KEY (employee_id) REFERENCES employees(employee_id)
        ON UPDATE CASCADE
        ON DELETE RESTRICT
);

CREATE TABLE IF NOT EXISTS service_orders (
    service_order_id INTEGER PRIMARY KEY AUTOINCREMENT,
    car_id INTEGER NOT NULL,
    description TEXT NOT NULL,
    cost REAL NOT NULL CHECK (cost >= 0),
    status TEXT NOT NULL DEFAULT 'новый'
        CHECK (status IN ('новый', 'в работе', 'завершен', 'отменен')),
    FOREIGN KEY (car_id) REFERENCES cars(car_id)
        ON UPDATE CASCADE
        ON DELETE RESTRICT
);

CREATE TRIGGER IF NOT EXISTS set_car_reserved_after_reservation
AFTER INSERT ON reservations
WHEN NEW.status = 'активна'
BEGIN
    UPDATE cars SET status = 'забронирована' WHERE car_id = NEW.car_id;
END;

CREATE TRIGGER IF NOT EXISTS set_car_sold_after_sale
AFTER INSERT ON sales
BEGIN
    UPDATE cars SET status = 'продана' WHERE car_id = NEW.car_id;
END;

CREATE TRIGGER IF NOT EXISTS complete_reservation_after_sale
AFTER INSERT ON sales
BEGIN
    UPDATE reservations
    SET status = 'завершена'
    WHERE car_id = NEW.car_id AND status = 'активна';
END;
