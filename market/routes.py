# -*- coding: utf-8 -*-
from market import app
from flask import render_template,redirect,url_for,flash,get_flashed_messages, request,jsonify
from market.models import Item,User,Comment
from market.forms import RegisterForm,LoginForm,PurchaseItemForm,SellItemForm,UpdateItemForm
from sqlalchemy.exc import IntegrityError
from market import db
from flask_login import login_user,login_required,logout_user,current_user
from openai import OpenAI  # 加入百度的大模型deepseekR8
import markdown
import re # 用来进行文本处理
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
        return render_template('storage.html',items=items,owned_items=owned_items)


# ---------------------------------------------------------------------------------------------------------------------------
# 市场交易的显示
@app.route('/market',methods=['GET','POST'])
@login_required
def market_page():
    # Purchase Item Logic
    selling_form = SellItemForm()
    purchase_form =PurchaseItemForm()
    if request.method =='POST': #解决js表单每一次跳出,request不能分清get和post方法
        purchased_item = request.form.get('purchase_item')
        p_item_object = Item.query.filter_by(name=purchased_item).first()
        if p_item_object:
                if current_user.can_purchase(p_item_object):    
                    if current_user.budget >= p_item_object.price:   # 判断金额是否大于budget
                        p_item_object.buy(current_user,p_item_object)
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
        items = Item.query.filter_by(owner=None)
        owned_items = Item.query.filter_by(owner=current_user.id)
        return render_template('market.html',items=items,purchase_form=purchase_form,owned_items=owned_items,selling_form=selling_form)
    
# ---------------------------------------------------------------------------------------------------------------------------
# 药品查询部分
@app.route('/api/query/<string:item_name>', methods=['GET', 'POST'])
def query_item(item_name):
    # 使用 SQLAlchemy 的 like() 方法进行模糊查询
    #  like()  方法: 用于在数据库中执行模式匹配查询。
    #  %:   表示可以匹配任何字符序列（包括空序列）。
    item = Item.query.filter(Item.name.like(f'%{item_name}%')).first()

    if item:
        return jsonify({
            'name': item.name,
            'price': item.price,
            'barcode': item.barcode,
            'description': item.description,
            'quantity': item.quantity
        })
    else:
        return jsonify({'error': '未找到相关药品'}), 404        

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
    return render_template('user_table.html', users=users)

# -----------------------------------------------------------------------------------------------------------------------
# 评论系统当前药物显示
@app.route('/notion',methods=['GET','POST'])
def notion_page():
    items = Item.query.all()
    items = Item.query.filter_by(name="蒙脱石散").first()
    comment = Comment.query.filter_by(item_id=items.id).order_by(Comment.created_at.desc()).all()
    # update_item_form = UpdateItemForm()
    # if update_item_form.validate_on_submit():
    #     try:
    #         item_to_insert = Item(
    #             name=update_item_form.item_name.data,
    #             price=update_item_form.item_price.data,
    #             barcode=update_item_form.item_barcode.data,
    #             description=update_item_form.item_description.data
    #         )
    #         db.session.add(item_to_insert)
    #         db.session.commit()
    #         login_user(item_to_insert)
    #         flash(f'{item_to_insert.data}成功录入', category='success')
    #         return redirect(url_for('index_page')) # 跳转页面
    #     except IntegrityError:
    #         db.session.rollback()
    #         flash("此药品已经已存在", category="danger")
    return render_template('notion.html',item=items,comments=comment)
# 增加评论系统
@app.route('/api/comments', methods=['POST'])
@login_required
def post_comment():
    data = request.get_json()
    comment_text = data.get('comment_text')
    item_id = 9
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
# @app.route('/api/comments/<int:comment_id>', methods=['DELETE'])
# @login_required
# def delete_comment(comment_id):
#     comment = Comment.query.get_or_404(comment_id)
#     if comment.user_id != current_user.id:
#         return jsonify({'message': '你没有权限删除这个评论'}), 403

#     db.session.delete(comment)
#     db.session.commit()
#     return jsonify({'message': '评论已删除'}), 200
# -----------------------------------------------------------------------------------------------------------------------
# 更新货物
@app.route('/update_item/<int:item_id>', methods=['GET', 'POST'])
@login_required
def update_item(item_id):
    item = Item.query.get_or_404(item_id)
    # if current_user.id == current_user.admin or item.owner == current_user.id:
    # # 判断是否是管理员或者物品的拥有者
    if True:
        if request.method == 'POST':
            item.name = request.form.get('item_name')
            item.price = request.form.get('item_price')
            item.barcode = request.form.get('item_barcode')
            item.quantity = request.form.get('item_quantity')
            item.description = request.form.get('item_description')
            db.session.commit()
            flash(f"成功更新物品: {item.name}", category="success")
            return redirect(url_for('market_page'))
        return render_template('update_item.html', item=item) # 渲染更新表单
    else:
        flash("你没有权限更新这个物品", category="danger")
        return redirect(url_for('market_page'))
# 删除货物

@app.route('/delete_item/<int:item_id>', methods=['POST'])
@login_required
def delete_item(item_id):
    item = Item.query.get_or_404(item_id)
    if item.owner == current_user.id:
        db.session.delete(item)
        db.session.commit()
        flash(f"成功删除物品: {item.name}", category="success")
    else:
        flash("你没有权限删除这个物品", category="danger")
    return redirect(url_for('market_page'))



# @app.route('/item/<int:item_id>')  # 定义货物的view视图
# def view_item(item_id):
#     item = Item.query.get_or_404(item_id)
#     comments = Comment.query.filter_by(item_id=item_id).order_by(Comment.created_at.desc()).all()
#     return render_template('item_details.html', item=item, comments=comments)



