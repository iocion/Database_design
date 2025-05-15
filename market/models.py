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
    budget = db.Column(db.Integer(),nullable=False,default=1000)
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

    def buy(self, user, item):
        self.owner = user.id  # 设置商品的所有者
        user.budget -= item.price  # 扣除用户的预算
        item.quantity -= 1      #商品数量减一
        db.session.commit() #提前commit，解决延迟问题

        if item.quantity == 0:
            db.session.delete(item)
        db.session.commit()
    
    def sell(self,user):
        self.owner = None
        user.budget +=self.price
        db.session.commit()
    # created_at = db.Column(db.DateTime, default=datetime.now)
    # def time_now(self):
    #     return datetime.now().strftime('%Y-%m-%d %H:%M:%S')

# class Register(db.Model):
#     user_name = db.Column(db.String(length=50),nullable=False,unique=True)
# 评论表
class Comment(db.Model):
    __tablename__ = 'comment'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    item_id = db.Column(db.Integer, db.ForeignKey('item.id'), nullable=False) # 新增 item_id 外键
    comment_text = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.TIMESTAMP, nullable=False, server_default=db.func.now())
    author = db.relationship('User', backref='comments')
    item = db.relationship('Item', backref='comments') # 添加与 Item 的关系

    def __repr__(self):
        return f"<Comment by {self.author.username} on Item {self.item_id}: {self.comment_text[:20]}...>"

    
    def __repr__(self):
        return f"药品名称:{self.name}"
    
class Doctor(db.Model,UserMixin):
    __tablename__ = 'doctor'  # 指定表名

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)  # 医生ID，自动生成唯一标识
    doctor_name = db.Column(db.String(30), nullable=False)  # 医生姓名，不能为空，最大长度30
    doctor_id_number = db.Column(db.String(20), nullable=False, unique=True)  # 医生身份证号，不能为空，唯一
    doctor_phone = db.Column(db.String(11), nullable=False, unique=True)  # 医生电话，不能为空，唯一，长度11
    doctor_email = db.Column(db.String(255), nullable=False, unique=True)  # 医生邮箱，不能为空，唯一，符合邮箱格式，最大长度255
    created_at = db.Column(db.TIMESTAMP, server_default=db.func.now())  # 创建时间，默认为当前时间
    updated_at = db.Column(db.TIMESTAMP, server_default=db.func.now(), onupdate=db.func.now())  # 更新时间，默认为当前时间，更新时自动更新

    def check_password_correction(self, attempted_password):
        return self.doctor_id_number == attempted_password  # 直接比较明文密码