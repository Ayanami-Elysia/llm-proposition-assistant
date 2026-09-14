"""
知识库管理 蓝图
"""
from flask import Blueprint, jsonify
from controller.knowledge_controller import KnowledgeController

# 创建蓝图
knowledge_bp = Blueprint('knowledge', __name__)

# 后台管理接口
@knowledge_bp.route('/admin/list', methods=['GET'])
def admin_knowledge_list():
    result = KnowledgeController.admin_list()
    return jsonify(result)

@knowledge_bp.route('/admin/detail', methods=['GET'])
def admin_knowledge_detail():
    result = KnowledgeController.admin_detail()
    return jsonify(result)

@knowledge_bp.route('/admin/create', methods=['POST'])
def admin_knowledge_create():
    result = KnowledgeController.admin_create()
    return jsonify(result)

@knowledge_bp.route('/admin/update', methods=['POST'])
def admin_knowledge_update():
    result = KnowledgeController.admin_update()
    return jsonify(result)

@knowledge_bp.route('/admin/delete', methods=['GET'])
def admin_knowledge_delete():
    result = KnowledgeController.admin_delete()
    return jsonify(result)

@knowledge_bp.route('/admin/toggle-status', methods=['GET'])
def admin_knowledge_toggle_status():
    result = KnowledgeController.admin_toggle_status()
    return jsonify(result)

@knowledge_bp.route('/admin/relations', methods=['GET'])
def admin_knowledge_relations():
    result = KnowledgeController.admin_get_relations()
    return jsonify(result)

@knowledge_bp.route('/admin/create-relation', methods=['POST'])
def admin_knowledge_create_relation():
    result = KnowledgeController.admin_create_relation()
    return jsonify(result)

@knowledge_bp.route('/admin/delete-relation', methods=['GET'])
def admin_knowledge_delete_relation():
    result = KnowledgeController.admin_delete_relation()
    return jsonify(result)

# 前台接口（公开访问）
@knowledge_bp.route('/front/list', methods=['GET'])
def front_knowledge_list():
    result = KnowledgeController.front_list()
    return jsonify(result)

@knowledge_bp.route('/front/detail', methods=['GET'])
def front_knowledge_detail():
    result = KnowledgeController.front_detail()
    return jsonify(result)

