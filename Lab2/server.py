from markupsafe import escape
import re
from flask import Flask, json, request
from database_helper import *
import secrets
import threading

app = Flask(__name__)
conn = threading.local()


@app.before_request
def before_request():
    if not hasattr(conn, "db"):
        conn.db = init_db()


@app.route("/sign_in", methods=["POST"])
def sign_in():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")

    user = get_user_by_email(conn.db, username)
    if user is None:
        return craft_response(False, "Incorrect username or password")
    if password is None:
        return craft_response(False, "Please fill in all fields")
    if password == user[2]:
        token = generate_access_token(user[0])
        response = app.make_response(craft_response(True, "User signed in", token))

        return response
    else:
        return craft_response(False, "Incorrect username or password")


@app.route("/sign_up", methods=["POST"])
def sign_up():
    data = request.get_json()

    email = data.get("email")
    password = data.get("password")
    firstname = data.get("firstname")
    familyname = data.get("familyname")
    gender = data.get("gender")
    city = data.get("city")
    country = data.get("country")

    if any(
        field is None or field == ""
        for field in [email, password, firstname, familyname, gender, city, country]
    ):
        return craft_response(False, "Please fill in all fields")

    if len(password) < 8:
        return craft_response(False, "Password must be at least 8 characters long")
    if invalid_email(email):
        return craft_response(False, "invalid email address")

    user = (email, password, firstname, familyname, gender, city, country)
    if get_user_by_email(conn.db, email) is None:
        uid = create_user(conn.db, user)
        return craft_response(True, f"User Created with id {uid}")

    else:
        return craft_response(False, "User already exists")


@app.route("/sign_out", methods=["DELETE"])
def sign_out():
    token = request.headers.get("Authorization")
    if token is None or not get_token_id(conn.db, token):
        return craft_response(False, "Unauthorized - Invalid or missing token")

    delete_token(conn.db, token)
    return craft_response(True, "signed out successfully")


@app.route("/change_password", methods=["PUT"])
def change_password():
    data = request.get_json()
    old_password = data.get("oldpassword")
    new_password = data.get("newpassword")
    if any(field is None or field == "" for field in [old_password, new_password]):
        return craft_response(False, "Please fill in all fields")
    token = request.headers.get("Authorization")
    uid = get_token_id(conn=conn.db, token=token)
    if token is None or uid is None:
        return craft_response(False, "Unauthorized - Invalid or missing token")

    user = get_user_by_id(conn.db, uid)
    if user is None:
        return craft_response(False, "User does not exist")

    if old_password != user[2]:
        return craft_response(False, "Incorrect password")

    if len(new_password) < 8:
        return craft_response(False, "Password must be at least 8 characters long")

    update_password(conn.db, uid, new_password)
    return craft_response(True, "Password updated")


@app.route("/get_user_data_by_token", methods=["GET"])
def get_user_data_by_token():
    token = request.headers.get("Authorization")
    uid = get_token_id(conn.db, token)
    print(f"token is {token} and uid is {uid}")
    if token is None or uid is None:
        return craft_response(False, "Unauthorized - Invalid or missing token")
    user = get_user_by_id(conn.db, uid)
    if user is None:
        return craft_response(False, "User does not exist")
    user = user[0:3] + user[4:]
    return craft_response(True, "Success", user)


@app.route("/get_user_data_by_email/<email>", methods=["GET"])
def get_user_data_by_email(email):
    token = request.headers.get("Authorization")
    if token is None or not get_token_id(conn.db, token):
        return craft_response(False, "Unauthorized - Invalid or missing token")
    email = escape(email)
    user = get_user_by_email(conn.db, email)
    if user is None:
        return craft_response(False, "User does not exist")
    user = user[0:3] + user[4:]
    return craft_response(True, "Success", user)


@app.route("/post_message", methods=["POST"])
def post_message():
    token = request.headers.get("Authorization")
    uid = get_token_id(conn.db, token)
    if token is None or uid is None:
        return craft_response(False, "Unauthorized - Invalid or missing token")
    data = request.get_json()
    message = data.get("message")
    email = data.get("email")
    if message is None or message == "":
        return craft_response(False, "empty message")
    if email is None or email == "":
        return craft_response(False, "empty email address")
    user = get_user_by_email(conn.db, email)
    if user is None:
        return craft_response(False, "User does not exist")
    create_message(conn.db, uid, user[0], message)
    return craft_response(True, "OK")


@app.route("/get_user_messages_by_token", methods=["GET"])
def get_user_messages_by_token():
    token = request.headers.get("Authorization")
    uid = get_token_id(conn.db, token)
    if token is None or uid is None:
        return craft_response(False, "Unauthorized - Invalid or missing token")
    messages = get_messages_by_receiver(conn.db, uid)
    return craft_response(True, "Success", messages)


@app.route("/get_user_messages_by_email/<email>", methods=["GET"])
def get_user_messages_by_email(email):
    token = request.headers.get("Authorization")
    if token is None or not get_token_id(conn.db, token):
        return craft_response(False, "Unauthorized - Invalid or missing token")

    if email is None or email == "":
        return craft_response(False, "empty email address")
    user = get_user_by_email(conn.db, email)
    if user is None:
        return craft_response(False, "User does not exist")
    messages = get_messages_by_receiver(conn.db, user[0])
    return craft_response(True, "Success", messages)


def generate_access_token(user_id):
    access_token = secrets.token_hex(16)
    issue_token(conn.db, user_id, access_token)
    return access_token


def invalid_email(email):
    email_pattern = re.compile(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")
    return not bool(email_pattern.match(email))


def get_authorization_token(req):
    if "Authorization" not in req.headers:
        return None

    auth_header = req.headers.get("Authorization")
    parts = auth_header.split()

    if len(parts) != 2 or parts[0].lower() != "bearer":
        return None

    return parts[1]


def craft_response(status, message, data=None):
    return json.dumps({"success": status, "message": message, "data": data})


if __name__ == "__main__":
    app.run()
