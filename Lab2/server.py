import http
from flask import Flask, json, request
from database_helper import *
import secrets
import threading

app = Flask(__name__)
conn = threading.local()
tokens = set()


@app.before_request
def before_request():
    if not hasattr(conn, "db"):
        conn.db = init_db()


@app.route("/sign_in", methods=["POST"])
def sign_in():
    username = request.form.get("username")
    password = request.form.get("password")

    user = get_user_by_email(conn.db, username)
    if user is None:
        return "Incorrect username or password", http.HTTPStatus.UNAUTHORIZED
    if password == user[2]:
        token = generate_access_token()
        return response(True, "User signed in", token), http.HTTPStatus.OK
    else:
        return (
            response(False, "Incorrect username or password"),
            http.HTTPStatus.UNAUTHORIZED,
        )


@app.route("/sign_up", methods=["POST"])
def sign_up():
    email = request.form.get("email")
    password = request.form.get("password")
    firstname = request.form.get("firstname")
    familyname = request.form.get("familyname")
    gender = request.form.get("gender")
    city = request.form.get("city")
    country = request.form.get("country")

    if any(
        field is None or field == ""
        for field in [email, password, firstname, familyname, gender, city, country]
    ):
        return response(False, "Please fill in all fields"), http.HTTPStatus.BAD_REQUEST

    if len(password) < 8:
        return (
            response(False, "Password must be at least 8 characters long"),
            http.HTTPStatus.BAD_REQUEST,
        )

    user = (email, password, firstname, familyname, gender, city, country)
    if get_user_by_email(conn.db, email) is None:
        uid = create_user(conn.db, user)
        token = generate_access_token(uid)
        return (
            response(True, f"User Created with id {uid}", token),
            http.HTTPStatus.CREATED,
        )
    else:
        return "User already exists", http.HTTPStatus.CONFLICT


@app.route("/sign_out", methods=["DELETE"])
def sign_out():
    token = get_authorization_token(request)
    if token is None or not is_valid_token(token):
        return (
            response(False, "Unauthorized - Invalid or missing token"),
            http.HTTPStatus.UNAUTHORIZED,
        )
    remove_token(token)
    return response(True, "signed out successfully"), http.HTTPStatus.NO_CONTENT


@app.route("/change_password", methods=["POST"])
def change_password():
    old_password = request.form.get("old_password")
    new_password = request.form.get("new_password")
    if any(field is None or field == "" for field in [old_password, new_password]):
        return response(False, "Please fill in all fields"), http.HTTPStatus.BAD_REQUEST
    token = get_authorization_token(request)
    if token is None or not is_valid_token(token):
        return (
            response(False, "Unauthorized - Invalid or missing token"),
            http.HTTPStatus.UNAUTHORIZED,
        )
    uid = tokens[token]
    user = get_user_by_id(uid)
    if user is None:
        return (
            response(False, "User does not exist"),
            http.HTTPStatus.INTERNAL_SERVER_ERROR,
        )
    if old_password != user[2]:
        return (
            response(False, "Incorrect password"),
            http.HTTPStatus.UNAUTHORIZED,
        )
    if len(new_password) < 8:
        return (
            response(False, "Password must be at least 8 characters long"),
            http.HTTPStatus.BAD_REQUEST,
        )
    update_password(uid, new_password)
    return (
        response(True, "Password updated"),
        http.HTTPStatus.OK,
    )


@app.route("/get_user_data_by_token", methods=["GET"])
def get_user_data_by_token():
    token = get_authorization_token(request)
    if token is None or not is_valid_token(token):
        return (
            response(False, "Unauthorized - Invalid or missing token"),
            http.HTTPStatus.UNAUTHORIZED,
        )
    uid = tokens[token]
    user = get_user_by_id(uid)
    if user is None:
        return (
            response(False, "User does not exist"),
            http.HTTPStatus.INTERNAL_SERVER_ERROR,
        )
    return response(True, "Success", user), http.HTTPStatus.OK


def generate_access_token(user_id):
    access_token = secrets.token_hex(16)
    tokens[access_token] = user_id
    return access_token


def remove_token(token):
    tokens.pop(token, None)


def is_valid_token(token):
    return token in tokens


def get_authorization_token(req):
    if "Authorization" not in req.headers:
        return None

    auth_header = req.headers.get("Authorization")
    parts = auth_header.split()

    if len(parts) != 2 or parts[0].lower() != "bearer":
        return None

    return parts[1]


def response(status, message, data=None):
    return json.dumps({"success": status, "message": message, "data": data})


if __name__ == "__main__":
    app.run(debug=True)
