from flask import Flask


# set template folder
app = Flask(__name__, template_folder="template")

import twidder.views
