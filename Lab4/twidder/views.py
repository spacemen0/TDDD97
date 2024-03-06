from markupsafe import escape
from flask_sock import Sock
from flask import render_template, render_template_string, request, send_from_directory
import threading
from twidder.database_helper_psql import *
from twidder.config_reader import server_config
from twidder import app
from twidder.utils import *

# this file defines all the server routers

sock = Sock(app)
conn = threading.local()
# the dictionary to the websocket connections
socks = {}


@app.before_request
def before_request():
    if not hasattr(conn, "db"):
        conn.db = init_db()


# route to render the webpage
@app.route("/")
def index():
    return render_template("client.html")


# web browser will request icon using this route
@app.route("/favicon.ico", methods=["GET"])
def send_icon():
    return send_from_directory("static", "favicon.ico")


# route to send password recovery email
@app.route("/send_recover_email_with_password", methods=["POST"])
def send_recover_email_with_password():
    data = request.get_json()
    email = data.get("email")
    # first validate email, if no user registered under this email then return 404 user not exist
    user = get_user_by_email(conn.db, email)
    if user is None:
        return craft_response("User not exist", 404)
    # generate random new password for the user
    new_password = secrets.token_hex(8)
    # pass the generated password and user's first name to generate a email template
    content = email_template_with_password(email, user[3], new_password)
    # send the email
    send_email(email, content)
    # update user password in database
    update_password(conn.db, user[0], new_password)
    # returns status code ok
    return craft_response("Success", 200)


# for generating unique password recovery email with unique token but is not used by client now
# @app.route("/send_recover_email", methods=["POST"])
# def send_recover_email():
#     data = request.get_json()
#     email = data.get("email")
#     user = get_user_by_email(conn.db, email)
#     if user is None:
#         return craft_response("User not exist", 404)
#     delete_url_token(conn.db, user[0])
#     content = email_template(
#         email, user[3], generate_url_token(conn.db, user[0], email)
#     )
#     send_email(email, content)
#     return craft_response("Success", 200)


# @app.route("/reset_password/<token>", methods=["PUT"])
# def reset_password(token):
#     data = request.get_json()
#     new_password = data.get("new_password")
#     if len(new_password) < 8:
#         return craft_response("Invalid password", 400)
#     info = validate_url_token(conn.db, token)
#     if info is None:
#         return craft_response("Incorrect token", 401)
#     update_password(conn.db, info[0], new_password)
#     delete_url_token(conn.db, info[0])
#     return craft_response("Success", 200)


# @app.route("/reset_password/<token>", methods=["GET"])
# def send_password_reset_form(token):
#     return render_template_string(reset_password_template(token))


# anytime when a user logs in the client will request a websocket connection with the server using this route
@sock.route("/sock")
def check_logout(sock: Sock):
    while True:
        # client will send the token associated with the user
        token = sock.receive()
        # if token is valid then server will store the websocket connection in a dictionary, using token as teh key.
        if get_token_id(conn.db, token):
            socks[token] = sock


@app.route("/sign_in", methods=["POST"])
def sign_in():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")
    # validate if values of all required fields are sent with the request
    if username is None:
        return craft_response("Missing fields", 400)
    if password is None:
        return craft_response("Missing fields", 400)

    # check if user exist, if not returns user not exist un authorized
    user = get_user_by_email(conn.db, username)

    if user is None:
        return craft_response("User not exist", 401)
    if password == user[2]:
        # if user has a token stored in database, delete it so that server can issue a new one
        previous_token = get_token_by_id(conn.db, user[0])
        if previous_token:
            delete_token(conn.db, previous_token)
        # if server is storing a websocket connection for the current user, means this account is logged in in another place
        if socks.get(previous_token):
            try:
                # send log out message to the client where the current user is logged in before
                socks[previous_token].send("Log Out")
                # delete the previous websocket connection
                socks.pop(previous_token)
            except:
                # if there is error, means previous client may already closed the websocket connection
                print("Connection Closed")
        # generate a new token and insert it into database
        token = generate_access_token(conn.db, user[0])
        # returns status code ok
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

    # check if values of all fields are sent with the request, if not returns status code bad request
    if any(
        field is None or field == ""
        for field in [email, password, firstname, familyname, gender, city, country]
    ):
        return craft_response("Missing fields", 400)

    # validate password length and email in server side
    if len(password) < 8:
        return craft_response("Invalid password", 400)
    if invalid_email(email):
        return craft_response("Invalid email address", 400)

    # check is email is already be taken
    user = (email, password, firstname, familyname, gender, city, country)
    if get_user_by_email(conn.db, email) is None:
        create_user(conn.db, user)
        # return status created
        return craft_response("Success", 201)

    else:
        # return status conflict
        return craft_response("User already exists", 409)


@app.route("/sign_out", methods=["DELETE"])
def sign_out():
    # validate token, if token not exist or the associated user is none returns unauthorized
    token = get_authorization_token(request)
    if token is None or not get_token_id(conn.db, token):
        return craft_response("Invalid or missing token", 401)
    # delete token from database and pop the stored websocket connection
    delete_token(conn.db, token)
    if socks.get(token):
        socks.pop(token)
    return craft_response(None, 204)


@app.route("/change_password", methods=["PUT"])
def change_password():
    # check if values of all fields are sent with the request, if not returns status code bad request
    data = request.get_json()
    old_password = data.get("oldpassword")
    new_password = data.get("newpassword")
    if any(field is None or field == "" for field in [old_password, new_password]):
        return craft_response("Missing fields", 400)
    # validate token, if token not exist or the associated user is none returns unauthorized
    token = get_authorization_token(request)
    uid = get_token_id(conn=conn.db, token=token)
    if token is None or uid is None:
        return craft_response("Invalid or missing token", 401)
    # theoretically won't happen but checked anyway
    user = get_user_by_id(conn.db, uid)
    if user is None:
        return craft_response("User not exist", 401)

    # check if old password is correct and new password has at least 8 digits
    if old_password != user[2]:
        return craft_response("Incorrect password", 401)
    if len(new_password) < 8:
        return craft_response("Invalid password", 400)

    # if success, update password in database and returns status ok
    update_password(conn.db, uid, new_password)
    return craft_response("Success", 200)


@app.route("/get_user_data_by_token", methods=["GET"])
def get_user_data_by_token():
    # validate token, if token not exist or the associated user is none returns unauthorized
    token = get_authorization_token(request)
    uid = get_token_id(conn.db, token)
    if token is None or uid is None:
        return craft_response("Invalid or missing token", 401)
    user = get_user_by_id(conn.db, uid)
    if user is None:
        return craft_response("User not exist", 401)
    # using slices to exclude password in the response
    user = user[0:2] + user[3:]
    return craft_response("Success", 200, user)


@app.route("/get_user_data_by_email/<email>", methods=["GET"])
def get_user_data_by_email(email):
    # validate token, if token not exist or the associated user is none returns unauthorized
    token = get_authorization_token(request)
    if token is None or not get_token_id(conn.db, token):
        return craft_response("Invalid or missing token", 401)
    # using escape to prevent malicious user input
    email = escape(email)
    # check if user exist
    user = get_user_by_email(conn.db, email)
    if user is None:
        return craft_response("User not exist", 404)
    # using slices to exclude password in the response
    user = user[0:2] + user[3:]
    return craft_response("Success", 200, user)


@app.route("/post_message", methods=["POST"])
def post_message():
    # validate token, if token not exist or the associated user is none returns unauthorized
    token = get_authorization_token(request)
    uid = get_token_id(conn.db, token)
    if token is None or uid is None:
        return craft_response("Invalid or missing token", 401)
    # get message and email from request body
    data = request.get_json()
    message = data.get("message")
    email = data.get("email")
    # check the legality of email and message value, they can't be empty and email has to have a associated user
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
    # validate token, if token not exist or the associated user is none returns unauthorized
    token = get_authorization_token(request)
    uid = get_token_id(conn.db, token)
    if token is None or uid is None:
        return craft_response("Invalid or missing token", 401)
    # retrieve all the messages for the current user, here messages is a list of tuple
    messages = get_messages_by_receiver(conn.db, str(uid))
    if messages is not None:
        # iterate through the messages list, each entity(tuple) represent one message
        # messages table only stores id thus we need to fetch the email using id and format the response content using it
        for i in range(len(messages)):
            email = get_user_by_id(conn.db, messages[i][1])[1]
            content = messages[i][3]
            latitude = messages[i][4]
            longitude = messages[i][5]
            messages[i] = {
                "writer": email,
                "content": content,
                latitude: "latitude",
                longitude: "longitude",
            }
    return craft_response("Success", 200, messages)


@app.route("/get_user_messages_by_email/<email>", methods=["GET"])
def get_user_messages_by_email(email):
    # validate token, if token not exist or the associated user is none returns unauthorized
    token = get_authorization_token(request)
    if token is None or not get_token_id(conn.db, token):
        return craft_response(" Invalid or missing token", 401)
    # using escape to prevent malicious user input
    email = escape(email)
    # check whether the user whose messages the current user wants to query exists, if not returns not find
    user = get_user_by_email(conn.db, email)
    if user is None:
        return craft_response("User not exist", 404)
    # retrieve all the messages, here messages is a list of tuple
    messages = get_messages_by_receiver(conn.db, str(user[0]))
    if messages is not None:
        # iterate through the messages list, each entity(tuple) represent one message
        # messages table only stores id thus we need to fetch the email using id and format the response content using it
        for i in range(len(messages)):
            email = get_user_by_id(conn.db, messages[i][1])[1]
            content = messages[i][3]
            latitude = messages[i][4]
            longitude = messages[i][5]
            messages[i] = {
                "writer": email,
                "content": content,
                latitude: "latitude",
                longitude: "longitude",
            }
    return craft_response("Success", 200, messages)


if __name__ == "__main__":
    # run the server with the configured host and port
    app.run(host=server_config()["host"], port=server_config()["port"])
