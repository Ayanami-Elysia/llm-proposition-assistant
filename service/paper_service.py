"""
试卷管理 服务层
"""
import pymysql
import random
from typing import Any, Optional, List, Dict

from utils.db_utils import get_db_connection
from utils.response import success, error, page_response


class PaperService:
    """试卷服务类"""

    @staticmethod
    def _append_paper_access_scope(
        where_conditions: List[str],
        params: List[Any],
        current_user: Optional[Dict[str, Any]],
        paper_alias: str = "p"
    ) -> None:
        """追加教师端试卷访问范围"""
        if not current_user or current_user.get("role") != "doctor":
            return

        class_id = current_user.get("class_id")
        if not class_id:
            user_id = current_user.get("id")
            where_conditions.append(f"{paper_alias}.authorId = %s")
            params.append(user_id)
            return

        where_conditions.append(f"""
            EXISTS (
                SELECT 1
                FROM py_user pu
                WHERE pu.id = {paper_alias}.authorId
                  AND pu.role = 'doctor'
                  AND pu.class_id = %s
            )
        """)
        params.append(class_id)

    @staticmethod
    def _has_paper_access(
        cursor: Any,
        paper_id: int,
        current_user: Optional[Dict[str, Any]]
    ) -> bool:
        """检查是否有试卷访问权限"""
        where_conditions: List[str] = ["p.id = %s"]
        params: List[Any] = [paper_id]
        PaperService._append_paper_access_scope(where_conditions, params, current_user)
        sql = f"""
            SELECT p.id
            FROM py_paper p
            WHERE {' AND '.join(where_conditions)}
        """
        cursor.execute(sql, params)
        return cursor.fetchone() is not None

    @staticmethod
    def _append_front_paper_scope(
        where_conditions: List[str],
        params: List[Any],
        current_user: Optional[Dict[str, Any]],
        paper_alias: str = "p"
    ) -> None:
        """追加前台试卷访问范围"""
        if not current_user or current_user.get("role") != "user":
            return

        class_id = current_user.get("class_id")
        if not class_id:
            return

        where_conditions.append(f"""
            EXISTS (
                SELECT 1
                FROM py_user pu
                WHERE pu.id = {paper_alias}.authorId
                  AND (pu.class_id = %s OR pu.class_id IS NULL)
            )
        """)
        params.append(class_id)

    @staticmethod
    def get_paper_list(
        page_num: int = 1,
        page_size: int = 10,
        status: Optional[str] = None,
        keyword: Optional[str] = None,
        current_user: Optional[Dict[str, Any]] = None
    ):
        """
        获取试卷列表（分页 + 条件）
        Args:
            page_num: 页码
            page_size: 每页数量
            status: 状态筛选（enabled/disabled）
            keyword: 关键字（匹配试卷名称）
        """
        try:
            with get_db_connection() as conn:
                with conn.cursor() as cursor:
                    where_conditions = []
                    params = []

                    if status:
                        where_conditions.append("p.status = %s")
                        params.append(status)

                    if keyword:
                        where_conditions.append("p.paperName LIKE %s")
                        params.append(f"%{keyword}%")

                    PaperService._append_paper_access_scope(where_conditions, params, current_user)
                    where_clause = f"WHERE {' AND '.join(where_conditions)}" if where_conditions else ""

                    # total
                    count_sql = f"""
                        SELECT COUNT(*) AS total
                        FROM py_paper p
                        LEFT JOIN py_user u ON p.authorId = u.id
                        LEFT JOIN py_class c ON u.class_id = c.id
                        {where_clause}
                    """
                    print(f"执行SQL: {count_sql}, 参数: {params}")
                    cursor.execute(count_sql, params)
                    total = cursor.fetchone()["total"]

                    # rows
                    offset = (page_num - 1) * page_size
                    data_sql = f"""
                        SELECT p.id, p.paperName, p.duration, p.startTime, p.endTime, p.description,
                               p.imageUrl, p.totalScore, p.questionCount, p.status, p.author,
                               p.authorId, c.class_name AS className, p.createTime, p.updateTime
                        FROM py_paper p
                        LEFT JOIN py_user u ON p.authorId = u.id
                        LEFT JOIN py_class c ON u.class_id = c.id
                        {where_clause}
                        ORDER BY p.createTime DESC
                        LIMIT %s OFFSET %s
                    """
                    query_params = list(params) + [page_size, offset]
                    print(f"执行SQL: {data_sql}, 参数: {query_params}")
                    cursor.execute(data_sql, query_params)
                    rows = cursor.fetchall()

                    return page_response(rows, total, page_num, page_size)
        except Exception as e:
            print(f"获取试卷列表失败: {str(e)}")
            return error(f"获取试卷列表失败: {str(e)}")

    @staticmethod
    def get_paper_by_id(
        paper_id: int,
        current_user: Optional[Dict[str, Any]] = None
    ):
        """根据ID获取试卷详情"""
        try:
            with get_db_connection() as conn:
                with conn.cursor() as cursor:
                    where_conditions: List[str] = ["p.id = %s"]
                    params: List[Any] = [paper_id]
                    PaperService._append_paper_access_scope(where_conditions, params, current_user)
                    sql = """
                        SELECT id, paperName, duration, startTime, endTime, description, imageUrl,
                               totalScore, questionCount, status, author, authorId, createTime, updateTime
                        FROM py_paper p
                        WHERE {where_clause}
                    """.format(where_clause=" AND ".join(where_conditions))
                    print(f"执行SQL: {sql}, 参数: {params}")
                    cursor.execute(sql, params)
                    row = cursor.fetchone()
                    if not row:
                        return error("试卷不存在")
                    return success(row)
        except Exception as e:
            print(f"获取试卷详情失败: {str(e)}")
            return error(f"获取试卷详情失败: {str(e)}")

    @staticmethod
    def create_paper(
        paper_name: str,
        duration: int = 60,
        start_time: Optional[str] = None,
        end_time: Optional[str] = None,
        description: Optional[str] = None,
        image_url: Optional[str] = None,
        author: Optional[str] = None,
        author_id: Optional[int] = None,
        status: str = "enabled",
        current_user: Optional[Dict[str, Any]] = None
    ):
        """创建试卷"""
        try:
            with get_db_connection() as conn:
                with conn.cursor() as cursor:
                    sql = """
                        INSERT INTO py_paper
                        (paperName, duration, startTime, endTime, description, imageUrl,
                         totalScore, questionCount, status, author, authorId, createTime, updateTime)
                        VALUES
                        (%s, %s, %s, %s, %s, %s, '0', 0, %s, %s, %s, NOW(), NOW())
                    """
                    params = [
                        paper_name, duration, start_time, end_time, description, image_url,
                        status, author, author_id
                    ]
                    print(f"执行SQL: {sql}, 参数: {params}")
                    cursor.execute(sql, params)
                    conn.commit()
                    new_id = cursor.lastrowid
                    return success({"id": new_id}, "试卷创建成功")
        except Exception as e:
            print(f"创建试卷失败: {str(e)}")
            return error(f"创建试卷失败: {str(e)}")

    @staticmethod
    def update_paper(
        paper_id: int,
        paper_name: str,
        duration: int,
        start_time: Optional[str],
        end_time: Optional[str],
        description: Optional[str],
        image_url: Optional[str],
        status: str,
        current_user: Optional[Dict[str, Any]] = None
    ):
        """更新试卷"""
        try:
            with get_db_connection() as conn:
                with conn.cursor() as cursor:
                    if not PaperService._has_paper_access(cursor, paper_id, current_user):
                        return error("试卷不存在")

                    sql = """
                        UPDATE py_paper
                        SET paperName=%s, duration=%s, startTime=%s, endTime=%s, description=%s,
                            imageUrl=%s, status=%s, updateTime=NOW()
                        WHERE id=%s
                    """
                    params = [
                        paper_name, duration, start_time, end_time, description, image_url, status, paper_id
                    ]
                    print(f"执行SQL: {sql}, 参数: {params}")
                    cursor.execute(sql, params)
                    conn.commit()
                    return success(None, "试卷更新成功")
        except Exception as e:
            print(f"更新试卷失败: {str(e)}")
            return error(f"更新试卷失败: {str(e)}")

    @staticmethod
    def delete_paper(
        paper_id: int,
        current_user: Optional[Dict[str, Any]] = None
    ):
        """删除试卷"""
        try:
            with get_db_connection() as conn:
                with conn.cursor() as cursor:
                    if not PaperService._has_paper_access(cursor, paper_id, current_user):
                        return error("试卷不存在")

                    # 删除试卷题目关系
                    delete_relation_sql = "DELETE FROM py_paper_question WHERE paperId = %s"
                    print(f"执行SQL: {delete_relation_sql}, 参数: [{paper_id}]")
                    cursor.execute(delete_relation_sql, [paper_id])

                    # 删除试卷
                    sql = "DELETE FROM py_paper WHERE id = %s"
                    print(f"执行SQL: {sql}, 参数: [{paper_id}]")
                    cursor.execute(sql, [paper_id])
                    conn.commit()
                    return success(None, "试卷删除成功")
        except Exception as e:
            print(f"删除试卷失败: {str(e)}")
            return error(f"删除试卷失败: {str(e)}")

    @staticmethod
    def toggle_paper_status(
        paper_id: int,
        current_user: Optional[Dict[str, Any]] = None
    ):
        """切换试卷状态 enabled/disabled"""
        try:
            with get_db_connection() as conn:
                with conn.cursor() as cursor:
                    where_conditions: List[str] = ["p.id = %s"]
                    params: List[Any] = [paper_id]
                    PaperService._append_paper_access_scope(where_conditions, params, current_user)
                    get_sql = """
                        SELECT p.status
                        FROM py_paper p
                        WHERE {where_clause}
                    """.format(where_clause=" AND ".join(where_conditions))
                    print(f"执行SQL: {get_sql}, 参数: {params}")
                    cursor.execute(get_sql, params)
                    row = cursor.fetchone()
                    if not row:
                        return error("试卷不存在")

                    current = row["status"] or "enabled"
                    new_status = "disabled" if current == "enabled" else "enabled"

                    upd_sql = "UPDATE py_paper SET status=%s, updateTime=NOW() WHERE id=%s"
                    print(f"执行SQL: {upd_sql}, 参数: [{new_status}, {paper_id}]")
                    cursor.execute(upd_sql, [new_status, paper_id])
                    conn.commit()
                    return success(None, f"状态已更新为 {new_status}")
        except Exception as e:
            print(f"切换试卷状态失败: {str(e)}")
            return error(f"切换试卷状态失败: {str(e)}")

    @staticmethod
    def get_paper_questions(
        paper_id: int,
        current_user: Optional[Dict[str, Any]] = None
    ):
        """获取试卷中的题目列表"""
        try:
            with get_db_connection() as conn:
                with conn.cursor() as cursor:
                    if not PaperService._has_paper_access(cursor, paper_id, current_user):
                        return error("试卷不存在")

                    sql = """
                        SELECT pq.id, pq.paperId, pq.questionId, pq.orderNum, pq.score,
                               q.content, q.questionType, q.optionA, q.optionB, q.optionC, q.optionD,
                               q.score as defaultScore, q.subject, q.grade, q.category
                        FROM py_paper_question pq
                        LEFT JOIN py_question_bank q ON pq.questionId = q.id
                        WHERE pq.paperId = %s
                        ORDER BY pq.orderNum ASC, pq.id ASC
                    """
                    print(f"执行SQL: {sql}, 参数: [{paper_id}]")
                    cursor.execute(sql, [paper_id])
                    rows = cursor.fetchall()
                    return success(rows)
        except Exception as e:
            print(f"获取试卷题目列表失败: {str(e)}")
            return error(f"获取试卷题目列表失败: {str(e)}")

    @staticmethod
    def add_question_to_paper(
        paper_id: int,
        question_id: int,
        order_num: Optional[int] = None,
        score: Optional[str] = None,
        current_user: Optional[Dict[str, Any]] = None
    ):
        """手动添加题目到试卷"""
        try:
            with get_db_connection() as conn:
                with conn.cursor() as cursor:
                    if not PaperService._has_paper_access(cursor, paper_id, current_user):
                        return error("试卷不存在")

                    # 检查题目是否存在
                    check_question_sql = "SELECT id, score FROM py_question_bank WHERE id = %s AND status = 'enabled'"
                    print(f"执行SQL: {check_question_sql}, 参数: [{question_id}]")
                    cursor.execute(check_question_sql, [question_id])
                    question = cursor.fetchone()
                    if not question:
                        return error("题目不存在或已禁用")

                    # 检查是否已存在
                    check_exist_sql = "SELECT id FROM py_paper_question WHERE paperId = %s AND questionId = %s"
                    print(f"执行SQL: {check_exist_sql}, 参数: [{paper_id}, {question_id}]")
                    cursor.execute(check_exist_sql, [paper_id, question_id])
                    if cursor.fetchone():
                        return error("题目已存在于试卷中")

                    # 如果没有指定顺序，获取最大顺序号
                    if order_num is None:
                        max_order_sql = "SELECT MAX(orderNum) as maxOrder FROM py_paper_question WHERE paperId = %s"
                        cursor.execute(max_order_sql, [paper_id])
                        result = cursor.fetchone()
                        order_num = (result['maxOrder'] or 0) + 1

                    # 如果没有指定分值，使用题目默认分值
                    if score is None:
                        score = question['score'] or '10'

                    # 插入关系
                    insert_sql = """
                        INSERT INTO py_paper_question (paperId, questionId, orderNum, score, createTime)
                        VALUES (%s, %s, %s, %s, NOW())
                    """
                    print(f"执行SQL: {insert_sql}, 参数: [{paper_id}, {question_id}, {order_num}, {score}]")
                    cursor.execute(insert_sql, [paper_id, question_id, order_num, score])

                    # 更新试卷的题目数量和总分
                    PaperService._update_paper_statistics(conn, cursor, paper_id)

                    conn.commit()
                    return success(None, "题目添加成功")
        except pymysql.err.IntegrityError:
            return error("题目已存在于试卷中")
        except Exception as e:
            print(f"添加题目到试卷失败: {str(e)}")
            return error(f"添加题目到试卷失败: {str(e)}")

    @staticmethod
    def remove_question_from_paper(
        paper_id: int,
        paper_question_id: int,
        current_user: Optional[Dict[str, Any]] = None
    ):
        """从试卷中删除题目"""
        try:
            with get_db_connection() as conn:
                with conn.cursor() as cursor:
                    if not PaperService._has_paper_access(cursor, paper_id, current_user):
                        return error("试卷不存在")

                    # 删除关系
                    delete_sql = "DELETE FROM py_paper_question WHERE id = %s AND paperId = %s"
                    print(f"执行SQL: {delete_sql}, 参数: [{paper_question_id}, {paper_id}]")
                    cursor.execute(delete_sql, [paper_question_id, paper_id])
                    
                    if cursor.rowcount == 0:
                        return error("题目不存在于试卷中")

                    # 更新试卷的题目数量和总分
                    PaperService._update_paper_statistics(conn, cursor, paper_id)

                    conn.commit()
                    return success(None, "题目删除成功")
        except Exception as e:
            print(f"从试卷中删除题目失败: {str(e)}")
            return error(f"从试卷中删除题目失败: {str(e)}")

    @staticmethod
    def auto_generate_paper(
        paper_id: int,
        subject: Optional[str] = None,
        grade: Optional[str] = None,
        question_config: Optional[Dict[str, int]] = None,
        current_user: Optional[Dict[str, Any]] = None
    ):
        """
        自动组卷
        Args:
            paper_id: 试卷ID
            subject: 学科筛选
            grade: 年级筛选
            question_config: 题型配置，如 {'single_choice': 10, 'multiple_choice': 5, ...}
        """
        try:
            with get_db_connection() as conn:
                with conn.cursor() as cursor:
                    if not PaperService._has_paper_access(cursor, paper_id, current_user):
                        return error("试卷不存在")

                    # 清空现有题目
                    clear_sql = "DELETE FROM py_paper_question WHERE paperId = %s"
                    print(f"执行SQL: {clear_sql}, 参数: [{paper_id}]")
                    cursor.execute(clear_sql, [paper_id])

                    if not question_config:
                        question_config = {}

                    order_num = 1
                    selected_question_ids = set()

                    # 按题型配置抽取题目
                    for question_type, count in question_config.items():
                        if count <= 0:
                            continue

                        # 构建查询条件
                        where_conditions = ["status = 'enabled'"]
                        params = []

                        if subject:
                            where_conditions.append("subject = %s")
                            params.append(subject)

                        if grade:
                            where_conditions.append("grade = %s")
                            params.append(grade)

                        where_conditions.append("questionType = %s")
                        params.append(question_type)

                        where_clause = "WHERE " + " AND ".join(where_conditions)

                        # 查询符合条件的题目
                        query_sql = f"""
                            SELECT id, score FROM py_question_bank
                            {where_clause}
                        """
                        print(f"执行SQL: {query_sql}, 参数: {params}")
                        cursor.execute(query_sql, params)
                        available_questions = cursor.fetchall()

                        if len(available_questions) < count:
                            return error(f"{question_type}类型的题目不足，需要{count}道，但只有{len(available_questions)}道")

                        # 随机选择题目
                        selected = random.sample(available_questions, count)
                        
                        # 插入到试卷
                        for question in selected:
                            if question['id'] in selected_question_ids:
                                continue  # 避免重复
                            
                            selected_question_ids.add(question['id'])
                            insert_sql = """
                                INSERT INTO py_paper_question (paperId, questionId, orderNum, score, createTime)
                                VALUES (%s, %s, %s, %s, NOW())
                            """
                            score = question['score'] or '10'
                            print(f"执行SQL: {insert_sql}, 参数: [{paper_id}, {question['id']}, {order_num}, {score}]")
                            cursor.execute(insert_sql, [paper_id, question['id'], order_num, score])
                            order_num += 1

                    # 更新试卷的题目数量和总分
                    PaperService._update_paper_statistics(conn, cursor, paper_id)

                    conn.commit()
                    return success(None, f"自动组卷成功，共添加{len(selected_question_ids)}道题目")
        except Exception as e:
            print(f"自动组卷失败: {str(e)}")
            return error(f"自动组卷失败: {str(e)}")

    @staticmethod
    def get_front_paper_list(
        page: int = 1,
        limit: int = 10,
        keyword: str = '',
        current_user: Optional[Dict[str, Any]] = None
    ):
        """
        获取前台试卷列表（仅显示已启用的，支持分页和搜索）
        
        Args:
            page: 页码
            limit: 每页数量
            keyword: 关键词搜索
            
        Returns:
            dict: 响应数据
        """
        try:
            with get_db_connection() as conn:
                with conn.cursor() as cursor:
                    # 构建查询条件
                    where_conditions = ["p.status = 'enabled'"]  # 只显示已启用的
                    params = []
                    
                    if keyword:
                        where_conditions.append("p.paperName LIKE %s")
                        params.append(f'%{keyword}%')

                    PaperService._append_front_paper_scope(where_conditions, params, current_user)
                    
                    where_clause = "WHERE " + " AND ".join(where_conditions)
                    
                    # 查询总数
                    count_sql = f"SELECT COUNT(*) as total FROM py_paper p {where_clause}"
                    print(f"执行SQL: {count_sql}, 参数: {params}")
                    cursor.execute(count_sql, params)
                    total = cursor.fetchone()['total']
                    
                    # 查询数据
                    offset = (page - 1) * limit
                    data_sql = f"""
                        SELECT p.id, p.paperName, p.duration, p.startTime, p.endTime, p.description, p.imageUrl,
                               p.totalScore, p.questionCount, p.author, p.createTime
                        FROM py_paper p
                        {where_clause}
                        ORDER BY p.createTime DESC
                        LIMIT %s OFFSET %s
                    """
                    params.extend([limit, offset])
                    print(f"执行SQL: {data_sql}, 参数: {params}")
                    cursor.execute(data_sql, params)
                    rows = cursor.fetchall()
                    
                    # 格式化时间
                    for row in rows:
                        if row.get('createTime'):
                            row['createTime'] = row['createTime'].strftime('%Y-%m-%d %H:%M:%S')
                        if row.get('startTime'):
                            row['startTime'] = row['startTime'].strftime('%Y-%m-%d %H:%M:%S')
                        if row.get('endTime'):
                            row['endTime'] = row['endTime'].strftime('%Y-%m-%d %H:%M:%S')
                    
                    return page_response(rows, total, page, limit)
                    
        except Exception as e:
            print(f"获取前台试卷列表失败: {str(e)}")
            return error(f"获取前台试卷列表失败: {str(e)}")

    @staticmethod
    def get_front_paper_detail(
        paper_id: int,
        current_user: Optional[Dict[str, Any]] = None
    ):
        """获取前台试卷详情（仅返回已启用的试卷）"""
        try:
            with get_db_connection() as conn:
                with conn.cursor() as cursor:
                    where_conditions: List[str] = ["p.id = %s", "p.status = 'enabled'"]
                    params: List[Any] = [paper_id]
                    PaperService._append_front_paper_scope(where_conditions, params, current_user)
                    sql = """
                        SELECT p.id, p.paperName, p.duration, p.startTime, p.endTime, p.description, p.imageUrl,
                               p.totalScore, p.questionCount, p.author, p.createTime
                        FROM py_paper p
                        WHERE {where_clause}
                    """.format(where_clause=" AND ".join(where_conditions))
                    print(f"执行SQL: {sql}, 参数: {params}")
                    cursor.execute(sql, params)
                    row = cursor.fetchone()
                    if not row:
                        return error("试卷不存在或已禁用")
                    
                    # 统计各题型数量
                    type_count_sql = """
                        SELECT q.questionType, COUNT(*) as count
                        FROM py_paper_question pq
                        LEFT JOIN py_question_bank q ON pq.questionId = q.id
                        WHERE pq.paperId = %s
                        GROUP BY q.questionType
                    """
                    print(f"执行SQL: {type_count_sql}, 参数: [{paper_id}]")
                    cursor.execute(type_count_sql, [paper_id])
                    type_counts = cursor.fetchall()
                    
                    # 构建题型统计字典
                    question_type_stats = {
                        'single_choice': 0,
                        'multiple_choice': 0,
                        'fill_blank': 0,
                        'essay': 0,
                        'judge': 0
                    }
                    
                    for item in type_counts:
                        q_type = item.get('questionType')
                        count = item.get('count', 0)
                        if q_type in question_type_stats:
                            question_type_stats[q_type] = count
                    
                    row['questionTypeStats'] = question_type_stats
                    
                    # 格式化时间
                    if row.get('createTime'):
                        row['createTime'] = row['createTime'].strftime('%Y-%m-%d %H:%M:%S')
                    if row.get('startTime'):
                        row['startTime'] = row['startTime'].strftime('%Y-%m-%d %H:%M:%S')
                    if row.get('endTime'):
                        row['endTime'] = row['endTime'].strftime('%Y-%m-%d %H:%M:%S')
                    
                    return success(row)
        except Exception as e:
            print(f"获取前台试卷详情失败: {str(e)}")
            return error(f"获取前台试卷详情失败: {str(e)}")

    @staticmethod
    def _update_paper_statistics(conn, cursor, paper_id: int):
        """更新试卷的题目数量和总分"""
        try:
            # 计算题目数量和总分
            stats_sql = """
                SELECT COUNT(*) as count, COALESCE(SUM(CAST(COALESCE(NULLIF(pq.score, ''), q.score, '0') AS DECIMAL(10,2))), 0) as total
                FROM py_paper_question pq
                LEFT JOIN py_question_bank q ON pq.questionId = q.id
                WHERE pq.paperId = %s
            """
            print(f"执行SQL: {stats_sql}, 参数: [{paper_id}]")
            cursor.execute(stats_sql, [paper_id])
            stats = cursor.fetchone()

            question_count = stats['count'] or 0
            total_score = str(stats['total'] or 0)

            # 更新试卷
            update_sql = "UPDATE py_paper SET questionCount = %s, totalScore = %s, updateTime = NOW() WHERE id = %s"
            print(f"执行SQL: {update_sql}, 参数: [{question_count}, {total_score}, {paper_id}]")
            cursor.execute(update_sql, [question_count, total_score, paper_id])
        except Exception as e:
            print(f"更新试卷统计信息失败: {str(e)}")
            raise e

