import re
import secrets
import smtplib, ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from flask import jsonify
from twidder.database_helper_psql import issue_token, register_url_token
from twidder import app
from twidder.config_reader import smtp_config, server_config

# this file contains all the util methods


# util function to generate random authentication token and store it in database, returns the generated token
def generate_access_token(conn, user_id):
    access_token = secrets.token_hex(16)
    issue_token(conn, user_id, access_token)
    return access_token


# check if email address is valid, return true if it's not valid
def invalid_email(email):
    # using re pattern to match valid email address
    email_pattern = re.compile(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")
    return not bool(email_pattern.match(email))


# fetch token from request, return the fetched token
def get_authorization_token(req):
    if "Authorization" not in req.headers:
        return None

    return req.headers.get("Authorization")


# def generate_url_token(conn, id, email):
#     token = secrets.token_urlsafe(16)
#     register_url_token(conn, id, email, token)
#     return token


# accept three parameters and craft a response object, router methods will use this method to return response to the client
def craft_response(message, status_code, data=None):
    # use make_response method in flask library, pass json format data
    response = app.make_response(jsonify({"message": message, "data": data}))
    response.status_code = status_code
    return response


# def email_template(receiver, username, token):
#     subject = "Password Reset Request"
#     sender = smtp_config()["sender"]
#     message = MIMEMultipart()
#     message["From"] = sender
#     message["To"] = receiver
#     message["Subject"] = subject
#     url = f"""{server_config()["host"]}/reset_password/{token}"""
#     body = f"""
#     <html>
#         <head></head>
#         <body>
#             <p>Dear {username},</p>
#             <p>You have requested to reset your password. Click the link below to reset it:</p>
#             <p><a href="{url}">{url}</a></p>
#             <p>If you didn't request this, please ignore this email.</p>
#             <p>Best regards,<br/>Twidder</p>
#         </body>
#     </html>
#     """
#     message.attach(MIMEText(body, "html"))

#     return message.as_string()


# predefined email template, using python's email library to generate a email object
def email_template_with_password(receiver, username, password):
    subject = "Password Reset "
    # read sender address from config file
    sender = smtp_config()["sender"]
    # email object
    message = MIMEMultipart()
    message["From"] = sender
    message["To"] = receiver
    message["Subject"] = subject
    body = f"""
    <html>
        <head></head>
        <body>
            <p>Dear {username},</p>
            <p>You have requested to reset your password. We generated a new one for you:</p>
            <p>Your new password: {password}</p>
            <p>If you didn't request this, please ignore this email.</p>
            <p>Best regards,<br/>Twidder</p>
        </body>
    </html>
    """
    # attach email string as html
    message.attach(MIMEText(body, "html"))

    return message.as_string()


# def reset_password_template(token):
#     url = f"{server_config()['host']}/reset_password/{token}"
#     html_template = f"""
# <!DOCTYPE html>
# <html lang="en">
# <head>
#     <meta charset="UTF-8">
#     <meta name="viewport" content="width=device-width, initial-scale=1.0">
#     <title>Reset Password</title>
# </head>
# <script>
#     function submitNewPassword(event) {{
#         event.preventDefault();
#         let new_password = document.getElementById("password").value;
#         let dataObject = {{
#             new_password: new_password
#         }};
#         let xhr = new XMLHttpRequest();
#         xhr.open("PUT", "{url}", true);
#         xhr.setRequestHeader("Content-Type", "application/json");

#         xhr.onreadystatechange = function () {{
#             if (xhr.readyState == 4) {{
#                 let responseData = JSON.parse(xhr.responseText);
#                 console.log(responseData);
#                 if (xhr.status == 200) {{
#                     window.alert("Password reset successfully!");
#                 }}
#             }}
#         }};
#         let requestBody = JSON.stringify(dataObject);
#         xhr.send(requestBody);
#     }}
# </script>
# <body>
#     <h1>Reset Password</h1>
#     <form onsubmit="submitNewPassword(event);" method="put">
#         <label for="password">New Password:</label>
#         <input type="password" id="password" name="password" required>
#         <br>
#         <input type="submit" value="Reset Password">
#     </form>
# </body>
# </html>
# """
#     return html_template


def send_email(receiver, content):
    # using configured app password from google to connect to its smtp server with ssl
    port = 465
    password = smtp_config()["app_psd"]
    context = ssl.create_default_context()
    server = smtplib.SMTP_SSL(smtp_config()["server"], port, context=context)
    # login to google account
    server.login(smtp_config()["sender"], password)
    try:
        # try send the email, if success return true
        server.sendmail(smtp_config()["sender"], receiver, content)
        return True, None
    except Exception as e:
        return False, e
