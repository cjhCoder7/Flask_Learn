import os
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import and_

base_dir = os.path.abspath(os.path.dirname(__file__))
app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(
    base_dir, "data.sqlite"
)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_COMMIT_TEARDOWN"] = True
app.secret_key = "11223344"
db = SQLAlchemy(app)
# 实例化登录管理器对象
login_manager = LoginManager(app)
login_manager.login_view = "login"  # 验证失败跳转的页面
login_manager.session_protection = "strong"  # 会话保护的模式
login_manager.login_message = "欢迎回来"  # 用户重定向到登录页面时闪出的消息。


# 定义用户模型
class User(UserMixin, db.Model):
    __tablename__ = "tb_user"
    id = db.Column(db.Integer, comment="ID", primary_key=True, autoincrement=True)
    username = db.Column(db.String(30), unique=True, comment="用户名")
    password = db.Column(db.String(200), comment="密码")
    email = db.Column(db.String(30), unique=True, comment="邮箱")
    sex = db.Column(db.Integer, comment="性别")


# 用户认证的回调函数
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# 显示注册表单
@app.route("/reg", methods=["GET", "POST"])
def reg():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        email = request.form["email"]
        sex = request.form["sex"]
        # 检查用户名和邮箱是否已经存在
        existing_user = User.query.filter_by(username=username).first()
        existing_email = User.query.filter_by(email=email).first()

        if existing_user:
            flash('Usename Exist', 'danger')
            return render_template("reg.html")
        if existing_email:
            flash('Email Exist', 'danger')
            return render_template("reg.html")

        db.session.add(User(username=username, password=password, email=email, sex=sex))
        db.session.commit()
        return redirect(url_for("login"))
    return render_template("reg.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        user = User.query.filter(
            and_(User.username == username, User.password == password)
        ).first()
        if user:
            print(user)
            login_user(user)
            return redirect(url_for("index"))
        flash('Login Failed!', 'danger')
    return render_template("login.html")


# 显示主页
@app.route("/index")
@login_required
def index():
    users = User.query.all()
    return render_template("index.html", users=users)


# 用户注销
@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("login"))


@app.route("/edit/<int:user_id>", methods=["GET", "POST"])
@login_required
def edit(user_id):
    user = User.query.get_or_404(user_id)
    if request.method == "POST":
        new_username = request.form["username"]
        new_email = request.form["email"]
        new_password = request.form["password"]
        new_sex = request.form["sex"]

        # 检查是否有其他用户使用了相同的用户名或邮箱
        existing_user = User.query.filter(
            User.username == new_username, User.id != user_id
        ).first()
        existing_email = User.query.filter(
            User.email == new_email, User.id != user_id
        ).first()

        if existing_user:
            flash('Usename Exist', 'danger')
            return render_template("edit.html", user=user)
        if existing_email:
            flash('Email Exist', 'danger')
            return render_template("edit.html", user=user)

        # 更新用户信息
        user.username = new_username
        user.email = new_email
        user.password = new_password  # 假设直接保存明文密码，生产环境应使用哈希处理
        user.sex = new_sex
        db.session.commit()  # 提交数据库更新# 提交数据库更新
        return redirect(url_for("index"))  # 修改完成后返回首页
    return render_template("edit.html", user=user)


@app.route("/delete/<int:user_id>")
@login_required
def delete(user_id):
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    return redirect(url_for("index"))


with app.app_context():
    db.drop_all()
    db.create_all()

if __name__ == "__main__":
    app.run()
