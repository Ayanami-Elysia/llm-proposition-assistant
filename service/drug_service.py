"""
药品管理 服务层
"""
import pymysql
from datetime import datetime
from typing import Optional

from utils.db_utils import get_db_connection
from utils.response import success, error, page_response


class DrugService:
    """药品服务类"""

    @staticmethod
    def get_drug_list(
        page_num: int = 1,
        page_size: int = 10,
        status: Optional[str] = None,
        keyword: Optional[str] = None,
        category: Optional[str] = None
    ):
        """
        获取药品列表（分页 + 条件）
        Args:
            page_num: 页码
            page_size: 每页数量
            status: 状态筛选（enabled/disabled）
            keyword: 关键字（匹配 名称/通用名/编码/条形码/厂家）
            category: 分类
        """
        try:
            with get_db_connection() as conn:
                with conn.cursor() as cursor:
                    where_conditions = []
                    params = []

                    if status:
                        where_conditions.append("status = %s")
                        params.append(status)

                    if category:
                        where_conditions.append("category = %s")
                        params.append(category)

                    if keyword:
                        where_conditions.append(
                            "(drugName LIKE %s OR genericName LIKE %s OR code LIKE %s OR barcode LIKE %s OR manufacturer LIKE %s)"
                        )
                        like = f"%{keyword}%"
                        params.extend([like, like, like, like, like])

                    where_clause = f"WHERE {' AND '.join(where_conditions)}" if where_conditions else ""

                    # total
                    count_sql = f"SELECT COUNT(*) AS total FROM py_drug {where_clause}"
                    print(f"执行SQL: {count_sql}, 参数: {params}")
                    cursor.execute(count_sql, params)
                    total = cursor.fetchone()["total"]

                    # rows
                    offset = (page_num - 1) * page_size
                    data_sql = f"""
                        SELECT id, drugName, genericName, code, barcode, category, dosageForm,
                               specification, unit, manufacturer, approvalNumber, price, stock,
                               status, remark, imageUrl, createTime, updateTime
                        FROM py_drug
                        {where_clause}
                        ORDER BY createTime DESC
                        LIMIT %s OFFSET %s
                    """
                    query_params = list(params) + [page_size, offset]
                    print(f"执行SQL: {data_sql}, 参数: {query_params}")
                    cursor.execute(data_sql, query_params)
                    rows = cursor.fetchall()

                    return page_response(rows, total, page_num, page_size)
        except Exception as e:
            print(f"获取药品列表失败: {str(e)}")
            return error(f"获取药品列表失败: {str(e)}")

    @staticmethod
    def get_drug_by_id(drug_id: int):
        """根据ID获取药品详情"""
        try:
            with get_db_connection() as conn:
                with conn.cursor() as cursor:
                    sql = """
                        SELECT id, drugName, genericName, code, barcode, category, dosageForm,
                               specification, unit, manufacturer, approvalNumber, price, stock,
                               status, remark, imageUrl, createTime, updateTime
                        FROM py_drug
                        WHERE id = %s
                    """
                    print(f"执行SQL: {sql}, 参数: [{drug_id}]")
                    cursor.execute(sql, [drug_id])
                    row = cursor.fetchone()
                    if not row:
                        return error("药品不存在")
                    return success(row)
        except Exception as e:
            print(f"获取药品详情失败: {str(e)}")
            return error(f"获取药品详情失败: {str(e)}")

    @staticmethod
    def create_drug(
        drug_name: str,
        generic_name: Optional[str],
        code: Optional[str],
        barcode: Optional[str],
        category: Optional[str],
        dosage_form: Optional[str],
        specification: Optional[str],
        unit: Optional[str],
        manufacturer: Optional[str],
        approval_number: Optional[str],
        price: Optional[str],
        stock: Optional[str],
        status: str = "enabled",
        remark: Optional[str] = None,
        image_url: Optional[str] = None
    ):
        """创建药品"""
        try:
            with get_db_connection() as conn:
                with conn.cursor() as cursor:
                    sql = """
                        INSERT INTO py_drug
                        (drugName, genericName, code, barcode, category, dosageForm, specification,
                         unit, manufacturer, approvalNumber, price, stock, status, remark, imageUrl,
                         createTime, updateTime)
                        VALUES
                        (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW(), NOW())
                    """
                    params = [
                        drug_name, generic_name, code, barcode, category, dosage_form, specification,
                        unit, manufacturer, approval_number, price, stock, status, remark, image_url
                    ]
                    print(f"执行SQL: {sql}, 参数: {params}")
                    cursor.execute(sql, params)
                    conn.commit()
                    new_id = cursor.lastrowid
                    return success({"id": new_id}, "药品创建成功")
        except pymysql.err.IntegrityError as ie:
            print(f"创建药品失败(唯一约束): {str(ie)}")
            return error("创建失败：编码或条形码已存在")
        except Exception as e:
            print(f"创建药品失败: {str(e)}")
            return error(f"创建药品失败: {str(e)}")

    @staticmethod
    def update_drug(
        drug_id: int,
        drug_name: str,
        generic_name: Optional[str],
        code: Optional[str],
        barcode: Optional[str],
        category: Optional[str],
        dosage_form: Optional[str],
        specification: Optional[str],
        unit: Optional[str],
        manufacturer: Optional[str],
        approval_number: Optional[str],
        price: Optional[str],
        stock: Optional[str],
        status: str,
        remark: Optional[str],
        image_url: Optional[str]
    ):
        """更新药品"""
        try:
            with get_db_connection() as conn:
                with conn.cursor() as cursor:
                    # 存在性校验
                    check_sql = "SELECT id FROM py_drug WHERE id = %s"
                    print(f"执行SQL: {check_sql}, 参数: [{drug_id}]")
                    cursor.execute(check_sql, [drug_id])
                    if not cursor.fetchone():
                        return error("药品不存在")

                    sql = """
                        UPDATE py_drug
                        SET drugName=%s, genericName=%s, code=%s, barcode=%s, category=%s,
                            dosageForm=%s, specification=%s, unit=%s, manufacturer=%s,
                            approvalNumber=%s, price=%s, stock=%s, status=%s, remark=%s,
                            imageUrl=%s, updateTime=NOW()
                        WHERE id=%s
                    """
                    params = [
                        drug_name, generic_name, code, barcode, category, dosage_form, specification,
                        unit, manufacturer, approval_number, price, stock, status, remark,
                        image_url, drug_id
                    ]
                    print(f"执行SQL: {sql}, 参数: {params}")
                    cursor.execute(sql, params)
                    conn.commit()
                    return success(None, "药品更新成功")
        except pymysql.err.IntegrityError as ie:
            print(f"更新药品失败(唯一约束): {str(ie)}")
            return error("更新失败：编码或条形码与其他记录重复")
        except Exception as e:
            print(f"更新药品失败: {str(e)}")
            return error(f"更新药品失败: {str(e)}")

    @staticmethod
    def delete_drug(drug_id: int):
        """删除药品"""
        try:
            with get_db_connection() as conn:
                with conn.cursor() as cursor:
                    check_sql = "SELECT id FROM py_drug WHERE id = %s"
                    print(f"执行SQL: {check_sql}, 参数: [{drug_id}]")
                    cursor.execute(check_sql, [drug_id])
                    if not cursor.fetchone():
                        return error("药品不存在")

                    sql = "DELETE FROM py_drug WHERE id = %s"
                    print(f"执行SQL: {sql}, 参数: [{drug_id}]")
                    cursor.execute(sql, [drug_id])
                    conn.commit()
                    return success(None, "药品删除成功")
        except Exception as e:
            print(f"删除药品失败: {str(e)}")
            return error(f"删除药品失败: {str(e)}")

    @staticmethod
    def toggle_drug_status(drug_id: int):
        """切换药品状态 enabled/disabled"""
        try:
            with get_db_connection() as conn:
                with conn.cursor() as cursor:
                    get_sql = "SELECT status FROM py_drug WHERE id = %s"
                    print(f"执行SQL: {get_sql}, 参数: [{drug_id}]")
                    cursor.execute(get_sql, [drug_id])
                    row = cursor.fetchone()
                    if not row:
                        return error("药品不存在")

                    current = row["status"] or "enabled"
                    new_status = "disabled" if current == "enabled" else "enabled"

                    upd_sql = "UPDATE py_drug SET status=%s, updateTime=NOW() WHERE id=%s"
                    print(f"执行SQL: {upd_sql}, 参数: [{new_status}, {drug_id}]")
                    cursor.execute(upd_sql, [new_status, drug_id])
                    conn.commit()
                    return success(None, f"状态已更新为 {new_status}")
        except Exception as e:
            print(f"切换药品状态失败: {str(e)}")
            return error(f"切换药品状态失败: {str(e)}")


