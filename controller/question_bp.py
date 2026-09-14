"""
题库管理 蓝图
"""
from flask import Blueprint, jsonify
from controller.question_controller import QuestionController

# 创建蓝图
question_bp = Blueprint('question', __name__)

# 后台管理接口
@question_bp.route('/admin/list', methods=['GET'])
def admin_question_list():
    result = QuestionController.admin_list()
    return jsonify(result)

@question_bp.route('/admin/detail', methods=['GET'])
def admin_question_detail():
    result = QuestionController.admin_detail()
    return jsonify(result)

@question_bp.route('/admin/create', methods=['POST'])
def admin_question_create():
    result = QuestionController.admin_create()
    return jsonify(result)

@question_bp.route('/admin/update', methods=['POST'])
def admin_question_update():
    result = QuestionController.admin_update()
    return jsonify(result)

@question_bp.route('/admin/delete', methods=['GET'])
def admin_question_delete():
    result = QuestionController.admin_delete()
    return jsonify(result)

@question_bp.route('/admin/toggle-status', methods=['GET'])
def admin_question_toggle_status():
    result = QuestionController.admin_toggle_status()
    return jsonify(result)

# AI智能命题接口
@question_bp.route('/admin/ai/generate', methods=['POST'])
def ai_generate_questions():
    """AI智能生成题目"""
    result = QuestionController.ai_generate()
    return jsonify(result)

@question_bp.route('/admin/ai/evaluate-difficulty', methods=['GET'])
def ai_evaluate_difficulty():
    """AI评估题目难度"""
    result = QuestionController.ai_evaluate_difficulty()
    return jsonify(result)

@question_bp.route('/admin/ai/analyze-knowledge', methods=['GET'])
def ai_analyze_knowledge():
    """AI分析题目知识点"""
    result = QuestionController.ai_analyze_knowledge()
    return jsonify(result)

@question_bp.route('/admin/ai/batch-save', methods=['POST'])
def ai_batch_save():
    """批量保存AI生成的题目"""
    result = QuestionController.ai_batch_save()
    return jsonify(result)

