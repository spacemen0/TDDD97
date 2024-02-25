import smtplib, ssl
from twidder.config_reader import smtp_config

port = 465
password = smtp_config()["app_psd"]
context = ssl.create_default_context()

with smtplib.SMTP_SSL(smtp_config()["server"], port, context=context) as server:
    server.login(smtp_config()["sender"], password)
    server.sendmail(smtp_config()["sender"], "frakctures@gmail.com", "second try")
