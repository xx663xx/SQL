import sqlite3

conn = sqlite3.connect('students.db')
conn.execute("PRAGMA foreign_keys = ON")
cursor = conn.cursor()

cursor.execute('''
CREATE TABLE IF NOT EXISTS уровень_обучения (
    id_уровня INTEGER PRIMARY KEY,
    название VARCHAR(100) NOT NULL
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS направления (
    id_направления INTEGER PRIMARY KEY,
    название VARCHAR(100) NOT NULL
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS типы_обучения (
    id_типа INTEGER PRIMARY KEY,
    название VARCHAR(100) NOT NULL
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS студенты (
    id_студента INTEGER PRIMARY KEY,
    id_уровня INTEGER NOT NULL,
    id_направления INTEGER NOT NULL,
    id_типа_обучения INTEGER NOT NULL,
    фамилия VARCHAR(50) NOT NULL,
    имя VARCHAR(50) NOT NULL,
    отчество VARCHAR(50) NOT NULL,
    средний_балл INTEGER NOT NULL,
    FOREIGN KEY (id_уровня) REFERENCES уровень_обучения(id_уровня),
    FOREIGN KEY (id_направления) REFERENCES направления(id_направления),
    FOREIGN KEY (id_типа_обучения) REFERENCES типы_обучения(id_типа)
)
''')

уровни = [
    (1, 'Бакалавриат'),
    (2, 'Магистратура'),
    (3, 'Специалитет'),
]
cursor.executemany('INSERT OR REPLACE INTO уровень_обучения VALUES (?, ?)', уровни)

направления = [
    (1, 'Прикладная Информатика'),
    (2, 'Экономика'),
    (3, 'Юриспруденция'),
    (4, 'Менеджмент'),
]
cursor.executemany('INSERT OR REPLACE INTO направления VALUES (?, ?)', направления)

типы = [
    (1, 'Очная'),
    (2, 'Вечерняя'),
    (3, 'Заочная'),
]
cursor.executemany('INSERT OR REPLACE INTO типы_обучения VALUES (?, ?)', типы)

студенты = [
    (1, 1, 1, 1, 'Иванов', 'Иван', 'Иванович', 85),
    (2, 1, 1, 1, 'Петров', 'Петр', 'Петрович', 92),
    (3, 1, 1, 1, 'Сидоров', 'Сидор', 'Сидорович', 78),
    (4, 1, 2, 1, 'Смирнова', 'Анна', 'Алексеевна', 88),
    (5, 1, 2, 2, 'Кузнецов', 'Дмитрий', 'Сергеевич', 75),
    (6, 2, 1, 1, 'Васильев', 'Василий', 'Васильевич', 95),
    (7, 2, 3, 1, 'Михайлова', 'Мария', 'Михайловна', 82),
    (8, 2, 3, 3, 'Федоров', 'Федор', 'Федорович', 70),
    (9, 3, 4, 2, 'Алексеева', 'Александра', 'Александровна', 90),
    (10, 3, 4, 3, 'Николаев', 'Николай', 'Николаевич', 68),
    (11, 1, 1, 1, 'Иванов', 'Иван', 'Петрович', 87),
    (12, 1, 2, 2, 'Петров', 'Петр', 'Иванович', 91),
    (13, 2, 1, 1, 'Сидорова', 'Светлана', 'Игоревна', 94),
    (14, 2, 3, 3, 'Козлов', 'Константин', 'Кириллович', 72),
    (15, 3, 4, 1, 'Новикова', 'Наталья', 'Никитична', 86),
]
cursor.executemany('INSERT OR REPLACE INTO студенты VALUES (?, ?, ?, ?, ?, ?, ?, ?)', студенты)

conn.commit()

print("=" * 60)
print("ЗАПРОС 1: Количество всех студентов")
print("=" * 60)
cursor.execute('SELECT COUNT(*) AS количество FROM студенты')
result = cursor.fetchone()
print(f"Количество: {result[0]}")
print()

print("=" * 60)
print("ЗАПРОС 2: Количество студентов по направлениям")
print("=" * 60)
cursor.execute('''
SELECT н.название, COUNT(с.id_студента) AS количество
FROM студенты с
JOIN направления н ON с.id_направления = н.id_направления
GROUP BY н.id_направления, н.название
''')
for row in cursor.fetchall():
    print(f"{row[0]}: {row[1]}")
print()

print("=" * 60)
print("ЗАПРОС 3: Количество студентов по формам обучения")
print("=" * 60)
cursor.execute('''
SELECT т.название, COUNT(с.id_студента) AS количество
FROM студенты с
JOIN типы_обучения т ON с.id_типа_обучения = т.id_типа
GROUP BY т.id_типа, т.название
''')
for row in cursor.fetchall():
    print(f"{row[0]}: {row[1]}")
print()

print("=" * 60)
print("ЗАПРОС 4: Максимальный, минимальный, средний баллы по направлениям")
print("=" * 60)
cursor.execute('''
SELECT н.название,
       MAX(с.средний_балл) AS макс_балл,
       MIN(с.средний_балл) AS мин_балл,
       ROUND(AVG(с.средний_балл), 2) AS средн_балл
FROM студенты с
JOIN направления н ON с.id_направления = н.id_направления
GROUP BY н.id_направления, н.название
''')
for row in cursor.fetchall():
    print(f"{row[0]}: макс={row[1]}, мин={row[2]}, средн={row[3]}")
print()

print("=" * 60)
print("ЗАПРОС 5: Средний балл по направлениям, уровням и формам обучения")
print("=" * 60)
cursor.execute('''
SELECT н.название, у.название, т.название, ROUND(AVG(с.средний_балл), 2) AS средн_балл
FROM студенты с
JOIN направления н ON с.id_направления = н.id_направления
JOIN уровень_обучения у ON с.id_уровня = у.id_уровня
JOIN типы_обучения т ON с.id_типа_обучения = т.id_типа
GROUP BY н.id_направления, у.id_уровня, т.id_типа
''')
for row in cursor.fetchall():
    print(f"{row[0]} | {row[1]} | {row[2]}: {row[3]}")
print()

print("=" * 60)
print("ЗАПРОС 6: Топ-5 студентов Прикладной Информатики очной формы (по среднему баллу)")
print("=" * 60)
cursor.execute('''
SELECT с.фамилия, с.имя, с.отчество, с.средний_балл
FROM студенты с
JOIN направления н ON с.id_направления = н.id_направления
JOIN типы_обучения т ON с.id_типа_обучения = т.id_типа
WHERE н.название = 'Прикладная Информатика' AND т.название = 'Очная'
ORDER BY с.средний_балл DESC
LIMIT 5
''')
for row in cursor.fetchall():
    print(f"{row[0]} {row[1]} {row[2]} — балл: {row[3]}")
print()

print("=" * 60)
print("ЗАПРОС 7: Количество однофамильцев в базе")
print("=" * 60)
cursor.execute('''
SELECT фамилия, COUNT(*) AS количество
FROM студенты
GROUP BY фамилия
HAVING COUNT(*) > 1
''')
results = cursor.fetchall()
if results:
    for row in results:
        print(f"{row[0]}: {row[1]} человека")
else:
    print("Однофамильцев нет")
print()

print("=" * 60)
print("ЗАПРОС 8: Есть ли полные тезки (совпадают фамилия, имя, отчество)")
print("=" * 60)
cursor.execute('''
SELECT фамилия, имя, отчество, COUNT(*) AS количество
FROM студенты
GROUP BY фамилия, имя, отчество
HAVING COUNT(*) > 1
''')
results = cursor.fetchall()
if results:
    for row in results:
        print(f"{row[0]} {row[1]} {row[2]}: {row[3]} человека")
else:
    print("Полных тезок нет")
print()

print("=" * 60)
print("ДАННЫЕ ТАБЛИЦ")
print("=" * 60)

print("\n--- Таблица: уровень_обучения ---")
cursor.execute('SELECT * FROM уровень_обучения')
for row in cursor.fetchall():
    print(row)

print("\n--- Таблица: направления ---")
cursor.execute('SELECT * FROM направления')
for row in cursor.fetchall():
    print(row)

print("\n--- Таблица: типы_обучения ---")
cursor.execute('SELECT * FROM типы_обучения')
for row in cursor.fetchall():
    print(row)

print("\n--- Таблица: студенты ---")
cursor.execute('SELECT * FROM студенты')
for row in cursor.fetchall():
    print(row)

conn.close()

print("\n" + "=" * 60)
print("Файл students.db")
print("=" * 60)
