from flask import Flask, send_from_directory, request, redirect, url_for, session
import os
from config.config import *

# 创建Flask应用
app = Flask(__name__)

# 配置应用
app.config.from_object('config.config')

# 确保上传目录存在
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# 注册蓝图
from controller.auth_controller import auth_bp
from controller.user_controller import user_bp
from controller.upload_controller import upload_bp
from controller.announcement_bp import announcement_bp
from controller.dashboard_controller import dashboard_bp
from controller.drug_bp import drug_bp
from controller.knowledge_bp import knowledge_bp
from controller.question_bp import question_bp
from controller.paper_bp import paper_bp
from controller.exam_record_bp import exam_record_bp
from controller.class_controller import class_bp

app.register_blueprint(auth_bp, url_prefix='/api/auth')
app.register_blueprint(user_bp, url_prefix='/api/user')
app.register_blueprint(upload_bp, url_prefix='/open')
app.register_blueprint(announcement_bp, url_prefix='/api/announcement')
app.register_blueprint(dashboard_bp, url_prefix='/api/dashboard')
app.register_blueprint(drug_bp, url_prefix='/api/drug')
app.register_blueprint(knowledge_bp, url_prefix='/api/knowledge')
app.register_blueprint(question_bp, url_prefix='/api/question')
app.register_blueprint(paper_bp, url_prefix='/api/paper')
app.register_blueprint(exam_record_bp, url_prefix='/api/exam_record')
app.register_blueprint(class_bp, url_prefix='/api/class')

# 页面路由分发
@app.route('/')
def index():
    """首页重定向到前台"""
    return redirect('/front/index.html')

@app.route('/login')
def login_page():
    """登录页面"""
    return send_from_directory('templates', 'login.html')

@app.route('/register')
def register_page():
    """注册页面"""
    return send_from_directory('templates', 'register.html')

@app.route('/front/<path:filename>')
def front_page(filename):
    """前台页面分发"""
    return send_from_directory('templates/front', filename)

@app.route('/admin/<path:filename>')
def admin_page(filename):
    """后台页面分发"""
    return send_from_directory('templates/admin', filename)

@app.route('/static/<path:filename>')
def static_files(filename):
    """静态文件分发"""
    return send_from_directory('static', filename)

@app.route('/upload/<path:filename>')
def upload_files(filename):
    """上传文件访问"""
    return send_from_directory('upload', filename)


if __name__ == '__main__':
    app.run(debug=DEBUG, host='0.0.0.0', port=5001)
