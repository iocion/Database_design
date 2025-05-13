from market import db,login_manager
from market import bcrypt
from flask_login import UserMixin
from datetime import datetime
# python 的代码逻辑
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# 用户表
class User(db.Model,UserMixin):
    id = db.Column(db.Integer(),primary_key=True)
    username =db.Column(db.String(length=30),nullable=False,unique=True)
    email_address = db.Column(db.String(length=50),nullable=False,unique=True)
    password_hash = db.Column(db.String(length=60),nullable=False)
    budget = db.Column(db.Integer(),nullable=False,default=10000000)
    items =db.relationship('Item',backref='owned_user',lazy=True)
# backreference



    @property
    def prettier_budget(self):
        if len(str(self.budget))>=4 and len(str(self.budget)) < 7 : #超过三位，中间显示" , "
            return f'{str(self.budget)[:-3]},{str(self.budget)[-3:]}元'
        elif len(str(self.budget))>=7: #超过6位，中间显示" , "
            return f'{str(self.budget)[:-6]},{str(self.budget)[-6:-3]},{str(self.budget)[-3:]}元' 
        else:
            return f"{self.budget}元"
        


    @property
    def password(self):
        return self.password
    
    @password.setter
    def password(self,plain_text_password):
        # self.password_hash=plain_text_password
        self.password_hash= bcrypt.generate_password_hash(plain_text_password).decode('utf-8')
    def check_password_correction(self,attempted_password):        # 检查密码是否正确
        return bcrypt.check_password_hash(self.password_hash,attempted_password)


    def can_purchase(self,item_obj):
        return self.budget >= item_obj.price

    def can_sell(self,item_obj):
        return item_obj in self.items

# 药品表    
class Item(db.Model):
    id = db.Column(db.Integer(),primary_key=True)
    name = db.Column(db.String(length=30),nullable=False,unique=True)
    price =db.Column(db.Integer(),nullable=False)
    barcode =db.Column(db.String(length=12),nullable=False,unique=False)
    description =db.Column(db.String(length=1024),nullable=False,unique=False)
    quantity =db.Column(db.Integer(),nullable=False,default=100)
    specification =db.Column(db.String(length=30),nullable=False,unique=False)
    owner = db.Column(db.Integer(),db.ForeignKey('user.id')) # 外键连接用户id
    # created_at = db.Column(db.DateTime, default=datetime.now)
    # def time_now(self):
    #     return datetime.now().strftime('%Y-%m-%d %H:%M:%S')

# class Register(db.Model):
#     user_name = db.Column(db.String(length=50),nullable=False,unique=True)
class Comment(db.Model):
    # 指定表名，确保与数据库表名一致
    __tablename__ = 'comment'
    # 评论的唯一ID，主键，自动递增
    id = db.Column(db.Integer, primary_key=True)
    # 发表评论的用户ID，外键关联到 user 表的 id
    # nullable=False 表示此字段不能为空
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    # 评论内容，使用 Text 类型以允许存储较长的文本
    # nullable=False 表示此字段不能为空
    comment_text = db.Column(db.Text, nullable=False)
    # 评论创建时间，默认为当前时间戳
    server_default=db.func.now()  #使用数据库服务器的当前时间函数
    created_at = db.Column(db.TIMESTAMP, nullable=False, server_default=db.func.now())
    # 定义与 User 模型的关系
    # 这使得你可以通过 comment.author 访问发表评论的用户对象
    # backref='comments' 在 User 模型中创建一个 comments 属性，
    # 可以通过 user.comments 访问该用户发表的所有评论
    author = db.relationship('User', backref='comments')

    # 可选：定义 __repr__ 方法，方便调试时打印对象信息
    def __repr__(self):
        return f"<Comment {self.id} by User {self.user_id}>"

    def __repr__(self):
        return f"药品名称:{self.name}"
    

    def buy(self,user):
        self.owner=user.id
        user.budget -=self.price
        db.session.commit()

    def sell(self,user):
        self.owner = None
        user.budget +=self.price
        db.session.commit()
