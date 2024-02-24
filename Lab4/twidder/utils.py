import re
import secrets

from flask import jsonify

from twidder.database_helper_psql import issue_token
from twidder import app


def generate_access_token(conn, user_id):
    access_token = secrets.token_hex(16)
    print(user_id)
    print(access_token)
    issue_token(conn, user_id, access_token)
    return access_token


def invalid_email(email):
    email_pattern = re.compile(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")
    return not bool(email_pattern.match(email))


def get_authorization_token(req):
    if "Authorization" not in req.headers:
        return None

    return req.headers.get("Authorization")


def craft_response(message, status_code, data=None):
    response = app.make_response(jsonify({"message": message, "data": data}))
    response.status_code = status_code
    return response
