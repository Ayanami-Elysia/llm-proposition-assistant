from flask import Blueprint, jsonify, request
import logging

from service.auth_service import AuthService
from utils.auth_utils import clear_user_session, get_current_user, set_user_session
from utils.response import error, success

logger = logging.getLogger(__name__)

auth_bp = Blueprint("auth", __name__)
auth_service = AuthService()


@auth_bp.route("/login", methods=["POST"])
def login():
    """用户登录"""
    try:
        data = request.get_json()
        username = data.get("username")
        password = data.get("password")
        role = data.get("role")

        if not username or not password:
            return jsonify(error("用户名和密码不能为空"))
        if not role:
            return jsonify(error("请选择登录角色"))

        user = auth_service.login(username, password, role)
        if not user:
            return jsonify(error("用户名或密码错误"))

        set_user_session(user)
        if user["role"] == "user":
            redirect_url = "/front/knowledge.html"
        elif user["role"] == "doctor":
            redirect_url = "/admin/question.html"
        else:
            redirect_url = "/admin/index.html"

        logger.info(f"用户 {username} 登录成功，角色: {user['role']}")
        return jsonify(success({
            "user": user,
            "redirect_url": redirect_url
        }, "登录成功"))
    except Exception as exc:
        logger.error(f"登录异常: {exc}")
        return jsonify(error("登录失败，请稍后重试"))


@auth_bp.route("/register", methods=["POST"])
def register():
    """用户注册"""
    try:
        data = request.get_json()
        username = data.get("username")
        password = data.get("password")
        nickname = data.get("nickname")
        email = data.get("email")
        phone = data.get("phone")
        role = data.get("role")
        class_name = data.get("class_name")
        grade = data.get("grade")

        if not username or not password:
            return jsonify(error("用户名和密码不能为空"))
        if not role:
            return jsonify(error("请选择注册角色"))

        result = auth_service.register(
            username,
            password,
            nickname,
            email,
            phone,
            role,
            class_name,
            grade
        )
        if result:
            logger.info(f"用户 {username} 注册成功")
            return jsonify(success(None, "注册成功"))
        return jsonify(error("注册失败，用户名可能已存在"))
    except ValueError as exc:
        logger.error(f"注册校验异常: {exc}")
        return jsonify(error(str(exc)))
    except Exception as exc:
        logger.error(f"注册异常: {exc}")
        return jsonify(error("注册失败，请稍后重试"))


@auth_bp.route("/logout", methods=["POST"])
def logout():
    """用户登出"""
    try:
        clear_user_session()
        logger.info("用户登出成功")
        return jsonify(success(None, "登出成功"))
    except Exception as exc:
        logger.error(f"登出异常: {exc}")
        return jsonify(error("登出失败"))


@auth_bp.route("/userinfo", methods=["GET"])
def get_user_info():
    """获取当前用户信息"""
    try:
        user = get_current_user()
        if user:
            return jsonify(success(user, "获取用户信息成功"))
        return jsonify(error("用户未登录", 401))
    except Exception as exc:
        logger.error(f"获取用户信息异常: {exc}")
        return jsonify(error("获取用户信息失败"))


@auth_bp.route("/check-auth", methods=["GET"])
def check_auth():
    """检查用户认证状态"""
    try:
        user = get_current_user()
        if user:
            if user["role"] == "user":
                available_pages = ["/front/index.html", "/front/about.html", "/front/profile.html"]
            else:
                available_pages = ["/admin/index.html", "/admin/users.html", "/admin/profile.html"]

            return jsonify(success({
                "authenticated": True,
                "user": user,
                "available_pages": available_pages
            }, "用户已认证"))

        return jsonify(success({
            "authenticated": False,
            "user": None,
            "available_pages": ["/login", "/register"]
        }, "用户未认证"))
    except Exception as exc:
        logger.error(f"检查认证状态异常: {exc}")
        return jsonify(error("检查认证状态失败"))
