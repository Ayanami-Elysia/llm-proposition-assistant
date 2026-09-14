"""
考试记录管理 蓝图
"""
from flask import Blueprint, jsonify
from controller.exam_record_controller import ExamRecordController

# 创建蓝图
exam_record_bp = Blueprint('exam_record', __name__)

# 后台管理接口
@exam_record_bp.route('/admin/list', methods=['GET'])
def admin_exam_record_list():
    result = ExamRecordController.admin_list()
    return jsonify(result)

@exam_record_bp.route('/admin/detail', methods=['GET'])
def admin_exam_record_detail():
    result = ExamRecordController.admin_detail()
    return jsonify(result)

@exam_record_bp.route('/admin/answers', methods=['GET'])
def admin_get_answers():
    result = ExamRecordController.admin_get_answers()
    return jsonify(result)

@exam_record_bp.route('/admin/review-exam', methods=['POST'])
def admin_review_exam():
    result = ExamRecordController.admin_review_exam()
    return jsonify(result)

@exam_record_bp.route('/admin/review-answer', methods=['POST'])
def admin_review_answer():
    result = ExamRecordController.admin_review_answer()
    return jsonify(result)

@exam_record_bp.route('/admin/delete', methods=['GET'])
def admin_exam_record_delete():
    result = ExamRecordController.admin_delete()
    return jsonify(result)

# 前台接口
@exam_record_bp.route('/front/start-exam', methods=['GET'])
def front_start_exam():
    result = ExamRecordController.front_start_exam()
    return jsonify(result)

@exam_record_bp.route('/front/get-questions', methods=['GET'])
def front_get_questions():
    result = ExamRecordController.front_get_questions()
    return jsonify(result)

@exam_record_bp.route('/front/save-answer', methods=['POST'])
def front_save_answer():
    result = ExamRecordController.front_save_answer()
    return jsonify(result)

@exam_record_bp.route('/front/submit-exam', methods=['POST'])
def front_submit_exam():
    result = ExamRecordController.front_submit_exam()
    return jsonify(result)

@exam_record_bp.route('/front/detail', methods=['GET'])
def front_exam_record_detail():
    result = ExamRecordController.front_detail()
    return jsonify(result)

@exam_record_bp.route('/front/list', methods=['GET'])
def front_exam_record_list():
    result = ExamRecordController.front_list()
    return jsonify(result)

@exam_record_bp.route('/front/get-answers', methods=['GET'])
def front_get_answers():
    result = ExamRecordController.front_get_answers()
    return jsonify(result)

