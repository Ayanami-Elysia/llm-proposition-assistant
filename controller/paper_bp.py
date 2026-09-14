"""
试卷管理 蓝图
"""
from flask import Blueprint, jsonify
from controller.paper_controller import PaperController

# 创建蓝图
paper_bp = Blueprint('paper', __name__)

# 后台管理接口
@paper_bp.route('/admin/list', methods=['GET'])
def admin_paper_list():
    result = PaperController.admin_list()
    return jsonify(result)

@paper_bp.route('/admin/detail', methods=['GET'])
def admin_paper_detail():
    result = PaperController.admin_detail()
    return jsonify(result)

@paper_bp.route('/admin/create', methods=['POST'])
def admin_paper_create():
    result = PaperController.admin_create()
    return jsonify(result)

@paper_bp.route('/admin/update', methods=['POST'])
def admin_paper_update():
    result = PaperController.admin_update()
    return jsonify(result)

@paper_bp.route('/admin/delete', methods=['GET'])
def admin_paper_delete():
    result = PaperController.admin_delete()
    return jsonify(result)

@paper_bp.route('/admin/toggle-status', methods=['GET'])
def admin_paper_toggle_status():
    result = PaperController.admin_toggle_status()
    return jsonify(result)

@paper_bp.route('/admin/questions', methods=['GET'])
def admin_paper_questions():
    result = PaperController.admin_get_questions()
    return jsonify(result)

@paper_bp.route('/admin/add-question', methods=['POST'])
def admin_paper_add_question():
    result = PaperController.admin_add_question()
    return jsonify(result)

@paper_bp.route('/admin/remove-question', methods=['POST'])
def admin_paper_remove_question():
    result = PaperController.admin_remove_question()
    return jsonify(result)

@paper_bp.route('/admin/auto-generate', methods=['POST'])
def admin_paper_auto_generate():
    result = PaperController.admin_auto_generate()
    return jsonify(result)

# 前台接口（公开访问）
@paper_bp.route('/front/list', methods=['GET'])
def front_paper_list():
    result = PaperController.front_list()
    return jsonify(result)

@paper_bp.route('/front/detail', methods=['GET'])
def front_paper_detail():
    result = PaperController.front_detail()
    return jsonify(result)

