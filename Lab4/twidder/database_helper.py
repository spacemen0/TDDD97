import sqlite3


def init_db() -> sqlite3.Connection:
    conn = sqlite3.connect("database.db")
    create_user_table(conn)
    create_message_table(conn)
    create_token_table(conn)
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


def create_token_table(conn: sqlite3.Connection) -> None:
    c = conn.cursor()
    c.execute(
        """CREATE TABLE IF NOT EXISTS tokens
                 (id INTEGER PRIMARY KEY , token TEXT)"""
    )
    conn.commit()
    c.close()


def create_user(conn: sqlite3.Connection, user: tuple) -> int:
    c = conn.cursor()
    c.execute("INSERT INTO users VALUES (NULL, ?, ?, ?, ?, ?, ?, ?)", user)
    conn.commit()
    user_id = c.lastrowid
    c.close()
    return user_id


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
    c.execute(
        "UPDATE users SET password = ? WHERE id = ?",
        (
            password,
            id,
        ),
    )
    conn.commit()
    c.close()


def create_message(
    conn: sqlite3.Connection, sender: str, receiver: str, message: str
) -> None:
    c = conn.cursor()
    c.execute(
        "INSERT INTO messages VALUES (NULL, ?, ?, ?)",
        (
            sender,
            receiver,
            message,
        ),
    )
    conn.commit()
    c.close()


def get_messages_by_receiver(conn: sqlite3.Connection, id: str) -> tuple | None:
    c = conn.cursor()
    c.execute("SELECT * FROM messages WHERE receiver = ?", (id,))
    messages = c.fetchall()
    c.close()
    return messages


def issue_token(conn: sqlite3.Connection, id: int, token: str) -> None:
    c = conn.cursor()
    c.execute(
        "INSERT INTO tokens VALUES (?, ?)",
        (
            id,
            token,
        ),
    )
    conn.commit()
    c.close()


def delete_token(conn: sqlite3.Connection, token: str) -> None:
    c = conn.cursor()
    c.execute(
        "DELETE FROM tokens WHERE token = ?",
        (token,),
    )
    conn.commit()
    c.close()


def get_token_by_id(conn: sqlite3.Connection, id: int) -> str:
    c = conn.cursor()
    c.execute(
        "SELECT token FROM tokens WHERE id = ?",
        (id,),
    )
    token = c.fetchone()
    c.close()
    if token is None:
        return None
    return token[0]


def get_token_id(conn: sqlite3.Connection, token: str) -> int | None:
    c = conn.cursor()
    c.execute(
        "SELECT id FROM tokens WHERE token = ?",
        (token,),
    )
    id = c.fetchone()
    c.close()
    if id is None:
        return None
    return id[0]


def get_all_tokens(conn: sqlite3.Connection) -> tuple:
    c = conn.cursor()
    c.execute("SELECT * FROM tokens")
    tokens = c.fetchall()
    c.close()
    return tokens


def close_db(conn: sqlite3.Connection) -> None:
    conn.close()
