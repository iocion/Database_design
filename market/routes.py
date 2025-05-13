# -*- coding: utf-8 -*-
from market import app
from flask import render_template,redirect,url_for,flash,get_flashed_messages, request,jsonify
from market.models import Item,User
from market.forms import RegisterForm,LoginForm,PurchaseItemForm,SellItemForm
from sqlalchemy.exc import IntegrityError
from market import db
from flask_login import login_user,login_required,logout_user,current_user
from openai import OpenAI  # 加入百度的大模型deepseekR8
import markdown
import re # 用来进行文本处理
# from mistralai.client import MistralClient




# 
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
                        p_item_object.buy(current_user)
                        flash(f"购买成功",category="success")
                    else:
                        missing_money = p_item_object.price-current_user.budget
                        flash(f"余额不足，还需要{missing_money}元",category="danger")
        # Sell Item logic
        sold_item = request.form.get('sold_item')
        s_item_object = Item.query.filter_by(name=sold_item).first()
        if s_item_object:
            if current_user.can_sell(s_item_object):
                s_item_object.sell(current_user)
                flash(f"恭喜你成功卖出{s_item_object.name}",category="success")
        return redirect(url_for('market_page'))  
    
    if request.method == 'GET':
        # if purchase_form.validate_on_submit():
        #     print(request.form.get('purchase_item'))
        items = Item.query.filter_by(owner=None)
        owned_items = Item.query.filter_by(owner=current_user.id)
        return render_template('market.html',items=items,purchase_form=purchase_form,owned_items=owned_items,selling_form=selling_form)
        


    # items = Item.query.filter_by(owner=None)
    # return render_template('market.html', items=items, purchase_form=purchase_form)




@app.route('/notion')
def notion_page():
    # 使用 SQLAlchemy Query API 查询所有用户
    item = Item.query.filter_by(name='阿莫西林').first()
    return render_template('notion.html',item=item)

@app.route('/register',methods=['GET','POST'])
def register_page():
    form = RegisterForm()
    if form.validate_on_submit():
        try:
                user_to_create= User(username=form.username.data,
                                    email_address=form.email_address.data,
                                    password=form.password1.data)
                db.session.add(user_to_create)
                db.session.commit()
                login_user(user_to_create)
                flash(
                    f'{user_to_create.username}成功注册！！',category='success'
                )
                return redirect(url_for('index_page'))
        except IntegrityError:
            db.session.rollback()
            # get_flashed_messages("Error: Email address already exists.")
            flash("这个邮箱已经存在了",category="danger")
            
    if form.errors !={}:    # if there are not errors from the validations -> return 'register.html'
        for err_msg in form.errors.values():
            if err_msg !={}:
                # 处理用户名已经存在
                if err_msg == ['Username already exists!!!']:
                     flash("用户名已经存在!",category="danger")
                # 处理两次密码输入不相同的情况
                else:
                    flash(f'两次密码输入不相同',category="danger")
    return render_template('register.html',form=form)



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

# It's a static website
# if we add vue ,js and css ,things will be different 

@app.route("/logout")
@login_required
def logout_page(): 
    logout_user()
    flash("已经成功退出登录", category="info")
    return redirect(url_for('index_page'))


@app.route("/game")
def game_page():
     return render_template("game.html")


@app.route("/just_for_fun")
# def just_for_fun_page():
#      return render_template("just_for_fun.html")
@login_required
def just_for_fun_page():
    # 使用 SQLAlchemy Query API 查询所有用户
    users = User.query.all()
    return render_template('just_for_fun.html', users=users)

