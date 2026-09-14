from flask import Blueprint, jsonify, request, session
import logging

from service.user_service import UserService
from utils.auth_utils import admin_required, get_current_user, set_user_session
from utils.response import convert_pagination_params, error, page_response, success

logger = logging.getLogger(__name__)

user_bp = Blueprint("user", __name__)
user_service = UserService()


@user_bp.route("/list", methods=["GET"])
@admin_required
def get_user_list():
    """获取用户列表"""
    try:
        page, limit = convert_pagination_params(request.args)
        keyword = request.args.get("keyword", "")
        role = request.args.get("role", "")
        status = request.args.get("status", "")
        users, total = user_service.get_user_list(page, limit, keyword, role, status)
        logger.info(f"获取用户列表成功，共 {total} 条记录")
        return jsonify(page_response(users, total, page, limit))
    except Exception as exc:
        logger.error(f"获取用户列表异常: {exc}")
        return jsonify(error("获取用户列表失败"))


@user_bp.route("/<int:user_id>", methods=["GET"])
def get_user_detail(user_id: int):
    """获取用户详情"""
    try:
        current_user = get_current_user()
        if current_user["role"] != "admin" and current_user["id"] != user_id:
            return jsonify(error("无权限访问", 403))

        user = user_service.get_user_by_id(user_id)
        if user:
            return jsonify(success(user, "获取用户信息成功"))
        return jsonify(error("用户不存在"))
    except Exception as exc:
        logger.error(f"获取用户详情异常: {exc}")
        return jsonify(error("获取用户信息失败"))


@user_bp.route("/<int:user_id>", methods=["PUT"])
def update_user(user_id: int):
    """更新用户信息"""
    try:
        current_user = get_current_user()
        data = request.get_json()

        if current_user["role"] != "admin" and current_user["id"] != user_id:
            return jsonify(error("无权限修改", 403))

        if current_user["role"] != "admin":
            data.pop("role", None)
            data.pop("status", None)

        result = user_service.update_user(user_id, data)
        if result:
            if current_user["id"] == user_id:
                user = user_service.get_user_by_id(user_id)
                if user:
                    set_user_session(user)
            logger.info(f"用户 {user_id} 信息更新成功")
            return jsonify(success(None, "更新成功"))
        return jsonify(error("更新失败"))
    except ValueError as exc:
        logger.error(f"更新用户信息校验异常: {exc}")
        return jsonify(error(str(exc)))
    except Exception as exc:
        logger.error(f"更新用户信息异常: {exc}")
        return jsonify(error("更新失败"))


@user_bp.route("/<int:user_id>", methods=["DELETE"])
@admin_required
def delete_user(user_id: int):
    """删除用户"""
    try:
        current_user = get_current_user()
        if current_user["id"] == user_id:
            return jsonify(error("不能删除自己的账号"))

        result = user_service.delete_user(user_id)
        if result:
            logger.info(f"用户 {user_id} 删除成功")
            return jsonify(success(None, "删除成功"))
        return jsonify(error("删除失败"))
    except Exception as exc:
        logger.error(f"删除用户异常: {exc}")
        return jsonify(error("删除失败"))


@user_bp.route("/change-password", methods=["POST"])
def change_password():
    """修改密码"""
    try:
        current_user = get_current_user()
        data = request.get_json()
        old_password = data.get("oldPassword") or data.get("old_password")
        new_password = data.get("newPassword") or data.get("new_password")

        if not old_password or not new_password:
            return jsonify(error("原密码和新密码不能为空"))

        result = user_service.change_password(current_user["id"], old_password, new_password)
        if result:
            logger.info(f"用户 {current_user['username']} 修改密码成功")
            return jsonify(success(None, "密码修改成功"))
        return jsonify(error("原密码错误"))
    except Exception as exc:
        logger.error(f"修改密码异常: {exc}")
        return jsonify(error("修改密码失败"))


@user_bp.route("/upload-avatar", methods=["POST"])
def upload_avatar():
    """上传头像"""
    try:
        current_user = get_current_user()
        if "file" not in request.files:
            return jsonify(error("没有选择文件"))

        file = request.files["file"]
        if file.filename == "":
            return jsonify(error("没有选择文件"))

        avatar_url = user_service.upload_avatar(current_user["id"], file)
        if avatar_url:
            logger.info(f"用户 {current_user['username']} 上传头像成功")
            return jsonify(success({"avatar_url": avatar_url}, "头像上传成功"))
        return jsonify(error("头像上传失败"))
    except Exception as exc:
        logger.error(f"上传头像异常: {exc}")
        return jsonify(error("头像上传失败"))


@user_bp.route("/profile", methods=["GET"])
def get_profile():
    """获取当前用户个人信息"""
    try:
        current_user = get_current_user()
        if current_user:
            user_detail = user_service.get_user_by_id(current_user["id"])
            return jsonify(success(user_detail, "获取个人信息成功"))
        return jsonify(error("用户未登录", 401))
    except Exception as exc:
        logger.error(f"获取个人信息异常: {exc}")
        return jsonify(error("获取个人信息失败"))


@user_bp.route("/add", methods=["POST"])
@admin_required
def add_user():
    """添加用户"""
    try:
        data = request.get_json()
        required_fields = ["username", "password", "nickname"]
        for field in required_fields:
            if not data.get(field):
                return jsonify(error(f"{field}不能为空"))

        result = user_service.add_user(data)
        if result:
            logger.info(f"管理员添加用户 {data['username']} 成功")
            return jsonify(success(None, "添加用户成功"))
        return jsonify(error("添加用户失败，用户名可能已存在"))
    except ValueError as exc:
        logger.error(f"添加用户校验异常: {exc}")
        return jsonify(error(str(exc)))
    except Exception as exc:
        logger.error(f"添加用户异常: {exc}")
        return jsonify(error("添加用户失败"))
