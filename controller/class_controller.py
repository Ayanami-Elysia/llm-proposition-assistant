from flask import Blueprint, jsonify, request
import logging

from service.class_service import ClassService
from utils.response import success

logger = logging.getLogger(__name__)

class_bp = Blueprint("class", __name__)
class_service = ClassService()


@class_bp.route("/options", methods=["GET"])
def get_class_options():
    """获取班级选项"""
    keyword = request.args.get("keyword", "").strip()
    data = class_service.get_class_options(keyword)
    logger.info("获取班级选项成功")
    return jsonify(success(data, "获取班级选项成功"))
