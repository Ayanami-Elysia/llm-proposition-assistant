"""
药品管理 控制层
"""
from flask import request, session
from service.drug_service import DrugService
from utils.response import success, error


class DrugController:
    """药品控制器类"""

    @staticmethod
    def admin_list():
        """后台获取药品列表（分页 + 条件）"""
        try:
            page_num = int(request.args.get('pageNum', 1))
            page_size = int(request.args.get('pageSize', 10))
            status = request.args.get('status', '').strip() or None
            keyword = request.args.get('keyword', '').strip() or None
            category = request.args.get('category', '').strip() or None

            if page_num < 1:
                page_num = 1
            if page_size < 1 or page_size > 100:
                page_size = 10

            return DrugService.get_drug_list(page_num, page_size, status, keyword, category)
        except Exception as e:
            print(f"获取药品列表失败: {str(e)}")
            return error(f"获取药品列表失败: {str(e)}")

    @staticmethod
    def admin_detail():
        """后台获取药品详情"""
        try:
            drug_id = request.args.get('id')
            if not drug_id:
                return error("缺少药品ID参数")
            try:
                drug_id = int(drug_id)
            except ValueError:
                return error("药品ID格式错误")

            return DrugService.get_drug_by_id(drug_id)
        except Exception as e:
            print(f"获取药品详情失败: {str(e)}")
            return error(f"获取药品详情失败: {str(e)}")

    @staticmethod
    def admin_create():
        """后台创建药品"""
        try:
            if 'user_id' not in session:
                return error("请先登录")

            data = request.get_json() or {}
            drug_name = (data.get('drugName') or '').strip()

            if not drug_name:
                return error("药品名称不能为空")

            return DrugService.create_drug(
                drug_name=drug_name,
                generic_name=(data.get('genericName') or '').strip() or None,
                code=(data.get('code') or '').strip() or None,
                barcode=(data.get('barcode') or '').strip() or None,
                category=(data.get('category') or '').strip() or None,
                dosage_form=(data.get('dosageForm') or '').strip() or None,
                specification=(data.get('specification') or '').strip() or None,
                unit=(data.get('unit') or '').strip() or None,
                manufacturer=(data.get('manufacturer') or '').strip() or None,
                approval_number=(data.get('approvalNumber') or '').strip() or None,
                price=(data.get('price') or '').strip() or None,
                stock=(data.get('stock') or '').strip() or None,
                status=(data.get('status') or 'enabled').strip() or 'enabled',
                remark=(data.get('remark') or '').strip() or None,
                image_url=(data.get('imageUrl') or '').strip() or None
            )
        except Exception as e:
            print(f"创建药品失败: {str(e)}")
            return error(f"创建药品失败: {str(e)}")

    @staticmethod
    def admin_update():
        """后台更新药品"""
        try:
            if 'user_id' not in session:
                return error("请先登录")

            data = request.get_json() or {}
            drug_id = data.get('id')
            if not drug_id:
                return error("缺少药品ID")
            try:
                drug_id = int(drug_id)
            except ValueError:
                return error("药品ID格式错误")

            drug_name = (data.get('drugName') or '').strip()
            if not drug_name:
                return error("药品名称不能为空")

            return DrugService.update_drug(
                drug_id=drug_id,
                drug_name=drug_name,
                generic_name=(data.get('genericName') or '').strip() or None,
                code=(data.get('code') or '').strip() or None,
                barcode=(data.get('barcode') or '').strip() or None,
                category=(data.get('category') or '').strip() or None,
                dosage_form=(data.get('dosageForm') or '').strip() or None,
                specification=(data.get('specification') or '').strip() or None,
                unit=(data.get('unit') or '').strip() or None,
                manufacturer=(data.get('manufacturer') or '').strip() or None,
                approval_number=(data.get('approvalNumber') or '').strip() or None,
                price=(data.get('price') or '').strip() or None,
                stock=(data.get('stock') or '').strip() or None,
                status=(data.get('status') or 'enabled').strip() or 'enabled',
                remark=(data.get('remark') or '').strip() or None,
                image_url=(data.get('imageUrl') or '').strip() or None
            )
        except Exception as e:
            print(f"更新药品失败: {str(e)}")
            return error(f"更新药品失败: {str(e)}")

    @staticmethod
    def admin_delete():
        """后台删除药品"""
        try:
            if 'user_id' not in session:
                return error("请先登录")

            drug_id = request.args.get('id')
            if not drug_id:
                return error("缺少药品ID参数")
            try:
                drug_id = int(drug_id)
            except ValueError:
                return error("药品ID格式错误")

            return DrugService.delete_drug(drug_id)
        except Exception as e:
            print(f"删除药品失败: {str(e)}")
            return error(f"删除药品失败: {str(e)}")

    @staticmethod
    def admin_toggle_status():
        """后台切换药品状态"""
        try:
            if 'user_id' not in session:
                return error("请先登录")

            drug_id = request.args.get('id')
            if not drug_id:
                return error("缺少药品ID参数")
            try:
                drug_id = int(drug_id)
            except ValueError:
                return error("药品ID格式错误")

            return DrugService.toggle_drug_status(drug_id)
        except Exception as e:
            print(f"切换药品状态失败: {str(e)}")
            return error(f"切换药品状态失败: {str(e)}")


