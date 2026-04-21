import sqlite3


def print_result(title, cursor):
    print("\n" + title)
    for row in cursor.fetchall():
        print(row)


connection = sqlite3.connect(":memory:")
cursor = connection.cursor()

with open("students-1776139362.sql", "r", encoding="utf-8") as file:
    cursor.executescript(file.read())

cursor.executemany(
    "INSERT INTO уровни VALUES (?, ?)",
    [
        (1, "бакалавриат"),
        (2, "магистратура"),
    ],
)

cursor.executemany(
    "INSERT INTO направления VALUES (?, ?)",
    [
        (1, "Информатика"),
        (2, "Экономика"),
        (3, "Менеджмент"),
    ],
)

cursor.executemany(
    "INSERT INTO типы VALUES (?, ?)",
    [
        (1, "бюджет"),
        (2, "платно"),
    ],
)

cursor.executemany(
    "INSERT INTO студенты VALUES (?, ?, ?, ?, ?, ?, ?)",
    [
        (1, 1, 1, 1, "Иванов", "Иван", 4.8),
        (2, 1, 1, 2, "Петров", "Петр", 3.9),
        (3, 1, 2, 1, "Сидорова", "Анна", 4.3),
        (4, 2, 2, 2, "Козлов", "Олег", 3.2),
        (5, 2, 3, 1, "Смирнова", "Мария", 4.9),
    ],
)

cursor.execute(
    """
    SELECT
        фамилия,
        имя,
        средний_балл,
        CASE
            WHEN средний_балл >= 4.5 THEN 'отличник'
            WHEN средний_балл >= 3.5 THEN 'хорошист'
            ELSE 'троечник'
        END AS статус
    FROM студенты
    """
)
print_result("1. CASE: статус студента", cursor)

cursor.execute(
    """
    SELECT
        с.фамилия,
        с.имя,
        т.название AS тип,
        CASE
            WHEN т.название = 'бюджет' THEN 'учится бесплатно'
            WHEN т.название = 'платно' THEN 'учится платно'
            ELSE 'другой тип'
        END AS описание
    FROM студенты AS с
    JOIN типы AS т ON с.id_типа = т.id_типа
    """
)
print_result("2. CASE: форма обучения", cursor)

cursor.execute(
    """
    SELECT
        фамилия,
        имя,
        средний_балл
    FROM студенты
    WHERE средний_балл > (
        SELECT AVG(средний_балл)
        FROM студенты
    )
    """
)
print_result("3. Подзапрос: балл выше среднего", cursor)

cursor.execute(
    """
    SELECT
        название
    FROM направления
    WHERE id_направления IN (
        SELECT id_направления
        FROM студенты
        WHERE средний_балл >= 4.5
    )
    """
)
print_result("4. Подзапрос: направления с отличниками", cursor)

cursor.execute(
    """
    WITH хорошие_студенты AS (
        SELECT
            фамилия,
            имя,
            средний_балл
        FROM студенты
        WHERE средний_балл >= 4.0
    )
    SELECT *
    FROM хорошие_студенты
    """
)
print_result("5. CTE: хорошие студенты", cursor)

cursor.execute(
    """
    WITH средний_балл_по_направлению AS (
        SELECT
            н.название AS направление,
            AVG(с.средний_балл) AS средний_балл
        FROM студенты AS с
        JOIN направления AS н ON с.id_направления = н.id_направления
        GROUP BY н.название
    )
    SELECT *
    FROM средний_балл_по_направлению
    """
)
print_result("6. CTE: средний балл по направлениям", cursor)

connection.close()