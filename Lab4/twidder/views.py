from markupsafe import escape
from flask_sock import Sock
from flask import render_template, render_template_string, request
import threading
from twidder.database_helper_psql import *
from twidder.config_reader import server_config
from twidder import app
from twidder.utils import *

sock = Sock(app)
conn = threading.local()
socks = {}


@app.before_request
def before_request():
    if not hasattr(conn, "db"):
        conn.db = init_db()


@app.route("/")
def index():
    return render_template("client.html")


@app.route("/send_recover_email", methods=["POST"])
def send_recover_email():
    data = request.get_json()
    email = data.get("email")
    user = get_user_by_email(conn.db, email)
    if user is None:
        return craft_response("User not exist", 404)
    delete_url_token(conn.db, user[0])
    content = email_template(
        email, user[3], generate_url_token(conn.db, user[0], email)
    )
    send_email(email, content)
    return craft_response("Success", 200)


@app.route("/reset_password/<token>", methods=["PUT"])
def reset_password(token):
    data = request.get_json()
    new_password = data.get("new_password")
    if len(new_password) < 8:
        return craft_response("Invalid password", 400)
    info = validate_url_token(conn.db, token)
    if info is None:
        return craft_response("Incorrect token", 401)
    update_password(conn.db, info[0], new_password)
    delete_url_token(conn.db, info[0])
    return craft_response("Success", 200)


@app.route("/reset_password/<token>", methods=["GET"])
def send_password_reset_form(token):
    return render_template_string(reset_password_template(token))


@sock.route("/sock")
def check_logout(sock: Sock):
    while True:
        token = sock.receive()
        if get_token_id(conn.db, token):
            socks[token] = sock


@app.route("/sign_in", methods=["POST"])
def sign_in():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")
    if username is None:
        return craft_response("Missing fields", 400)
    if password is None:
        return craft_response("Missing fields", 400)

    user = get_user_by_email(conn.db, username)

    if user is None:
        return craft_response("User not exist", 401)
    if password == user[2]:
        previous_token = get_token_by_id(conn.db, user[0])
        if previous_token:
            delete_token(conn.db, previous_token)
        if socks.get(previous_token):
            try:
                socks[previous_token].send("Log Out")
                socks.pop(previous_token)
            except:
                print("Connection Closed")

        token = generate_access_token(conn.db, user[0])

        return craft_response("success", 200, token)
    else:
        return craft_response("Incorrect password", 401)


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
        return craft_response("Missing fields", 400)

    if len(password) < 8:
        return craft_response("Invalid password", 400)
    if invalid_email(email):
        return craft_response("Invalid email address", 400)

    user = (email, password, firstname, familyname, gender, city, country)
    if get_user_by_email(conn.db, email) is None:
        create_user(conn.db, user)
        return craft_response("Success", 201)

    else:
        return craft_response("User already exists", 409)


@app.route("/sign_out", methods=["DELETE"])
def sign_out():
    token = get_authorization_token(request)
    if token is None or not get_token_id(conn.db, token):
        return craft_response("Invalid or missing token", 401)

    delete_token(conn.db, token)
    if socks.get(token):
        socks.pop(token)
    return craft_response(None, 204)


@app.route("/change_password", methods=["PUT"])
def change_password():
    data = request.get_json()
    old_password = data.get("oldpassword")
    new_password = data.get("newpassword")
    if any(field is None or field == "" for field in [old_password, new_password]):
        return craft_response("Missing fields", 400)
    token = get_authorization_token(request)
    uid = get_token_id(conn=conn.db, token=token)
    if token is None or uid is None:
        return craft_response("Invalid or missing token", 401)

    user = get_user_by_id(conn.db, uid)
    if user is None:
        return craft_response("User not exist", 401)

    if old_password != user[2]:
        return craft_response("Incorrect password", 401)

    if len(new_password) < 8:
        return craft_response("Invalid password", 400)

    update_password(conn.db, uid, new_password)
    return craft_response("Success", 200)


@app.route("/get_user_data_by_token", methods=["GET"])
def get_user_data_by_token():
    token = get_authorization_token(request)
    uid = get_token_id(conn.db, token)
    if token is None or uid is None:
        return craft_response("Invalid or missing token", 401)
    user = get_user_by_id(conn.db, uid)
    if user is None:
        return craft_response("User not exist", 401)
    user = user[0:2] + user[3:]
    return craft_response("Success", 200, user)


@app.route("/get_user_data_by_email/<email>", methods=["GET"])
def get_user_data_by_email(email):
    token = get_authorization_token(request)
    if token is None or not get_token_id(conn.db, token):
        return craft_response("Invalid or missing token", 401)
    email = escape(email)
    user = get_user_by_email(conn.db, email)
    if user is None:
        return craft_response("User not exist", 404)
    user = user[0:2] + user[3:]
    return craft_response("Success", 200, user)


@app.route("/post_message", methods=["POST"])
def post_message():
    token = get_authorization_token(request)
    uid = get_token_id(conn.db, token)
    if token is None or uid is None:
        return craft_response("Invalid or missing token", 401)
    data = request.get_json()
    message = data.get("message")
    email = data.get("email")
    if message is None or message == "":
        return craft_response("Empty message", 400)
    if email is None or email == "":
        return craft_response("Empty email address", 400)
    user = get_user_by_email(conn.db, email)
    if user is None:
        return craft_response("User not exist", 401)
    create_message(conn.db, uid, user[0], message)
    return craft_response("Success", 201)


@app.route("/get_user_messages_by_token", methods=["GET"])
def get_user_messages_by_token():
    token = get_authorization_token(request)
    uid = get_token_id(conn.db, token)
    if token is None or uid is None:
        return craft_response("Invalid or missing token", 401)
    messages = get_messages_by_receiver(conn.db, str(uid))
    if messages is not None:
        for i in range(len(messages)):
            email = get_user_by_id(conn.db, messages[i][1])[1]
            content = messages[i][3]
            messages[i] = {"writer": email, "content": content}
    return craft_response("Success", 200, messages)


@app.route("/get_user_messages_by_email/<email>", methods=["GET"])
def get_user_messages_by_email(email):
    token = get_authorization_token(request)
    if token is None or not get_token_id(conn.db, token):
        return craft_response(" Invalid or missing token", 401)
    email = escape(email)
    user = get_user_by_email(conn.db, email)
    if user is None:
        return craft_response("User not exist", 404)
    messages = get_messages_by_receiver(conn.db, str(user[0]))
    if messages is not None:
        for i in range(len(messages)):
            email = get_user_by_id(conn.db, messages[i][1])[1]
            content = messages[i][3]
            messages[i] = {"writer": email, "content": content}
    return craft_response("Success", 200, messages)


if __name__ == "__main__":
    app.run(port=server_config()["port"])
