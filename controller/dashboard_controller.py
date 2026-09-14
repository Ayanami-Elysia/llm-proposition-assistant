from flask import Blueprint, jsonify, request

from service.dashboard_service import DashboardService
from utils.auth_utils import get_current_user
from utils.response import error, success

dashboard_bp = Blueprint('dashboard', __name__)


@dashboard_bp.route('/overview', methods=['GET'])
def get_dashboard_overview():
    """获取仪表盘总览数据"""
    try:
        data = DashboardService.get_dashboard_overview()
        return jsonify(success(data))
    except Exception as exc:
        return jsonify(error(f"获取仪表盘数据失败: {str(exc)}"))


@dashboard_bp.route('/user-stats', methods=['GET'])
def get_user_statistics():
    """获取用户统计数据"""
    try:
        data = DashboardService.get_user_statistics()
        return jsonify(success(data))
    except Exception as exc:
        return jsonify(error(f"获取用户统计失败: {str(exc)}"))


@dashboard_bp.route('/user-trend', methods=['GET'])
def get_user_trend():
    """获取用户趋势数据"""
    try:
        days = request.args.get('days', 30, type=int)
        data = DashboardService.get_user_trend_data(days)
        return jsonify(success(data))
    except Exception as exc:
        return jsonify(error(f"获取用户趋势失败: {str(exc)}"))


@dashboard_bp.route('/role-distribution', methods=['GET'])
def get_role_distribution():
    """获取角色分布数据"""
    try:
        data = DashboardService.get_role_distribution()
        return jsonify(success(data))
    except Exception as exc:
        return jsonify(error(f"获取角色分布失败: {str(exc)}"))


@dashboard_bp.route('/recent-activities', methods=['GET'])
def get_recent_activities():
    """获取最近活动数据"""
    try:
        limit = request.args.get('limit', 10, type=int)
        data = DashboardService.get_recent_activities(limit)
        return jsonify(success(data))
    except Exception as exc:
        return jsonify(error(f"获取最近活动失败: {str(exc)}"))


@dashboard_bp.route('/exam-options', methods=['GET'])
def get_exam_options():
    """获取考试选项"""
    try:
        current_user = get_current_user()
        data = DashboardService.get_exam_options(current_user)
        return jsonify(success(data))
    except Exception as exc:
        return jsonify(error(f"获取考试选项失败: {str(exc)}"))


@dashboard_bp.route('/subject-options', methods=['GET'])
def get_subject_options():
    """获取学科选项"""
    try:
        data = DashboardService.get_subject_options()
        return jsonify(success(data))
    except Exception as exc:
        return jsonify(error(f"获取学科选项失败: {str(exc)}"))


@dashboard_bp.route('/exam-statistics', methods=['GET'])
def get_exam_statistics():
    """获取考试统计数据"""
    try:
        current_user = get_current_user()
        paper_id = request.args.get('paperId', type=int)
        subject = request.args.get('subject', '').strip() or None
        data = DashboardService.get_exam_statistics(current_user, paper_id, subject)
        return jsonify(success(data))
    except Exception as exc:
        return jsonify(error(f"获取考试统计失败: {str(exc)}"))


@dashboard_bp.route('/exam-trend', methods=['GET'])
def get_exam_trend():
    """获取考试趋势数据"""
    try:
        current_user = get_current_user()
        days = request.args.get('days', 30, type=int)
        paper_id = request.args.get('paperId', type=int)
        subject = request.args.get('subject', '').strip() or None
        data = DashboardService.get_exam_trend_data(days, current_user, paper_id, subject)
        return jsonify(success(data))
    except Exception as exc:
        return jsonify(error(f"获取考试趋势失败: {str(exc)}"))


@dashboard_bp.route('/paper-usage', methods=['GET'])
def get_paper_usage():
    """获取试卷使用情况"""
    try:
        current_user = get_current_user()
        paper_id = request.args.get('paperId', type=int)
        subject = request.args.get('subject', '').strip() or None
        data = DashboardService.get_paper_usage_statistics(current_user, paper_id, subject)
        return jsonify(success(data))
    except Exception as exc:
        return jsonify(error(f"获取试卷使用统计失败: {str(exc)}"))


@dashboard_bp.route('/exam-status-distribution', methods=['GET'])
def get_exam_status_distribution():
    """获取考试状态分布"""
    try:
        current_user = get_current_user()
        paper_id = request.args.get('paperId', type=int)
        subject = request.args.get('subject', '').strip() or None
        data = DashboardService.get_exam_status_distribution(current_user, paper_id, subject)
        return jsonify(success(data))
    except Exception as exc:
        return jsonify(error(f"获取考试状态分布失败: {str(exc)}"))


@dashboard_bp.route('/score-distribution', methods=['GET'])
def get_score_distribution():
    """获取分数分布统计"""
    try:
        current_user = get_current_user()
        paper_id = request.args.get('paperId', type=int)
        subject = request.args.get('subject', '').strip() or None
        data = DashboardService.get_score_distribution(current_user, paper_id, subject)
        return jsonify(success(data))
    except Exception as exc:
        return jsonify(error(f"获取分数分布统计失败: {str(exc)}"))


@dashboard_bp.route('/question-type-statistics', methods=['GET'])
def get_question_type_statistics():
    """获取题型统计"""
    try:
        current_user = get_current_user()
        paper_id = request.args.get('paperId', type=int)
        subject = request.args.get('subject', '').strip() or None
        data = DashboardService.get_question_type_statistics(current_user, paper_id, subject)
        return jsonify(success(data))
    except Exception as exc:
        return jsonify(error(f"获取题型统计失败: {str(exc)}"))


@dashboard_bp.route('/teacher-teaching-stats', methods=['GET'])
def get_teacher_teaching_stats():
    """获取教师教学情况统计"""
    try:
        current_user = get_current_user()
        subject = request.args.get('subject', '').strip() or None
        data = DashboardService.get_teacher_teaching_statistics(current_user, subject)
        return jsonify(success(data))
    except Exception as exc:
        return jsonify(error(f"获取教师教学情况失败: {str(exc)}"))
