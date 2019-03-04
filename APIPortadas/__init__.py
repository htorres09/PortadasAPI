#---------------------------------#
# -         Applicacion         - #
#---------------------------------#
from flask import Flask
from .configuracion import dict, hostData
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = dict['DIR_UPLOAD']
app.config['ALLOWED_EXTENSIONS'] = dict['EXTENSIONES']
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True
import APIPortadas.views