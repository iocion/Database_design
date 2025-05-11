from flask import Flask,render_template
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
# from market.models import Item
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///market.db'
app.config['SECRET_KEY'] ='db92354e927ef71db526f676'
db = SQLAlchemy(app)
bcrypt = Bcrypt(app) 
login_manager = LoginManager(app)
login_manager.init_app(app)
login_manager.login_view = 'login_page'
login_manager.login_message_category = "info"
# Getter and Setter methods
from market import routes

# from market import app
# with app.app_context():
#     db.create_all()  # 创建表格
    
