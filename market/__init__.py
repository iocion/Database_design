from flask import Flask,render_template
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
import pymysql
# from market.models import Item
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:123456@119.45.43.103:3311/medicine_market'  # 替换为你的 MySQL 连接信息
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///market.db'
app.config['SECRET_KEY'] ='db92354e927ef71db526f676'
db = SQLAlchemy(app)
bcrypt = Bcrypt(app) 
login_manager = LoginManager(app)
login_manager.init_app(app)
login_manager.login_view = 'login_page'
login_manager.login_message_category = "info"

login_manager.login_message = "请先登录才能访问此页面！"
# Getter and Setter methods
from market import routes    # 导入路由文件

# from market import app
# with app.app_context():
#     db.create_all()  # 创建表格
    
