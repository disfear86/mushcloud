from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
from flask_login import LoginManager

app = Flask(__name__)
app.config.from_object('config')
login_manager = LoginManager()
login_manager.init_app(app)

db = SQLAlchemy(app)
mail = Mail(app)

login_manager.login_view = 'login_page'


from . import views
