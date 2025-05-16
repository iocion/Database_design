from flask_wtf import FlaskForm
from wtforms import StringField,PasswordField,SubmitField
from wtforms.validators import Length,EqualTo,Email,DataRequired,ValidationError
from market.models import User,Item,Doctor



class RegisterForm(FlaskForm):
    def validate_username(self,username_to_check):
        user =User.query.filter_by(username=username_to_check.data).first()
        if user:
            raise ValidationError('用户名已经存在')
        def validate_email_address(self,email_address_to_check):
            email_address= User.query.filter_by(email_address=email_address_to_check.data).first()
            if email_address:
                raise ValidationError('该用户的邮箱已经存在')
    username = StringField(label='User name:',validators=[Length(min=2,max=30),DataRequired()])
    email_address = StringField(label='Email Address:',validators=[Email(),DataRequired()])
    password1 = PasswordField(label='password:',validators=[Length(min=6),DataRequired()])
    password2 = PasswordField(label='Confirm password:',validators=[EqualTo('password1'),DataRequired()]) # confirm password2 == password1
    submit = SubmitField(label='Submit')

# class MedicineForm(FlaskForm):
#     def validate_on_medicin_name(self,medicine_name_to_check):
#         medicine_name_to_check = MedicineForm.query.filter_by(medicin_name=medicine_name_to_check.data).first()


        
class LoginForm(FlaskForm):
    username = StringField(label='User Name:',validators=[DataRequired()])
    password = StringField(label='Password:',validators=[DataRequired()])
    submit = SubmitField(label='Sign in')


class PurchaseItemForm(FlaskForm):
    submit = SubmitField(label='购买药品')


class SellItemForm(FlaskForm):
    submit = SubmitField(label='卖出商品')



class UpdateItemForm(FlaskForm):
    item_name = StringField(label='药品名称',validators=[DataRequired()])
    item_price = StringField(label='药品价格',validators=[DataRequired()])
    item_barcode = StringField(label='药品条形码',validators=[DataRequired()])
    item_description = StringField(label='药品描述',validators=[DataRequired()])
    submit = SubmitField(label='更新药品信息')
    def validate_item_name(self, item_name_to_check):
        item = item.query.filter_by(name=item_name_to_check.data).first()
        if item:
            raise ValidationError('药品名称已经存在')
        

# Flask-WTF Form 类
class DoctorForm(FlaskForm):
    doctor_name = StringField(label='医生姓名(管理员)', validators=[Length(min=2, max=30), DataRequired()])
    doctor_id_number = StringField(label='身份证', validators=[Length(min=10,max=20), DataRequired()])
    doctor_phone = StringField(label='医生电话', validators=[Length(11), DataRequired()])
    doctor_email = StringField(label='医生邮箱', validators=[Email(), DataRequired()])
    submit = SubmitField(label='添加医生信息')

class Doctor_LoginForm(FlaskForm):
    doctor_name = StringField(label='管理员:',validators=[DataRequired()])
    doctor_id_number = PasswordField(label='身份证:',validators=[DataRequired()])
    submit = SubmitField(label='登录')


    