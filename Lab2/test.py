from database_helper import *

conn = init_db()
create_user_table(conn)
user = ("1", "1 ", " 1 ", " 1 ", "1  ", " 1 ", " 1 ")
insert_user(conn, user)
user = get_user_by_email(conn, "1")
print(user)
