"""
知识库管理 服务层
"""
import pymysql
import json
from datetime import datetime
from typing import Optional, List

from utils.db_utils import get_db_connection
from utils.response import success, error, page_response


class KnowledgeService:
    """知识库服务类"""

    @staticmethod
    def get_knowledge_list(
        page_num: int = 1,
        page_size: int = 10,
        status: Optional[str] = None,
        keyword: Optional[str] = None,
        subject: Optional[str] = None,
        grade: Optional[str] = None
    ):
        """
        获取知识库列表（分页 + 条件）
        Args:
            page_num: 页码
            page_size: 每页数量
            status: 状态筛选（enabled/disabled）
            keyword: 关键字（匹配 标题/摘要/知识点）
            subject: 学科筛选
            grade: 年级筛选
        """
        try:
            with get_db_connection() as conn:
                with conn.cursor() as cursor:
                    where_conditions = []
                    params = []

                    if status:
                        where_conditions.append("status = %s")
                        params.append(status)

                    if subject:
                        where_conditions.append("subject = %s")
                        params.append(subject)

                    if grade:
                        where_conditions.append("grade = %s")
                        params.append(grade)

                    if keyword:
                        where_conditions.append(
                            "(title LIKE %s OR summary LIKE %s OR knowledgePoint LIKE %s)"
                        )
                        like = f"%{keyword}%"
                        params.extend([like, like, like])

                    where_clause = f"WHERE {' AND '.join(where_conditions)}" if where_conditions else ""

                    # total
                    count_sql = f"SELECT COUNT(*) AS total FROM py_knowledge_base {where_clause}"
                    print(f"执行SQL: {count_sql}, 参数: {params}")
                    cursor.execute(count_sql, params)
                    total = cursor.fetchone()["total"]

                    # rows
                    offset = (page_num - 1) * page_size
                    data_sql = f"""
                        SELECT id, title, summary, knowledgePoint, subject, grade, attachmentUrl,
                               content, author, authorId, status, viewCount, createTime, updateTime
                        FROM py_knowledge_base
                        {where_clause}
                        ORDER BY createTime DESC
                        LIMIT %s OFFSET %s
                    """
                    query_params = list(params) + [page_size, offset]
                    print(f"执行SQL: {data_sql}, 参数: {query_params}")
                    cursor.execute(data_sql, query_params)
                    rows = cursor.fetchall()

                    # 处理JSON字段
                    for row in rows:
                        if row.get('knowledgePoint'):
                            try:
                                if isinstance(row['knowledgePoint'], str):
                                    row['knowledgePoint'] = json.loads(row['knowledgePoint'])
                            except:
                                # 如果不是JSON，尝试按逗号分割
                                if ',' in str(row['knowledgePoint']):
                                    row['knowledgePoint'] = [k.strip() for k in str(row['knowledgePoint']).split(',')]
                                else:
                                    row['knowledgePoint'] = [str(row['knowledgePoint'])]
                        
                        if row.get('attachmentUrl'):
                            try:
                                if isinstance(row['attachmentUrl'], str):
                                    row['attachmentUrl'] = json.loads(row['attachmentUrl'])
                            except:
                                row['attachmentUrl'] = []

                    return page_response(rows, total, page_num, page_size)
        except Exception as e:
            print(f"获取知识库列表失败: {str(e)}")
            return error(f"获取知识库列表失败: {str(e)}")

    @staticmethod
    def get_knowledge_by_id(knowledge_id: int):
        """根据ID获取知识库详情"""
        try:
            with get_db_connection() as conn:
                with conn.cursor() as cursor:
                    sql = """
                        SELECT id, title, summary, knowledgePoint, subject, grade, attachmentUrl,
                               content, author, authorId, status, viewCount, createTime, updateTime
                        FROM py_knowledge_base
                        WHERE id = %s
                    """
                    print(f"执行SQL: {sql}, 参数: [{knowledge_id}]")
                    cursor.execute(sql, [knowledge_id])
                    row = cursor.fetchone()
                    if not row:
                        return error("知识库不存在")
                    
                    # 处理JSON字段
                    if row.get('knowledgePoint'):
                        try:
                            if isinstance(row['knowledgePoint'], str):
                                row['knowledgePoint'] = json.loads(row['knowledgePoint'])
                        except:
                            if ',' in str(row['knowledgePoint']):
                                row['knowledgePoint'] = [k.strip() for k in str(row['knowledgePoint']).split(',')]
                            else:
                                row['knowledgePoint'] = [str(row['knowledgePoint'])]
                    
                    if row.get('attachmentUrl'):
                        try:
                            if isinstance(row['attachmentUrl'], str):
                                row['attachmentUrl'] = json.loads(row['attachmentUrl'])
                        except:
                            row['attachmentUrl'] = []
                    
                    return success(row)
        except Exception as e:
            print(f"获取知识库详情失败: {str(e)}")
            return error(f"获取知识库详情失败: {str(e)}")

    @staticmethod
    def get_front_knowledge_list(
        page_num: int = 1,
        page_size: int = 10,
        keyword: Optional[str] = None,
        subject: Optional[str] = None,
        grade: Optional[str] = None
    ):
        """
        获取前台知识库列表（只显示已启用的，支持分页和搜索）
        Args:
            page_num: 页码
            page_size: 每页数量
            keyword: 关键字（匹配标题/摘要/知识点）
            subject: 学科筛选
            grade: 年级筛选
        """
        try:
            with get_db_connection() as conn:
                with conn.cursor() as cursor:
                    where_conditions = ["status = 'enabled'"]  # 只显示已启用的
                    params = []

                    if subject:
                        where_conditions.append("subject = %s")
                        params.append(subject)

                    if grade:
                        where_conditions.append("grade = %s")
                        params.append(grade)

                    if keyword:
                        where_conditions.append(
                            "(title LIKE %s OR summary LIKE %s OR knowledgePoint LIKE %s)"
                        )
                        like = f"%{keyword}%"
                        params.extend([like, like, like])

                    where_clause = f"WHERE {' AND '.join(where_conditions)}"

                    # total
                    count_sql = f"SELECT COUNT(*) AS total FROM py_knowledge_base {where_clause}"
                    print(f"执行SQL: {count_sql}, 参数: {params}")
                    cursor.execute(count_sql, params)
                    total = cursor.fetchone()["total"]

                    # rows
                    offset = (page_num - 1) * page_size
                    data_sql = f"""
                        SELECT id, title, summary, knowledgePoint, subject, grade, attachmentUrl,
                               content, author, viewCount, createTime
                        FROM py_knowledge_base
                        {where_clause}
                        ORDER BY createTime DESC
                        LIMIT %s OFFSET %s
                    """
                    query_params = list(params) + [page_size, offset]
                    print(f"执行SQL: {data_sql}, 参数: {query_params}")
                    cursor.execute(data_sql, query_params)
                    rows = cursor.fetchall()

                    # 处理JSON字段和格式化时间
                    for row in rows:
                        if row.get('knowledgePoint'):
                            try:
                                if isinstance(row['knowledgePoint'], str):
                                    row['knowledgePoint'] = json.loads(row['knowledgePoint'])
                            except:
                                if ',' in str(row['knowledgePoint']):
                                    row['knowledgePoint'] = [k.strip() for k in str(row['knowledgePoint']).split(',')]
                                else:
                                    row['knowledgePoint'] = [str(row['knowledgePoint'])]
                        else:
                            row['knowledgePoint'] = []
                        
                        if row.get('attachmentUrl'):
                            try:
                                if isinstance(row['attachmentUrl'], str):
                                    row['attachmentUrl'] = json.loads(row['attachmentUrl'])
                            except:
                                row['attachmentUrl'] = []
                        else:
                            row['attachmentUrl'] = []
                        
                        if row.get('createTime'):
                            row['createTime'] = row['createTime'].strftime('%Y-%m-%d %H:%M:%S')

                    return page_response(rows, total, page_num, page_size)
        except Exception as e:
            print(f"获取前台知识库列表失败: {str(e)}")
            return error(f"获取前台知识库列表失败: {str(e)}")

    @staticmethod
    def get_front_knowledge_detail(knowledge_id: int):
        """获取前台知识库详情（仅返回已启用的）"""
        try:
            with get_db_connection() as conn:
                with conn.cursor() as cursor:
                    sql = """
                        SELECT id, title, summary, knowledgePoint, subject, grade, attachmentUrl,
                               content, author, viewCount, createTime
                        FROM py_knowledge_base
                        WHERE id = %s AND status = 'enabled'
                    """
                    print(f"执行SQL: {sql}, 参数: [{knowledge_id}]")
                    cursor.execute(sql, [knowledge_id])
                    row = cursor.fetchone()
                    if not row:
                        return error("知识库不存在或已禁用")
                    
                    # 处理JSON字段
                    if row.get('knowledgePoint'):
                        try:
                            if isinstance(row['knowledgePoint'], str):
                                row['knowledgePoint'] = json.loads(row['knowledgePoint'])
                        except:
                            if ',' in str(row['knowledgePoint']):
                                row['knowledgePoint'] = [k.strip() for k in str(row['knowledgePoint']).split(',')]
                            else:
                                row['knowledgePoint'] = [str(row['knowledgePoint'])]
                    else:
                        row['knowledgePoint'] = []
                    
                    if row.get('attachmentUrl'):
                        try:
                            if isinstance(row['attachmentUrl'], str):
                                row['attachmentUrl'] = json.loads(row['attachmentUrl'])
                        except:
                            row['attachmentUrl'] = []
                    else:
                        row['attachmentUrl'] = []
                    
                    # 格式化时间
                    if row.get('createTime'):
                        row['createTime'] = row['createTime'].strftime('%Y-%m-%d %H:%M:%S')
                    
                    # 增加浏览次数
                    update_view_sql = "UPDATE py_knowledge_base SET viewCount = viewCount + 1 WHERE id = %s"
                    cursor.execute(update_view_sql, [knowledge_id])
                    conn.commit()
                    
                    return success(row)
        except Exception as e:
            print(f"获取前台知识库详情失败: {str(e)}")
            return error(f"获取前台知识库详情失败: {str(e)}")

    @staticmethod
    def create_knowledge(
        title: str,
        summary: Optional[str],
        knowledge_point: Optional[List[str]],
        subject: str,
        grade: str,
        attachment_url: Optional[List[str]],
        content: Optional[str],
        author: str,
        author_id: int,
        status: str = "enabled"
    ):
        """创建知识库"""
        try:
            with get_db_connection() as conn:
                with conn.cursor() as cursor:
                    # 处理知识点和附件URL为JSON字符串
                    knowledge_point_str = json.dumps(knowledge_point, ensure_ascii=False) if knowledge_point else None
                    attachment_url_str = json.dumps(attachment_url, ensure_ascii=False) if attachment_url else None

                    sql = """
                        INSERT INTO py_knowledge_base
                        (title, summary, knowledgePoint, subject, grade, attachmentUrl, content,
                         author, authorId, status, createTime, updateTime)
                        VALUES
                        (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW(), NOW())
                    """
                    params = [
                        title, summary, knowledge_point_str, subject, grade, attachment_url_str,
                        content, author, author_id, status
                    ]
                    print(f"执行SQL: {sql}, 参数: {params}")
                    cursor.execute(sql, params)
                    conn.commit()
                    new_id = cursor.lastrowid
                    return success({"id": new_id}, "知识库创建成功")
        except Exception as e:
            print(f"创建知识库失败: {str(e)}")
            return error(f"创建知识库失败: {str(e)}")

    @staticmethod
    def update_knowledge(
        knowledge_id: int,
        title: str,
        summary: Optional[str],
        knowledge_point: Optional[List[str]],
        subject: str,
        grade: str,
        attachment_url: Optional[List[str]],
        content: Optional[str],
        status: str
    ):
        """更新知识库"""
        try:
            with get_db_connection() as conn:
                with conn.cursor() as cursor:
                    # 存在性校验
                    check_sql = "SELECT id FROM py_knowledge_base WHERE id = %s"
                    print(f"执行SQL: {check_sql}, 参数: [{knowledge_id}]")
                    cursor.execute(check_sql, [knowledge_id])
                    if not cursor.fetchone():
                        return error("知识库不存在")

                    # 处理知识点和附件URL为JSON字符串
                    knowledge_point_str = json.dumps(knowledge_point, ensure_ascii=False) if knowledge_point else None
                    attachment_url_str = json.dumps(attachment_url, ensure_ascii=False) if attachment_url else None

                    sql = """
                        UPDATE py_knowledge_base
                        SET title=%s, summary=%s, knowledgePoint=%s, subject=%s, grade=%s,
                            attachmentUrl=%s, content=%s, status=%s, updateTime=NOW()
                        WHERE id=%s
                    """
                    params = [
                        title, summary, knowledge_point_str, subject, grade, attachment_url_str,
                        content, status, knowledge_id
                    ]
                    print(f"执行SQL: {sql}, 参数: {params}")
                    cursor.execute(sql, params)
                    conn.commit()
                    return success(None, "知识库更新成功")
        except Exception as e:
            print(f"更新知识库失败: {str(e)}")
            return error(f"更新知识库失败: {str(e)}")

    @staticmethod
    def delete_knowledge(knowledge_id: int):
        """删除知识库"""
        try:
            with get_db_connection() as conn:
                with conn.cursor() as cursor:
                    check_sql = "SELECT id FROM py_knowledge_base WHERE id = %s"
                    print(f"执行SQL: {check_sql}, 参数: [{knowledge_id}]")
                    cursor.execute(check_sql, [knowledge_id])
                    if not cursor.fetchone():
                        return error("知识库不存在")

                    # 删除关联关系
                    delete_relation_sql = """
                        DELETE FROM py_knowledge_relation 
                        WHERE sourceId = %s OR targetId = %s
                    """
                    print(f"执行SQL: {delete_relation_sql}, 参数: [{knowledge_id}, {knowledge_id}]")
                    cursor.execute(delete_relation_sql, [knowledge_id, knowledge_id])

                    # 删除知识库
                    sql = "DELETE FROM py_knowledge_base WHERE id = %s"
                    print(f"执行SQL: {sql}, 参数: [{knowledge_id}]")
                    cursor.execute(sql, [knowledge_id])
                    conn.commit()
                    return success(None, "知识库删除成功")
        except Exception as e:
            print(f"删除知识库失败: {str(e)}")
            return error(f"删除知识库失败: {str(e)}")

    @staticmethod
    def toggle_knowledge_status(knowledge_id: int):
        """切换知识库状态 enabled/disabled"""
        try:
            with get_db_connection() as conn:
                with conn.cursor() as cursor:
                    get_sql = "SELECT status FROM py_knowledge_base WHERE id = %s"
                    print(f"执行SQL: {get_sql}, 参数: [{knowledge_id}]")
                    cursor.execute(get_sql, [knowledge_id])
                    row = cursor.fetchone()
                    if not row:
                        return error("知识库不存在")

                    current = row["status"] or "enabled"
                    new_status = "disabled" if current == "enabled" else "enabled"

                    upd_sql = "UPDATE py_knowledge_base SET status=%s, updateTime=NOW() WHERE id=%s"
                    print(f"执行SQL: {upd_sql}, 参数: [{new_status}, {knowledge_id}]")
                    cursor.execute(upd_sql, [new_status, knowledge_id])
                    conn.commit()
                    return success(None, f"状态已更新为 {new_status}")
        except Exception as e:
            print(f"切换知识库状态失败: {str(e)}")
            return error(f"切换知识库状态失败: {str(e)}")

    @staticmethod
    def get_knowledge_relations(knowledge_id: int):
        """获取知识库的关联关系（用于知识图谱展示）"""
        try:
            with get_db_connection() as conn:
                with conn.cursor() as cursor:
                    sql = """
                        SELECT kr.id, kr.sourceId, kr.targetId, kr.relationType, kr.weight,
                               kb1.title as sourceTitle, kb2.title as targetTitle
                        FROM py_knowledge_relation kr
                        LEFT JOIN py_knowledge_base kb1 ON kr.sourceId = kb1.id
                        LEFT JOIN py_knowledge_base kb2 ON kr.targetId = kb2.id
                        WHERE kr.sourceId = %s OR kr.targetId = %s
                    """
                    print(f"执行SQL: {sql}, 参数: [{knowledge_id}, {knowledge_id}]")
                    cursor.execute(sql, [knowledge_id, knowledge_id])
                    rows = cursor.fetchall()
                    return success(rows)
        except Exception as e:
            print(f"获取知识关联关系失败: {str(e)}")
            return error(f"获取知识关联关系失败: {str(e)}")

    @staticmethod
    def create_knowledge_relation(
        source_id: int,
        target_id: int,
        relation_type: str = "related",
        weight: float = 1.0
    ):
        """创建知识关联关系"""
        try:
            if source_id == target_id:
                return error("不能关联自己")

            with get_db_connection() as conn:
                with conn.cursor() as cursor:
                    # 检查两个知识是否存在
                    check_sql = "SELECT id FROM py_knowledge_base WHERE id IN (%s, %s)"
                    print(f"执行SQL: {check_sql}, 参数: [{source_id}, {target_id}]")
                    cursor.execute(check_sql, [source_id, target_id])
                    if cursor.rowcount < 2:
                        return error("关联的知识不存在")

                    # 检查是否已存在关联
                    exist_sql = """
                        SELECT id FROM py_knowledge_relation 
                        WHERE sourceId = %s AND targetId = %s AND relationType = %s
                    """
                    print(f"执行SQL: {exist_sql}, 参数: [{source_id}, {target_id}, {relation_type}]")
                    cursor.execute(exist_sql, [source_id, target_id, relation_type])
                    if cursor.fetchone():
                        return error("关联关系已存在")

                    sql = """
                        INSERT INTO py_knowledge_relation
                        (sourceId, targetId, relationType, weight, createTime)
                        VALUES (%s, %s, %s, %s, NOW())
                    """
                    params = [source_id, target_id, relation_type, weight]
                    print(f"执行SQL: {sql}, 参数: {params}")
                    cursor.execute(sql, params)
                    conn.commit()
                    return success({"id": cursor.lastrowid}, "关联关系创建成功")
        except pymysql.err.IntegrityError:
            return error("关联关系已存在")
        except Exception as e:
            print(f"创建知识关联关系失败: {str(e)}")
            return error(f"创建知识关联关系失败: {str(e)}")

    @staticmethod
    def delete_knowledge_relation(relation_id: int):
        """删除知识关联关系"""
        try:
            with get_db_connection() as conn:
                with conn.cursor() as cursor:
                    sql = "DELETE FROM py_knowledge_relation WHERE id = %s"
                    print(f"执行SQL: {sql}, 参数: [{relation_id}]")
                    cursor.execute(sql, [relation_id])
                    conn.commit()
                    return success(None, "关联关系删除成功")
        except Exception as e:
            print(f"删除知识关联关系失败: {str(e)}")
            return error(f"删除知识关联关系失败: {str(e)}")

