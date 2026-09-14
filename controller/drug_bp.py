"""
药品管理 蓝图
"""
from flask import Blueprint, jsonify
from controller.drug_controller import DrugController

# 创建蓝图
drug_bp = Blueprint('drug', __name__)

# 后台管理接口
@drug_bp.route('/admin/list', methods=['GET'])
def admin_drug_list():
    result = DrugController.admin_list()
    return jsonify(result)

@drug_bp.route('/admin/detail', methods=['GET'])
def admin_drug_detail():
    result = DrugController.admin_detail()
    return jsonify(result)

@drug_bp.route('/admin/create', methods=['POST'])
def admin_drug_create():
    result = DrugController.admin_create()
    return jsonify(result)

@drug_bp.route('/admin/update', methods=['POST'])
def admin_drug_update():
    result = DrugController.admin_update()
    return jsonify(result)

@drug_bp.route('/admin/delete', methods=['GET'])
def admin_drug_delete():
    result = DrugController.admin_delete()
    return jsonify(result)

@drug_bp.route('/admin/toggle-status', methods=['GET'])
def admin_drug_toggle_status():
    result = DrugController.admin_toggle_status()
    return jsonify(result)


