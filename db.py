import sqlite3

DB_PATH = "f1_data.db"


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS drivers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            team TEXT NOT NULL,
            number INTEGER,
            country TEXT,
            points INTEGER DEFAULT 0,
            image_path TEXT
        )
    """)
    conn.commit()

    cur.execute("SELECT COUNT(*) FROM drivers")
    if cur.fetchone()[0] == 0:
        sample = [
            ("Max Verstappen", "Red Bull Racing", 1, "Нидерланды", 575, ""),
            ("Lewis Hamilton", "Mercedes", 44, "Великобритания", 234, ""),
            ("Charles Leclerc", "Ferrari", 16, "Монако", 356, ""),
            ("Lando Norris", "McLaren", 4, "Великобритания", 374, ""),
            ("Fernando Alonso", "Aston Martin", 14, "Испания", 70, ""),
            ("Carlos Sainz", "Ferrari", 55, "Испания", 290, ""),
            ("George Russell", "Mercedes", 63, "Великобритания", 245, ""),
            ("Oscar Piastri", "McLaren", 81, "Австралия", 292, ""),
            ("Sergio Perez", "Red Bull Racing", 11, "Мексика", 152, ""),
        ]
        cur.executemany(
            "INSERT INTO drivers (name, team, number, country, points, image_path) "
            "VALUES (?, ?, ?, ?, ?, ?)", sample
        )
        conn.commit()
    conn.close()


def _like(text):
    """Экранирует спецсимволы шаблона LIKE, чтобы пользовательский ввод
    '%' или '_' не превращался в wildcards."""
    return text.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")


def fetch_all(search="", team_filter=""):
    conn = get_connection()
    cur = conn.cursor()
    query = "SELECT * FROM drivers WHERE 1=1"
    params = []
    if search:
        query += " AND (name LIKE ? ESCAPE '\\' OR country LIKE ? ESCAPE '\\'" \
                 " OR team LIKE ? ESCAPE '\\')"
        pattern = f"%{_like(search)}%"
        params += [pattern] * 3
    if team_filter and team_filter != "Все команды":
        query += " AND team = ?"
        params.append(team_filter)
    query += " ORDER BY points DESC"
    cur.execute(query, params)
    rows = cur.fetchall()
    conn.close()
    return rows


def get_stats():
    """Итоги по всей базе одним запросом."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*), COUNT(DISTINCT team), "
                "COALESCE(SUM(points), 0) FROM drivers")
    drivers, teams, points = cur.fetchone()
    conn.close()
    return drivers, teams, points


def get_teams():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT DISTINCT team FROM drivers ORDER BY team")
    teams = [r[0] for r in cur.fetchall()]
    conn.close()
    return ["Все команды"] + teams


def add_driver(name, team, number, country, points, image_path):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO drivers (name, team, number, country, points, image_path) "
        "VALUES (?, ?, ?, ?, ?, ?)",
        (name, team, number, country, points, image_path)
    )
    conn.commit()
    conn.close()


def update_driver(driver_id, name, team, number, country, points, image_path):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        UPDATE drivers
        SET name=?, team=?, number=?, country=?, points=?, image_path=?
        WHERE id=?
    """, (name, team, number, country, points, image_path, driver_id))
    conn.commit()
    conn.close()


def delete_driver(driver_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM drivers WHERE id=?", (driver_id,))
    conn.commit()
    conn.close()


def get_driver(driver_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM drivers WHERE id=?", (driver_id,))
    row = cur.fetchone()
    conn.close()
    return row
