# -*- coding: utf-8 -*-
from market import app
from flask import render_template,redirect,url_for,flash,get_flashed_messages, request,jsonify
from market.models import Item,User,Comment,Doctor
from market.forms import RegisterForm,LoginForm,PurchaseItemForm,SellItemForm,UpdateItemForm,DoctorForm,Doctor_LoginForm,AddItemForm
from sqlalchemy.exc import IntegrityError
from market import db
from flask_login import login_user,login_required,logout_user,current_user
from openai import OpenAI  # 加入百度的大模型deepseekR8
import markdown
import re # 用来进行文本处理
import wraps
from datetime import timedelta,datetime
# from market import admin_required  # 定义管理元用户
# from mistralai.client import MistralClient


# 首页的AI药物建议部分
# --------------------------------------------------------------------------------------------------------------------------
client = OpenAI(
    api_key="525c607104d8891a998419b0d2ad22e0f2f26a7f",
    base_url="https://api-xa0fv6o8a9m1q9hd.aistudio-app.com/v1"
)


@app.route("/", methods=["GET", "POST"])
def index_page():
    condition = None
    advice = None
    error = None

    if request.method == "POST":
        condition = request.form.get("condition")
        if not condition:
            error = "请填写病情内容"
        else:
            try:
                # API call to get medication advice
                completion = client.chat.completions.create(
                    model="deepseek-r1:8b",
                    temperature=0.6,
                    messages=[
                        {"role": "user", "content": f"请根据病情 '{condition}' 给出病人可能需要服用的药物，并告诉每一种药物的使用流程，内容精简，，简介明了"}
                    ],
                    stream=True
                )
                # Collect response from streaming API
                # reasoning="" # 分解推理内容和最终内容
                advice = ""
                for chunk in completion:
                    if hasattr(chunk.choices[0].delta, "reasoning_content") and chunk.choices[0].delta.reasoning_content:
                        advice += chunk.choices[0].delta.reasoning_content
                    elif chunk.choices[0].delta.content:
                        advice += chunk.choices[0].delta.content
                advice = "".join(advice)
                # 使用正则表达式去除 <think> 标签及其内部的内容
                advice = re.sub(r"<think>.*?</think>", "", advice, flags=re.DOTALL)

                advice = markdown.markdown(advice)  # Convert Markdown to HTML
                # print(advice) 测试
            except Exception as e:
                error = f"{str(e)}"

    return render_template("index.html", condition=condition, advice=advice, error=error)

# --------------------------------------------------------------------------------------------------------------------------
# 仓库存储的显示
@app.route('/storage',methods=['GET','POST'])
@login_required
def storage_page():
        items = Item.query.filter_by(owner=None)   
        owned_items = Item.query.filter_by(owner=current_user.id)
        # 在库存部分显示已经在库存中的数量
        # owned_item_count = Item.query.filter(Item.owner!=None).count()
        owned_item_count = Item.query.filter_by(owner=current_user.id).count()
        return render_template('storage.html',items=items,owned_items=owned_items,owned_item_count=owned_item_count)


# ---------------------------------------------------------------------------------------------------------------------------
# 市场交易的显示
@app.route('/market',methods=['GET','POST'])
@login_required
def market_page():
    # Purchase Item Logic
    selling_form = SellItemForm()
    purchase_form =PurchaseItemForm()
    item_count = Item.query.count()
    if request.method =='POST': #解决js表单每一次跳出,request不能分清get和post方法
        purchased_item = request.form.get('purchase_item')
        p_item_object = Item.query.filter_by(name=purchased_item).first()
        item_number = 3  # 这里返回从前端设置的item_number
        if p_item_object:
                if current_user.can_purchase(p_item_object):    
                    if current_user.budget >= p_item_object.price:   # 判断金额是否大于budget
                        p_item_object.buy(current_user,p_item_object, item_number)   # 增加item_number 用来记录用户购买数量
                        flash(f"购买成功",category="success")
                    else:
                        missing_money = p_item_object.price-current_user.budget
                        flash(f"余额不足，差{missing_money}元",category="danger")
        # 售卖药品的逻辑
        sold_item = request.form.get('sold_item')
        s_item_object = Item.query.filter_by(name=sold_item).first()
        if s_item_object:
            if current_user.can_sell(s_item_object):
                s_item_object.sell(current_user)
                flash(f"药品{s_item_object.name}已放置药品市场",category="success")
        return redirect(url_for('market_page'))  
    
    if request.method == 'GET':
        items = Item.query.all()
        owned_items = Item.query.filter_by(owner=current_user.id)
        return render_template('market.html',item_count=item_count,items=items,purchase_form=purchase_form,owned_items=owned_items,selling_form=selling_form)
    
# ---------------------------------------------------------------------------------------------------------------------------
# 药品查询部分
# 使用名称查询
@app.route('/api/query/<string:item_name>', methods=['GET', 'POST'])
def query_item(item_name):
    #  like()  方法: 用于在数据库中执行模式匹配查询。
    #  %:   表示可以匹配任何字符序列（包括空序列）。
    item = Item.query.filter(Item.name.like(f'%{item_name}%')).first()
    if item:
        return jsonify({
            'id': item.id,
            'specification': item.specification,
            'name': item.name,
            'price': item.price,
            'barcode': item.barcode,
            'description': item.description,
            'quantity': item.quantity
        })
    else:
        return jsonify({'error': '未找到相关药品'}), 404        
# 使用药品序号进行查询
@app.route('/api/query_id/<int:item_id>',methods=['GET','POST'])
def query_item_by_id(item_id):
    # item = Item.query.filter(item_id).first()
    item = Item.query.filter_by(id=item_id).first()
    if item:
        return jsonify({
            'id': item.id,
            'specification': item.specification,
            'name':item.name,
            'price':item.price,
            'barcode':item.barcode,
            'description':item.description,
            'quantity':item.quantity
        })
    else:
        return jsonify({'error':'未找到相关药品'}),404
# ------------------------------------------------------------------------------------------------------------------------
# 登录管理员账号
# @app.route('/admin_login',methods=['GET','POST'])
# def doctor_login_page():
#      form = Doctor_LoginForm()
#      if form.validate_on_submit():
#           admin_user = Doctor.query.filter_by(doctor_name=form.doctor_name.data).first()
#           if admin_user and admin_user.check_password_correction(
#                attempted_password=form.doctor_id_number.data                    
#                ):
#                 login_user(admin_user)
#                 flash(
#                     f'欢迎{admin_user.doctor_name}医生',category='success'
#                 )
#                 return redirect(url_for('outlook_page'))
#           else:
#                flash('密码错误或者用户不存在',category='danger')
#      return render_template('doctor_login.html',form=form)
# 管理员登出部分
@app.route("/admin_logout")
@login_required
def admin_logout_page(): 
    logout_user()
    flash("已经成功退出登录", category="info")
    return redirect(url_for('index_page'))

# ----------------------------------------------------------------------------------------------------------------------
# 用户注册部分
@app.route('/register', methods=['GET', 'POST'])
def register_page():
    form = RegisterForm()

    if form.validate_on_submit():
        try:
            user_to_create = User(
                username=form.username.data,
                email_address=form.email_address.data,
                password=form.password1.data
            )
            db.session.add(user_to_create)
            db.session.commit()
            login_user(user_to_create)
            flash(f'{user_to_create.username}成功注册！！', category='success')
            return redirect(url_for('index_page'))
        except IntegrityError:
            db.session.rollback()
            flash("邮箱已存在", category="danger")
    # 处理表单验证错误（无论是否提交成功）
    if form.errors:
        for field_name, err_msgs in form.errors.items():
            for err_msg in err_msgs:
                print(f"Field: {field_name}, Error: {err_msg}")
                if 'Username already exists' in err_msg and 'Field must be equal to' not in err_msg:
                    flash("用户名已经存在!", category="danger")
                elif 'Field must be equal to' in err_msg and 'Username already exists' not in err_msg:
                    flash("两次密码输入不相同!", category="danger")
                elif 'Username already exists' in err_msg and 'Field must be equal to'  in err_msg:
                    flash("用户名已经存在,两次密码输入不相同!", category="danger")
                else:
                    flash(f"{err_msg}", category="danger")
    # 统一返回渲染的模板（无论是否有错误）
    return render_template('register.html', form=form)

# ----------------------------------------------------------------------------------------------------------------------
# 用户登录部分
@app.route('/login',methods=['GET','POST'])
def login_page():
     form = LoginForm()
     if form.validate_on_submit():
          attempted_user = User.query.filter_by(username=form.username.data).first()
          if attempted_user and attempted_user.check_password_correction(
               attempted_password=form.password.data                     # 确定
               ):
                login_user(attempted_user)
                flash(
                    f'用户{attempted_user.username}成功登录',category='success'
                )
                return redirect(url_for('market_page'))
          else:
               flash('密码错误或者用户不存在',category='danger')
     return render_template('login.html',form=form)

# doctor：管理员登录部分
@app.route('/doctor_login', methods=['GET', 'POST'])
def doctor_login_page():
    form = Doctor_LoginForm()
    if form.validate_on_submit():
        admin_user = Doctor.query.filter_by(doctor_name=form.doctor_name.data).first()
        if admin_user and admin_user.check_password_correction(
                attempted_password=form.doctor_id_number.data):
            login_user(admin_user)
            flash(f'欢迎 {admin_user.doctor_name} 医生', category='success')
            return redirect(url_for('doctor_page'))
        else:
            flash('密码错误或者用户不存在', category='danger')
    return render_template('doctor_login.html', form=form)
# 管理员主界面

@app.route('/admin_home')
@login_required
def doctor_page():
    item_count = Item.query.count()
    user_count = User.query.count()
    doctor_count = Doctor.query.count()
    comment_count = Comment.query.count()
    user_comment_counts = db.session.query(User.id, User.username, db.func.count(Comment.id).label('comment_count')) \
    .join(Comment, User.id == Comment.user_id) \
    .group_by(User.id, User.username) \
    .order_by(db.desc('comment_count')) \
    .all()
    # print(user_comment_counts)
    return render_template('doctor_home.html',item_count=item_count,user_count=user_count,doctor_count=doctor_count,comment_count= comment_count,user_comment_counts=user_comment_counts)

@app.route('/profile')
@login_required
def profile():
    if isinstance(current_user, User):
        return  f'当前登录用户是 User: {current_user.username}'
    elif isinstance(current_user, Doctor):
         return  f'当前登录用户是 Doctor: {current_user.doctor_name}'
    else:
        return  '未登录用户'
# -----------------------------------------------------------------------------------------------------------------------
# 用户登出部分
@app.route("/logout")
@login_required
def logout_page(): 
    logout_user()
    flash("已经成功退出登录", category="info")
    return redirect(url_for('index_page'))

# -----------------------------------------------------------------------------------------------------------------------
# 用户个人信息部分
@app.route("/user_table")
@login_required
def user_table_page():
    users = User.query.all()
    user_count = User.query.count()
    return render_template('user_table.html', users=users,user_count=user_count)

# -----------------------------------------------------------------------------------------------------------------------
# 评论系统当前药物显示
@app.route('/outlook',methods=['GET','POST'])
def outlook_page():
    # item_name = Item.query.filter_by(id=Item.id).first()
    items = Item.query.filter_by(name="蒙脱石散").first()
    comment = Comment.query.filter_by(item_id=items.id).order_by(Comment.created_at.desc()).all()
    return render_template('outlook.html',item=items,comments=comment)

@app.route('/doctor_outlook',methods=['GET','POST'])
def doctor_outlook():
    items = Item.query.filter_by(name="蒙脱石散").first()
    comment = Comment.query.filter_by(item_id=items.id).order_by(Comment.created_at.desc()).all()
    return render_template('doctor_outlook.html',item=items,comments=comment)



@app.route('/comments/<int:item_id>',methods=['GET','POST'])
def comments_page(item_id):
    # items = Item.query.all()
    items = Item.query.filter_by(id=item_id).first()
    comments = Comment.query.filter_by(item_id=items.id).order_by(Comment.created_at.desc()).all()
    comment_count = Comment.query.filter_by(item_id=item_id).count()
    return render_template('comment.html',item=items,comments=comments,comment_count=comment_count)

@app.route('/item/<int:item_id>')  # 定义货物的view视图
def view_item(item_id):
    item = Item.query.get_or_404(item_id)
    comments = Comment.query.filter_by(item_id=item_id).order_by(Comment.created_at.desc()).all()
    return render_template('item_details.html', item=item, comments=comments)
# 增加评论系统
@app.route('/api/comments/<int:item_id>', methods=['POST'])
@login_required
def post_comment(item_id):
    data = request.get_json()
    comment_text = data.get('comment_text')
    item_id = item_id

    if not comment_text:
        return jsonify({'message': '评论内容不能为空'}), 400
    if not item_id:
        return jsonify({'message': '物品ID不能为空'}), 400

    try:
        item_id = int(item_id) # 尝试将 item_id 转换为整数
        item = Item.query.get(item_id)
        if not item:
            return jsonify({'message': '指定的物品不存在'}), 404
    except ValueError:
        return jsonify({'message': '物品ID格式不正确'}), 400

    new_comment = Comment(
        comment_text=comment_text,
        user_id=current_user.id,
        item_id=item_id
    )
    db.session.add(new_comment)
    db.session.commit()

    return jsonify({
        'id': new_comment.id,
        'author_name': current_user.username,
        'comment_text': new_comment.comment_text,
        'created_at': new_comment.created_at.isoformat()
    }), 201
# 删除评论
@app.route('/api/comments/<int:comment_id>', methods=['DELETE'])
@login_required
def delete_comment(comment_id):
    comment = Comment.query.get_or_404(comment_id)
    if comment.user_id != current_user.id:
        return jsonify({'message': '你没有权限删除这个评论'}), 403

    db.session.delete(comment)
    db.session.commit()
    return jsonify({'message': '你还是删除了你的真心好评'}), 200
# -----------------------------------------------------------------------------------------------------------------------
# 更新货物
@app.route('/update_item/<int:item_id>', methods=['GET', 'POST'])
@login_required
def update_item(item_id):
    item = Item.query.get_or_404(item_id)
    # if current_user.id == current_user.admin or item.owner == current_user.id:
    # # 判断是否是管理员或者物品的拥有者
    if current_user.doctor_id_number:   # 有这个属性才行
        if request.method == 'POST':
            item.name = request.form.get('item_name')
            item.price = request.form.get('item_price')
            item.barcode = request.form.get('item_barcode')
            item.quantity = request.form.get('item_quantity')
            item.description = request.form.get('item_description')
            db.session.commit()
            flash(f"成功更新物品: {item.name}", category="success")
            return redirect(url_for('doctor_outlook'))
        return render_template('update_item.html', item=item) # 渲染更新表单
    else:
        flash("你不是医生还想要更新药品", category="danger")
        return redirect(url_for('market_page'))
# 删除货物

@app.route('/delete_item/<int:item_id>', methods=['POST','GET'])
@login_required
def delete_item(item_id):
    item = Item.query.get_or_404(item_id)
    if current_user.doctor_id_number:
        db.session.delete(item)
        db.session.commit()
        flash(f"成功删除物品: {item.name}", category="success")
    else:
        flash("你没有权限删除这个物品", category="danger")
    return redirect(url_for('doctor_outlook'))



# @app.route('/item/<int:item_id>')  # 定义货物的view视图
# def view_item(item_id):
#     item = Item.query.get_or_404(item_id)
#     comments = Comment.query.filter_by(item_id=item_id).order_by(Comment.created_at.desc()).all()
#     return render_template('item_details.html', item=item, comments=comments)

# -----------------------------------------------------------------------------------------------------------------------
# 创建管理员账号
@app.route('/admin',methods=['GET','POST'])
@login_required
def admin_page():
    doctor_form = DoctorForm()
    if doctor_form.validate_on_submit():
        try:
            doctor_to_create = Doctor(
                doctor_name=doctor_form.doctor_name.data,
                doctor_id_number=doctor_form.doctor_id_number.data,
                doctor_phone=doctor_form.doctor_phone.data,
                doctor_email=doctor_form.doctor_email.data
            )
            db.session.add(doctor_to_create)
            db.session.commit()
            # login_user(doctor_to_create)
            flash(f'{doctor_to_create.doctor_name}医生', category='success')
            return redirect(url_for('doctor_page'))
        except IntegrityError:
            db.session.rollback()
            flash("该用户已存在", category="danger")
    if doctor_form.errors:
        for field_name, err_msgs in doctor_form.errors.items():
            for err_msg in err_msgs:
                print(f"Field: {field_name}, Error: {err_msg}")
                if 'Username already exists' in err_msg and 'Field must be equal to' not in err_msg:
                    flash("用户名已经存在!", category="danger")
                elif 'Field must be equal to' in err_msg and 'Username already exists' not in err_msg:
                    flash("两次密码输入不相同!", category="danger")
                elif 'Username already exists' in err_msg and 'Field must be equal to'  in err_msg:
                    flash("用户名已经存在,两次密码输入不相同", category="danger")
                else:
                    flash(f"{err_msg}", category="danger")
    return render_template('doctor_register.html', doctor_form=doctor_form)


# -----------------------------------------------------------------------------------------------------------------------
@app.route('/buy/<int:item_id>', methods=['POST'])
@login_required
def buy_item(item_id):
    item = Item.query.get_or_404(item_id)
    quantity = request.form.get('quantity', type=int, default=1)

    try:
        item.buy(current_user, quantity)
        return jsonify({'message': f'成功购买 {quantity} 个 {item.name}！'})
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    




@app.route('/add_item', methods=['GET', 'POST'])
@login_required
def add_item():
    form = AddItemForm()
    if form.validate_on_submit():
        try:
            item_to_create = Item(
                name=form.item_name.data,
                price=form.item_price.data,
                barcode=form.item_barcode.data,
                description=form.item_description.data
            )
            db.session.add(item_to_create)
            db.session.commit()
            flash(f'{item_to_create.name} 成功添加！！', category='success')
            return redirect(url_for('doctor_outlook'))  # 替换为你的管理员页面路由
        except IntegrityError:
            db.session.rollback()
            flash("添加药品失败，可能条形码或名称已存在", category="danger")

    if form.errors:
        for field_name, err_msgs in form.errors.items():
            for err_msg in err_msgs:
                print(f"Field: {field_name}, Error: {err_msg}")
                if '药品名称已经存在' in err_msg and '药品条形码已经存在' not in err_msg:
                    flash("药品名称已经存在!", category="danger")
                elif '药品条形码已经存在' in err_msg and '药品名称已经存在' not in err_msg:
                    flash("药品条形码已经存在!", category="danger")
                elif '药品名称已经存在' in err_msg and '药品条形码已经存在' in err_msg:
                    flash("药品名称和条形码均已存在!", category="danger")
                else:
                    flash(f"{err_msg}", category="danger")
    return render_template('doctor_add_item.html', form=form)


# @app.template_filter('add_hours')
# def add_hours_filter(dt, hours):
#     return dt + timedelta(hours=hours)

# app.jinja_env.filters['add_hours'] = add_hours_filter