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
        create_user(conn.db, user)
        token = generate_access_token()
        return response(True, "User Created", token), http.HTTPStatus.CREATED
    else:
        return "User already exists", http.HTTPStatus.CONFLICT


@app.route("/sign_out", methods=["POST"])
def sign_out():
    token = request.form.get("token")
    if token is None:
        return response(False, "incorrect token"), http.HTTPStatus.BAD_REQUEST
    try:
        tokens.remove(token)
    except KeyError:
        return response(False, "incorrect token"), http.HTTPStatus.BAD_REQUEST
    return response(True, "signed out successfully"), http.HTTPStatus.NO_CONTENT


def generate_access_token():
    access_token = secrets.token_hex(16)
    tokens.add(access_token)
    return access_token


def remove_access_token(token):
    tokens.discard(token)
    return


def response(status, message, data=None):
    return json.dumps({"success": status, "message": message, "data": data})


if __name__ == "__main__":
    app.run(debug=True)
