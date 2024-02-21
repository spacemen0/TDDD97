import json
import re
import secrets

from twidder.database_helper import issue_token


def generate_access_token(conn, user_id):
    access_token = secrets.token_hex(16)
    issue_token(conn, user_id, access_token)
    return access_token


def invalid_email(email):
    email_pattern = re.compile(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")
    return not bool(email_pattern.match(email))


def get_authorization_token(req):
    if "Authorization" not in req.headers:
        return None

    return req.headers.get("Authorization")


def craft_response(status, message, data=None):
    return json.dumps({"success": status, "message": message, "data": data})
