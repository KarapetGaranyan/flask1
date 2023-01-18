from flask import Flask
import os


BASE_PATH = os.getcwd()
UPLOAD_FOLDER = f'{os.path.join(BASE_PATH, "")}uploads'
TEMPORARY_FOLDER = f'{os.path.join(BASE_PATH, "")}temporary'
TEMPLATES_FOLDER = f'{os.path.join(BASE_PATH, "")}templates1'
TREATIES_FOLDER = f'{os.path.join(BASE_PATH, "")}treaties1'
ALLOWED_EXTENSIONS = {'pdf'}

app = Flask(__name__)
app.config['BASE_PATH'] = BASE_PATH
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['TEMPORARY_FOLDER'] = TEMPORARY_FOLDER
app.config['TEMPLATES_FOLDER'] = TEMPLATES_FOLDER
app.config['TREATIES_FOLDER'] = TREATIES_FOLDER
app.config['ALLOWED_EXTENSIONS'] = ALLOWED_EXTENSIONS


from inn_app import routes

