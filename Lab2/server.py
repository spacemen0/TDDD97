import http
import re
from flask import Flask, json, request
from database_helper import *
import secrets
import threading

app = Flask(__name__)
conn = threading.local()
tokens = {}


@app.before_request
def before_request():
    if not hasattr(conn, "db"):
        conn.db = init_db()


@app.route("/sign_in", methods=["POST"])
def sign_in():
    data = request.get_json()
    username = data.get("email")
    password = data.get("password")

    user = get_user_by_email(conn.db, username)
    if user is None:
        return craft_response(False, "Incorrect username or password")
    if password is None:
        return craft_response(False, "Please fill in all fields")
    if password == user[2]:
        token = generate_access_token(user[0])
        response = app.make_response(craft_response(True, "User signed in"))
        response.headers["Authorization"] = f"Bearer {token}"
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
        # token = generate_access_token(uid)
        return (
            craft_response(True, f"User Created with id {uid}")
            # ,
            # http.HTTPStatus.CREATED,
        )
    else:
        return craft_response(False, "User already exists")
    # , http.HTTPStatus.CONFLICT


@app.route("/sign_out", methods=["DELETE"])
def sign_out():
    token = get_authorization_token(request)
    if token is None or not is_valid_token(token):
        return (
            craft_response(False, "Unauthorized - Invalid or missing token")
            # ,
            # http.HTTPStatus.UNAUTHORIZED,
        )
    remove_token(token)
    return craft_response(True, "signed out successfully")


@app.route("/change_password", methods=["POST"])
def change_password():
    data = request.get_json()
    old_password = data.get("old_password")
    new_password = data.get("new_password")
    if any(field is None or field == "" for field in [old_password, new_password]):
        return craft_response(False, "Please fill in all fields")
    token = get_authorization_token(request)
    if token is None or not is_valid_token(token):
        return (
            craft_response(False, "Unauthorized - Invalid or missing token")
            # ,
            # http.HTTPStatus.UNAUTHORIZED,
        )
    uid = tokens[token]
    user = get_user_by_id(conn.db, uid)
    if user is None:
        return (
            craft_response(False, "User does not exist")
            # ,
            # http.HTTPStatus.INTERNAL_SERVER_ERROR,
        )
    if old_password != user[2]:
        return (
            craft_response(False, "Incorrect password")
            # ,
            # http.HTTPStatus.UNAUTHORIZED,
        )
    if len(new_password) < 8:
        return (
            craft_response(False, "Password must be at least 8 characters long")
            # ,
            # http.HTTPStatus.BAD_REQUEST,
        )
    update_password(conn.db, uid, new_password)
    return (
        craft_response(True, "Password updated")
        # ,
        # http.HTTPStatus.OK,
    )


@app.route("/get_user_data_by_token", methods=["GET"])
def get_user_data_by_token():
    token = get_authorization_token(request)
    if token is None or not is_valid_token(token):
        return (
            craft_response(False, "Unauthorized - Invalid or missing token")
            # ,
            # http.HTTPStatus.UNAUTHORIZED,
        )
    uid = tokens[token]
    user = get_user_by_id(conn.db, uid)
    if user is None:
        return (
            craft_response(False, "User does not exist")
            # ,
            # http.HTTPStatus.INTERNAL_SERVER_ERROR,
        )
    return craft_response(True, "Success", user)


def generate_access_token(user_id):
    access_token = secrets.token_hex(16)
    tokens[access_token] = user_id
    return access_token


def remove_token(token):
    tokens.pop(token, None)


def is_valid_token(token):
    return token in tokens


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
    app.run(debug=True)
