import psycopg2
from psycopg2 import Error
from twidder.config_reader import database_config

# this file contains all the methods to interact with the remote database


# connect t o postgreSQL database and create necessary tables
def init_db():
    try:
        # read all the necessary database configuration
        conn = psycopg2.connect(
            dbname=database_config()["dbname"],
            user=database_config()["user"],
            password=database_config()["password"],
            host=database_config()["host"],
            port=database_config()["port"],
        )
        create_user_table(conn)
        create_message_table(conn)
        create_token_table(conn)
        # create_url_token_table(conn)
        return conn
    except Error as e:
        print(f"Error while connecting to PostgreSQL: {e}")
        return None


# user table, store user accounts
def create_user_table(conn):
    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                email TEXT,
                password TEXT,
                firstname TEXT,
                familyname TEXT,
                gender TEXT,
                city TEXT,
                country TEXT
            )
        """
        )
        conn.commit()
        cursor.close()
    except Error as e:
        print(f"Error while creating 'users' table: {e}")


# message table
def create_message_table(conn):
    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS messages (
                id SERIAL PRIMARY KEY,
                sender TEXT,
                receiver TEXT,
                message TEXT,
                latitude TEXT,
                longitude TEXT,
            )
        """
        )
        conn.commit()
        cursor.close()
    except Error as e:
        print(f"Error while creating 'messages' table: {e}")


# token table, stores tokens for authentication, the id of a token is always equal to the id of the user it belongs to
def create_token_table(conn):
    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS tokens (
                id INTEGER PRIMARY KEY,
                token TEXT
            )
        """
        )
        conn.commit()
        cursor.close()
    except Error as e:
        print(f"Error while creating 'tokens' table: {e}")


# for generating password recovery links but not necessary now
# def create_url_token_table(conn):
#     try:
#         cursor = conn.cursor()
#         cursor.execute(
#             """
#             CREATE TABLE IF NOT EXISTS URLtokens (
#                 id INTEGER PRIMARY KEY,
#                 email TEXT,
#                 token TEXT
#             )
#         """
#         )
#         conn.commit()
#         cursor.close()
#     except Error as e:
#         print(f"Error while creating 'URLtokens' table: {e}")


# inserts a user to user table and returns user id
def create_user(conn, user):
    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO users (email, password, firstname, familyname, gender, city, country)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            RETURNING id
        """,
            user,
        )
        user_id = cursor.fetchone()[0]
        conn.commit()
        return user_id
    except Error as e:
        print(f"Error while creating user: {e}")
        return None
    finally:
        if cursor:
            cursor.close()


# get user by user id, returns a tuple
def get_user_by_id(conn, user_id):
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
        user = cursor.fetchone()
        return user
    except Error as e:
        print(f"Error while fetching user by id: {e}")
        return None
    finally:
        if cursor:
            cursor.close()


# get user by user email, returns a tuple
def get_user_by_email(conn, email):
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
        user = cursor.fetchone()
        return user
    except Error as e:
        print(f"Error while fetching user by email: {e}")
        return None
    finally:
        if cursor:
            cursor.close()


# update user password
def update_password(conn, user_id, password):
    try:
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE users SET password = %s WHERE id = %s", (password, user_id)
        )
        conn.commit()
    except Error as e:
        print(f"Error while updating password: {e}")
    finally:
        if cursor:
            cursor.close()


# insert a message into messages table
def create_message(conn, sender, receiver, message):
    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO messages (sender, receiver, message,latitude,longitude)
            VALUES (%s, %s, %s, %s, %s)
        """,
            (sender, receiver, message, latitude, longitude),
        )
        conn.commit()
    except Error as e:
        print(f"Error while creating message: {e}")
    finally:
        if cursor:
            cursor.close()


# retrieve all messages by receiver, returns a list of message
def get_messages_by_receiver(conn, user_id):
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM messages WHERE receiver = %s", (user_id,))
        messages = cursor.fetchall()
        return messages
    except Error as e:
        print(f"Error while fetching messages by receiver: {e}")
        return None
    finally:
        if cursor:
            cursor.close()


# called when user logins in and server assigns they a token. insert a token into tokens table
def issue_token(conn, user_id, token):
    try:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO tokens (id, token) VALUES (%s, %s)",
            (
                user_id,
                token,
            ),
        )
        conn.commit()
    except Error as e:
        print(f"Error while issuing token: {e}")
    finally:
        if cursor:
            cursor.close()


# called when user signs out or signs in. delete their previous token from tokens table
def delete_token(conn, token):
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM tokens WHERE token = %s", (token,))
        conn.commit()
    except Error as e:
        print(f"Error while deleting token: {e}")
    finally:
        if cursor:
            cursor.close()


# get token by user id
def get_token_by_id(conn, user_id):
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT token FROM tokens WHERE id = %s", (user_id,))
        token = cursor.fetchone()
        return token[0] if token else None
    except Error as e:
        print(f"Error while fetching token by id: {e}")
        return None
    finally:
        if cursor:
            cursor.close()


# get user id by token value
def get_token_id(conn, token):
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM tokens WHERE token = %s", (token,))
        user_id = cursor.fetchone()
        return user_id[0] if user_id else None
    except Error as e:
        print(f"Error while fetching user id by token: {e}")
        return None
    finally:
        if cursor:
            cursor.close()


# for generating password recovery links but not necessary now
# def register_url_token(conn, id, email, token):
#     try:
#         cursor = conn.cursor()
#         cursor.execute(
#             "INSERT INTO URLtokens (id, email, token) VALUES (%s, %s, %s)",
#             (
#                 id,
#                 email,
#                 token,
#             ),
#         )
#         conn.commit()
#     except Error as e:
#         print(f"Error while registering URLtoken: {e}")
#     finally:
#         if cursor:
#             cursor.close()

# for generating password recovery links but not necessary now
# def validate_url_token(conn, token):
#     try:
#         cursor = conn.cursor()
#         cursor.execute("SELECT * FROM URLtokens WHERE token = %s", (token,))
#         res = cursor.fetchone()
#         return res if res else None
#     except Error as e:
#         print(f"Error while validating URLtoken: {e}")
#         return None
#     finally:
#         if cursor:
#             cursor.close()

# for generating password recovery links but not necessary now
# def delete_url_token(conn, id):
#     try:
#         cursor = conn.cursor()
#         cursor.execute("DELETE FROM URLtokens WHERE id = %s", (id,))
#         conn.commit()
#     except Error as e:
#         print(f"Error while deleting URLtoken: {e}")
#     finally:
#         if cursor:
#             cursor.close()


def close_db(conn):
    try:
        conn.close()
    except Error as e:
        print(f"Error while closing database connection: {e}")
