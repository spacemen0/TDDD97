import secrets
from database_helper import *

conn = init_db()


def generate_access_token(user_id):
    access_token = secrets.token_hex(16)
    issue_token(conn, user_id, access_token)
    return access_token


generate_access_token(2)
token = generate_access_token(3)
delete_token(conn=conn, token=token)

tokens = get_all_tokens(conn=conn)
print(tokens)
