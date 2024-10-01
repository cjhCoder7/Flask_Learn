import os
from flask import Flask, request, render_template
from werkzeug.utils import secure_filename

app = Flask(__name__)


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["emailName"]
        password = request.form["password"]
        if username and password:
            if username == "admin@qq.com" and password == "123456":
                return render_template("login.html", message="Success")
            else:
                return render_template("login.html", message="Fail")
        else:
            return render_template(
                "login.html", message="Please enter both email and password"
            )
    else:
        return render_template("login.html")


@app.route("/upload", methods=["GET", "POST"])
def upload_file():
    # 配置上传目录
    path = os.path.join(os.path.dirname(__file__), "media/uploads/")
    if not os.path.exists(path):
        os.makedirs(path)
    # 在请求方法为POST时进行处理,文件上传为POST请求
    if request.method == "POST":
        files = request.files
        myfile = files["myfile"]
        if myfile:
            filename = secure_filename(myfile.filename)
            file_name = os.path.join(path, filename)
            myfile.save(file_name)
    return render_template("upload.html")
