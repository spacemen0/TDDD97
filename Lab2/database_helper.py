import sqlite3


def init_db() -> sqlite3.Connection:
    conn = sqlite3.connect("database.db")
    create_user_table(conn)
    create_message_table(conn)
    return conn


def create_user_table(conn: sqlite3.Connection) -> None:
    c = conn.cursor()
    c.execute(
        """CREATE TABLE IF NOT EXISTS users
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, email TEXT, password TEXT, firstname TEXT, familyname TEXT, gender TEXT, city TEXT, country TEXT)"""
    )
    conn.commit()
    c.close()


def create_message_table(conn: sqlite3.Connection) -> None:
    c = conn.cursor()
    c.execute(
        """CREATE TABLE IF NOT EXISTS messages
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, sender TEXT, receiver TEXT, message TEXT)"""
    )
    conn.commit()
    c.close()


def create_user(conn: sqlite3.Connection, user: tuple) -> None:
    c = conn.cursor()
    c.execute("INSERT INTO users VALUES (NULL, ?, ?, ?, ?, ?, ?, ?)", user)
    conn.commit()
    c.close()


def get_user_by_id(conn: sqlite3.Connection, id: int) -> tuple | None:
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE id = ?", (id,))
    user = c.fetchone()
    c.close()
    return user


def get_user_by_email(conn: sqlite3.Connection, email: str) -> tuple | None:
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE email = ?", (email,))
    user = c.fetchone()
    c.close()
    return user


def update_password(conn: sqlite3.Connection, id: str, password: str) -> None:
    c = conn.cursor()
    c.execute("UPDATE users SET password = ? WHERE id = ?", password, id)
    conn.commit()
    c.close()


def close_db(conn: sqlite3.Connection) -> None:
    conn.close()
