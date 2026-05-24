-- Простые запросы
SELECT car_id, brand, model, year, mileage, color, price
FROM cars
WHERE status = 'доступна';

SELECT client_id, name, phone, email
FROM clients
ORDER BY name;

SELECT employee_id, name, position, salary
FROM employees
WHERE salary > 90000;

SELECT supplier_id, name, contact
FROM suppliers
ORDER BY name;

SELECT service_order_id, car_id, description, cost, status
FROM service_orders
WHERE status = 'в работе';

SELECT reservation_id, car_id, client_id, employee_id, reservation_date, valid_until, status
FROM reservations
WHERE status = 'активна';

-- Вычисляемые запросы (с COUNT/SUM/AVG)
SELECT status, COUNT(*) AS car_count
FROM cars
GROUP BY status;

SELECT COUNT(*) AS sold_cars_count
FROM sales;

SELECT SUM(sale_price) AS total_sales_amount
FROM sales;

SELECT AVG(price) AS average_available_car_price
FROM cars
WHERE status = 'доступна';

SELECT status, COUNT(*) AS order_count, SUM(cost) AS total_service_cost, AVG(cost) AS average_service_cost
FROM service_orders
GROUP BY status;

-- Запросы с параметрами (5 штук, параметр обозначен символом ?)
SELECT car_id, brand, model, year, mileage, color, price, status
FROM cars
WHERE brand = ?;

SELECT car_id, brand, model, year, mileage, color, price, status
FROM cars
WHERE price BETWEEN ? AND ?;

SELECT client_id, name, phone, email
FROM clients
WHERE phone = ?;

SELECT sale_id, car_id, client_id, employee_id, sale_date, contract_number,
       sale_price, payment_status, payment_method, payment_date, contract_file
FROM sales
WHERE sale_date BETWEEN ? AND ?;

SELECT service_order_id, car_id, description, cost, status
FROM service_orders
WHERE status = ?;

-- Запросы с JOIN
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
    sales.payment_date,
    sales.contract_file
FROM sales
JOIN cars ON sales.car_id = cars.car_id
JOIN clients ON sales.client_id = clients.client_id
JOIN employees ON sales.employee_id = employees.employee_id;

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
JOIN employees ON reservations.employee_id = employees.employee_id;

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
JOIN employees ON test_drives.employee_id = employees.employee_id;

SELECT
    service_orders.service_order_id,
    cars.brand,
    cars.model,
    service_orders.description,
    service_orders.cost,
    service_orders.status
FROM service_orders
JOIN cars ON service_orders.car_id = cars.car_id;

-- Отчеты по продажам, договорам и новым сценариям
SELECT
    payment_method,
    COUNT(*) AS sales_count,
    SUM(sale_price) AS total_sales_amount,
    AVG(sale_price) AS average_sale_price
FROM sales
GROUP BY payment_method
ORDER BY total_sales_amount DESC;

SELECT sale_id, contract_number, car_id, client_id, employee_id,
       sale_date, sale_price, payment_method
FROM sales
WHERE contract_file IS NULL OR contract_file = ''
ORDER BY sale_date;

SELECT sale_id, contract_number, sale_date, sale_price, payment_method, contract_file
FROM sales
WHERE contract_file IS NOT NULL AND contract_file <> ''
ORDER BY sale_date;

SELECT reservation_id, car_id, client_id, employee_id, reservation_date, valid_until, status
FROM reservations
WHERE status = 'активна'
  AND valid_until BETWEEN ? AND ?
ORDER BY valid_until;

SELECT status AS reservation_status, COUNT(*) AS reservations_count
FROM reservations
GROUP BY status
ORDER BY reservations_count DESC;

SELECT
    employees.employee_id,
    employees.name AS employee_name,
    COUNT(sales.sale_id) AS sales_count,
    SUM(sales.sale_price) AS total_sales_amount,
    AVG(sales.sale_price) AS average_sale_price
FROM sales
JOIN employees ON sales.employee_id = employees.employee_id
GROUP BY employees.employee_id, employees.name
ORDER BY total_sales_amount DESC;

SELECT
    cars.brand,
    COUNT(sales.sale_id) AS sales_count,
    SUM(sales.sale_price) AS total_sales_amount,
    AVG(sales.sale_price) AS average_sale_price
FROM sales
JOIN cars ON sales.car_id = cars.car_id
GROUP BY cars.brand
ORDER BY sales_count DESC, total_sales_amount DESC;

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
ORDER BY average_available_car_price;

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
ORDER BY test_drives.test_drive_date;

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
ORDER BY total_service_cost DESC;