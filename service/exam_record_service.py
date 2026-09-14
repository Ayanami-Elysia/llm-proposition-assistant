"""
考试记录管理 服务层
"""
import pymysql
from datetime import datetime
from typing import Any, Dict, List, Optional

from utils.db_utils import get_db_connection
from utils.response import success, error, page_response


class ExamRecordService:
    """考试记录服务类"""

    @staticmethod
    def _append_exam_record_scope(
        where_conditions: List[str],
        params: List[Any],
        current_user: Optional[Dict[str, Any]],
        exam_alias: str = "er"
    ) -> None:
        """追加教师端考试记录访问范围"""
        if not current_user or current_user.get("role") != "doctor":
            return

        class_id = current_user.get("class_id")
        if not class_id:
            user_id = current_user.get("id")
            where_conditions.append(f"""
                EXISTS (
                    SELECT 1
                    FROM py_paper p
                    WHERE p.id = {exam_alias}.paperId
                      AND p.authorId = %s
                )
            """)
            params.append(user_id)
            return
        where_conditions.append(f"""
            EXISTS (
                SELECT 1
                FROM py_user su
                WHERE su.id = {exam_alias}.studentId
                  AND (su.class_id = %s OR su.class_id IS NULL)
            )
        """)
        params.append(class_id)

    @staticmethod
    def _get_exam_record(
        cursor: Any,
        exam_record_id: int,
        current_user: Optional[Dict[str, Any]],
        fields: str = "er.id"
    ) -> Optional[Dict[str, Any]]:
        """按权限获取考试记录"""
        where_conditions: List[str] = ["er.id = %s"]
        params: List[Any] = [exam_record_id]
        ExamRecordService._append_exam_record_scope(where_conditions, params, current_user)
        sql = f"""
            SELECT {fields}
            FROM py_exam_record er
            WHERE {' AND '.join(where_conditions)}
        """
        cursor.execute(sql, params)
        return cursor.fetchone()

    @staticmethod
    def get_exam_record_list(
        page_num: int = 1,
        page_size: int = 10,
        status: Optional[str] = None,
        review_status: Optional[str] = None,
        keyword: Optional[str] = None,
        paper_id: Optional[int] = None,
        student_id: Optional[int] = None,
        current_user: Optional[Dict[str, Any]] = None
    ):
        """
        获取考试记录列表（分页 + 条件）
        Args:
            page_num: 页码
            page_size: 每页数量
            status: 状态筛选（in_progress/submitted/graded）
            review_status: 批阅状态筛选（pending/reviewing/completed）
            keyword: 关键字（匹配试卷名称/学生姓名）
            paper_id: 试卷ID筛选
            student_id: 学生ID筛选
        """
        try:
            with get_db_connection() as conn:
                with conn.cursor() as cursor:
                    where_conditions = []
                    params = []

                    if status:
                        where_conditions.append("er.status = %s")
                        params.append(status)

                    if review_status:
                        where_conditions.append("er.reviewStatus = %s")
                        params.append(review_status)

                    if paper_id:
                        where_conditions.append("er.paperId = %s")
                        params.append(paper_id)

                    if student_id:
                        where_conditions.append("er.studentId = %s")
                        params.append(student_id)

                    if keyword:
                        where_conditions.append("(er.paperName LIKE %s OR er.studentName LIKE %s)")
                        params.extend([f"%{keyword}%", f"%{keyword}%"])

                    ExamRecordService._append_exam_record_scope(where_conditions, params, current_user)
                    where_clause = f"WHERE {' AND '.join(where_conditions)}" if where_conditions else ""

                    # total
                    count_sql = f"SELECT COUNT(*) AS total FROM py_exam_record er {where_clause}"
                    print(f"执行SQL: {count_sql}, 参数: {params}")
                    cursor.execute(count_sql, params)
                    total = cursor.fetchone()["total"]

                    # rows
                    offset = (page_num - 1) * page_size
                    data_sql = f"""
                        SELECT er.id, er.paperId, er.paperName, er.studentId, er.studentName, er.startTime,
                               er.endTime, er.submitTime, er.totalScore, er.obtainedScore, er.status,
                               er.reviewStatus, er.reviewerId, er.reviewerName, er.reviewTime,
                               er.reviewRemark, er.createTime, er.updateTime
                        FROM py_exam_record er
                        {where_clause}
                        ORDER BY er.createTime DESC
                        LIMIT %s OFFSET %s
                    """
                    query_params = list(params) + [page_size, offset]
                    print(f"执行SQL: {data_sql}, 参数: {query_params}")
                    cursor.execute(data_sql, query_params)
                    rows = cursor.fetchall()

                    # 格式化时间
                    for row in rows:
                        if row.get('startTime'):
                            row['startTime'] = row['startTime'].strftime('%Y-%m-%d %H:%M:%S')
                        if row.get('endTime'):
                            row['endTime'] = row['endTime'].strftime('%Y-%m-%d %H:%M:%S')
                        if row.get('submitTime'):
                            row['submitTime'] = row['submitTime'].strftime('%Y-%m-%d %H:%M:%S')
                        if row.get('reviewTime'):
                            row['reviewTime'] = row['reviewTime'].strftime('%Y-%m-%d %H:%M:%S')
                        if row.get('createTime'):
                            row['createTime'] = row['createTime'].strftime('%Y-%m-%d %H:%M:%S')
                        if row.get('updateTime'):
                            row['updateTime'] = row['updateTime'].strftime('%Y-%m-%d %H:%M:%S')

                    return page_response(rows, total, page_num, page_size)
        except Exception as e:
            print(f"获取考试记录列表失败: {str(e)}")
            return error(f"获取考试记录列表失败: {str(e)}")

    @staticmethod
    def get_exam_record_by_id(
        exam_record_id: int,
        current_user: Optional[Dict[str, Any]] = None
    ):
        """根据ID获取考试记录详情"""
        try:
            with get_db_connection() as conn:
                with conn.cursor() as cursor:
                    where_conditions: List[str] = ["er.id = %s"]
                    params: List[Any] = [exam_record_id]
                    ExamRecordService._append_exam_record_scope(
                        where_conditions,
                        params,
                        current_user
                    )
                    sql = """
                        SELECT er.id, er.paperId, er.paperName, er.studentId, er.studentName, er.startTime,
                               er.endTime, er.submitTime, er.totalScore, er.obtainedScore, er.status,
                               er.reviewStatus, er.reviewerId, er.reviewerName, er.reviewTime,
                               er.reviewRemark, er.createTime, er.updateTime
                        FROM py_exam_record er
                        WHERE {where_clause}
                    """.format(where_clause=" AND ".join(where_conditions))
                    print(f"执行SQL: {sql}, 参数: {params}")
                    cursor.execute(sql, params)
                    row = cursor.fetchone()
                    if not row:
                        return error("考试记录不存在")
                    
                    # 格式化时间
                    if row.get('startTime'):
                        row['startTime'] = row['startTime'].strftime('%Y-%m-%d %H:%M:%S')
                    if row.get('endTime'):
                        row['endTime'] = row['endTime'].strftime('%Y-%m-%d %H:%M:%S')
                    if row.get('submitTime'):
                        row['submitTime'] = row['submitTime'].strftime('%Y-%m-%d %H:%M:%S')
                    if row.get('reviewTime'):
                        row['reviewTime'] = row['reviewTime'].strftime('%Y-%m-%d %H:%M:%S')
                    if row.get('createTime'):
                        row['createTime'] = row['createTime'].strftime('%Y-%m-%d %H:%M:%S')
                    if row.get('updateTime'):
                        row['updateTime'] = row['updateTime'].strftime('%Y-%m-%d %H:%M:%S')
                    
                    return success(row)
        except Exception as e:
            print(f"获取考试记录详情失败: {str(e)}")
            return error(f"获取考试记录详情失败: {str(e)}")

    @staticmethod
    def get_answer_records(
        exam_record_id: int,
        current_user: Optional[Dict[str, Any]] = None
    ):
        """获取考试记录的答题详情"""
        try:
            with get_db_connection() as conn:
                with conn.cursor() as cursor:
                    if not ExamRecordService._get_exam_record(cursor, exam_record_id, current_user):
                        return error("考试记录不存在")

                    sql = """
                        SELECT ar.id, ar.examRecordId, ar.questionId, ar.questionType, ar.studentAnswer,
                               ar.correctAnswer, ar.isCorrect, ar.score, ar.obtainedScore, ar.teacherScore,
                               ar.teacherRemark, ar.isWrong,
                               q.content, q.optionA, q.optionB, q.optionC, q.optionD, q.analysis, q.imageUrl
                        FROM py_answer_record ar
                        LEFT JOIN py_question_bank q ON ar.questionId = q.id
                        WHERE ar.examRecordId = %s
                        ORDER BY ar.id ASC
                    """
                    print(f"执行SQL: {sql}, 参数: [{exam_record_id}]")
                    cursor.execute(sql, [exam_record_id])
                    rows = cursor.fetchall()
                    return success(rows)
        except Exception as e:
            print(f"获取答题记录失败: {str(e)}")
            return error(f"获取答题记录失败: {str(e)}")

    @staticmethod
    def review_exam_record(
        exam_record_id: int,
        reviewer_id: int,
        reviewer_name: str,
        review_remark: Optional[str] = None,
        current_user: Optional[Dict[str, Any]] = None
    ):
        """批阅考试记录"""
        try:
            with get_db_connection() as conn:
                with conn.cursor() as cursor:
                    exam_record = ExamRecordService._get_exam_record(
                        cursor,
                        exam_record_id,
                        current_user,
                        "er.id, er.status"
                    )
                    if not exam_record:
                        return error("考试记录不存在")

                    # 更新考试记录批阅信息
                    update_sql = """
                        UPDATE py_exam_record
                        SET reviewStatus = 'completed', reviewerId = %s, reviewerName = %s,
                            reviewTime = NOW(), reviewRemark = %s, status = 'graded', updateTime = NOW()
                        WHERE id = %s
                    """
                    params = [reviewer_id, reviewer_name, review_remark, exam_record_id]
                    print(f"执行SQL: {update_sql}, 参数: {params}")
                    cursor.execute(update_sql, params)
                    conn.commit()
                    return success(None, "批阅完成")
        except Exception as e:
            print(f"批阅考试记录失败: {str(e)}")
            return error(f"批阅考试记录失败: {str(e)}")

    @staticmethod
    def review_answer(
        answer_record_id: int,
        teacher_score: Optional[str] = None,
        teacher_remark: Optional[str] = None,
        is_wrong: Optional[int] = None,
        current_user: Optional[Dict[str, Any]] = None
    ):
        """批阅单个答题记录（主观题评分）"""
        try:
            with get_db_connection() as conn:
                with conn.cursor() as cursor:
                    where_conditions: List[str] = ["ar.id = %s"]
                    params: List[Any] = [answer_record_id]
                    ExamRecordService._append_exam_record_scope(where_conditions, params, current_user)
                    check_sql = """
                        SELECT ar.id, ar.examRecordId
                        FROM py_answer_record ar
                        LEFT JOIN py_exam_record er ON ar.examRecordId = er.id
                        WHERE {where_clause}
                    """.format(where_clause=" AND ".join(where_conditions))
                    print(f"执行SQL: {check_sql}, 参数: {params}")
                    cursor.execute(check_sql, params)
                    answer_record = cursor.fetchone()
                    if not answer_record:
                        return error("答题记录不存在")

                    # 构建更新字段
                    update_fields = []
                    params = []

                    if teacher_score is not None:
                        update_fields.append("teacherScore = %s")
                        params.append(teacher_score)
                        # 同时更新获得分数
                        update_fields.append("obtainedScore = %s")
                        params.append(teacher_score)

                    if teacher_remark is not None:
                        update_fields.append("teacherRemark = %s")
                        params.append(teacher_remark)

                    if is_wrong is not None:
                        update_fields.append("isWrong = %s")
                        params.append(is_wrong)

                    if not update_fields:
                        return error("请至少提供一个批阅信息")

                    update_fields.append("updateTime = NOW()")
                    params.append(answer_record_id)

                    update_sql = f"""
                        UPDATE py_answer_record
                        SET {', '.join(update_fields)}
                        WHERE id = %s
                    """
                    print(f"执行SQL: {update_sql}, 参数: {params}")
                    cursor.execute(update_sql, params)

                    # 重新计算考试记录总分
                    ExamRecordService._update_exam_record_score(conn, cursor, answer_record['examRecordId'])

                    conn.commit()
                    return success(None, "批阅成功")
        except Exception as e:
            print(f"批阅答题记录失败: {str(e)}")
            return error(f"批阅答题记录失败: {str(e)}")

    @staticmethod
    def _update_exam_record_score(conn, cursor, exam_record_id: int):
        """更新考试记录的总分"""
        try:
            # 计算总分
            score_sql = """
                SELECT COALESCE(SUM(CAST(COALESCE(NULLIF(obtainedScore, ''), '0') AS DECIMAL(10,2))), 0) as total
                FROM py_answer_record
                WHERE examRecordId = %s
            """
            print(f"执行SQL: {score_sql}, 参数: [{exam_record_id}]")
            cursor.execute(score_sql, [exam_record_id])
            result = cursor.fetchone()
            total_score = str(result['total'] or 0)

            # 更新考试记录
            update_sql = "UPDATE py_exam_record SET obtainedScore = %s, updateTime = NOW() WHERE id = %s"
            print(f"执行SQL: {update_sql}, 参数: [{total_score}, {exam_record_id}]")
            cursor.execute(update_sql, [total_score, exam_record_id])
        except Exception as e:
            print(f"更新考试记录总分失败: {str(e)}")
            raise e

    @staticmethod
    def delete_exam_record(
        exam_record_id: int,
        current_user: Optional[Dict[str, Any]] = None
    ):
        """删除考试记录（同时删除答题记录）"""
        try:
            with get_db_connection() as conn:
                with conn.cursor() as cursor:
                    if not ExamRecordService._get_exam_record(cursor, exam_record_id, current_user):
                        return error("考试记录不存在")

                    # 删除答题记录
                    delete_answer_sql = "DELETE FROM py_answer_record WHERE examRecordId = %s"
                    print(f"执行SQL: {delete_answer_sql}, 参数: [{exam_record_id}]")
                    cursor.execute(delete_answer_sql, [exam_record_id])

                    # 删除考试记录
                    delete_exam_sql = "DELETE FROM py_exam_record WHERE id = %s"
                    print(f"执行SQL: {delete_exam_sql}, 参数: [{exam_record_id}]")
                    cursor.execute(delete_exam_sql, [exam_record_id])
                    conn.commit()
                    return success(None, "考试记录删除成功")
        except Exception as e:
            print(f"删除考试记录失败: {str(e)}")
            return error(f"删除考试记录失败: {str(e)}")

    @staticmethod
    def start_exam(paper_id: int, student_id: int, student_name: str):
        """开始考试（创建考试记录并获取题目）"""
        try:
            with get_db_connection() as conn:
                with conn.cursor() as cursor:
                    # 检查试卷是否存在
                    paper_sql = """
                        SELECT id, paperName, duration, totalScore
                        FROM py_paper
                        WHERE id = %s AND status = 'enabled'
                    """
                    print(f"执行SQL: {paper_sql}, 参数: [{paper_id}]")
                    cursor.execute(paper_sql, [paper_id])
                    paper = cursor.fetchone()
                    if not paper:
                        return error("试卷不存在或已禁用")

                    # 检查是否已有进行中的考试记录
                    check_sql = """
                        SELECT id FROM py_exam_record
                        WHERE paperId = %s AND studentId = %s AND status = 'in_progress'
                    """
                    print(f"执行SQL: {check_sql}, 参数: [{paper_id}, {student_id}]")
                    cursor.execute(check_sql, [paper_id, student_id])
                    existing = cursor.fetchone()
                    if existing:
                        exam_record_id = existing['id']
                    else:
                        # 创建考试记录
                        insert_sql = """
                            INSERT INTO py_exam_record (paperId, paperName, studentId, studentName, startTime, totalScore, status, reviewStatus)
                            VALUES (%s, %s, %s, %s, NOW(), %s, 'in_progress', 'pending')
                        """
                        print(f"执行SQL: {insert_sql}, 参数: [{paper_id}, paper['paperName'], {student_id}, {student_name}, paper['totalScore']]")
                        cursor.execute(insert_sql, [paper_id, paper['paperName'], student_id, student_name, paper['totalScore']])
                        exam_record_id = cursor.lastrowid

                    # 获取试卷题目
                    questions_sql = """
                        SELECT q.id, q.content, q.questionType, q.optionA, q.optionB, q.optionC, q.optionD,
                               q.correctAnswer, q.score, q.imageUrl, q.analysis,
                               COALESCE(NULLIF(pq.score, ''), q.score) as questionScore, 
                               COALESCE(pq.orderNum, 0) as orderNum
                        FROM py_paper_question pq
                        LEFT JOIN py_question_bank q ON pq.questionId = q.id
                        WHERE pq.paperId = %s AND q.status = 'enabled'
                        ORDER BY COALESCE(pq.orderNum, 0) ASC, pq.id ASC
                    """
                    print(f"执行SQL: {questions_sql}, 参数: [{paper_id}]")
                    cursor.execute(questions_sql, [paper_id])
                    questions = cursor.fetchall()

                    # 初始化答题记录（如果不存在）
                    for q in questions:
                        check_answer_sql = """
                            SELECT id FROM py_answer_record
                            WHERE examRecordId = %s AND questionId = %s
                        """
                        cursor.execute(check_answer_sql, [exam_record_id, q['id']])
                        if not cursor.fetchone():
                            insert_answer_sql = """
                                INSERT INTO py_answer_record (examRecordId, questionId, questionType, correctAnswer, score)
                                VALUES (%s, %s, %s, %s, %s)
                            """
                            cursor.execute(insert_answer_sql, [
                                exam_record_id, q['id'], q['questionType'],
                                q['correctAnswer'], q['questionScore'] or q['score']
                            ])

                    conn.commit()

                    # 获取考试记录信息
                    exam_sql = "SELECT id, startTime, totalScore FROM py_exam_record WHERE id = %s"
                    cursor.execute(exam_sql, [exam_record_id])
                    exam_record = cursor.fetchone()

                    return success({
                        'examRecordId': exam_record_id,
                        'paperName': paper['paperName'],
                        'duration': paper['duration'],
                        'totalScore': exam_record['totalScore'],
                        'startTime': exam_record['startTime'].strftime('%Y-%m-%d %H:%M:%S'),
                        'questions': questions
                    })
        except Exception as e:
            print(f"开始考试失败: {str(e)}")
            return error(f"开始考试失败: {str(e)}")

    @staticmethod
    def get_exam_questions(exam_record_id: int):
        """获取考试题目列表（包含已保存的答案）"""
        try:
            with get_db_connection() as conn:
                with conn.cursor() as cursor:
                    # 检查考试记录
                    exam_sql = "SELECT id, paperId, status FROM py_exam_record WHERE id = %s"
                    cursor.execute(exam_sql, [exam_record_id])
                    exam_record = cursor.fetchone()
                    if not exam_record:
                        return error("考试记录不存在")

                    # 获取题目和答案
                    sql = """
                        SELECT q.id, q.content, q.questionType, q.optionA, q.optionB, q.optionC, q.optionD,
                               q.correctAnswer, q.imageUrl, q.analysis,
                               ar.studentAnswer, ar.score, ar.obtainedScore, ar.isCorrect,
                               pq.orderNum
                        FROM py_paper_question pq
                        LEFT JOIN py_question_bank q ON pq.questionId = q.id
                        LEFT JOIN py_answer_record ar ON ar.examRecordId = %s AND ar.questionId = q.id
                        WHERE pq.paperId = %s AND q.status = 'enabled'
                        ORDER BY pq.orderNum ASC, pq.id ASC
                    """
                    print(f"执行SQL: {sql}, 参数: [{exam_record_id}, exam_record['paperId']]")
                    cursor.execute(sql, [exam_record_id, exam_record['paperId']])
                    questions = cursor.fetchall()
                    return success(questions)
        except Exception as e:
            print(f"获取考试题目失败: {str(e)}")
            return error(f"获取考试题目失败: {str(e)}")

    @staticmethod
    def _auto_judge_answer(question_type: str, student_answer: str, correct_answer: str) -> tuple:
        """
        自动判题
        返回: (is_correct: bool, obtained_score: str)
        """
        if not student_answer:
            return (None, '0')

        student_answer = student_answer.strip()
        correct_answer = correct_answer.strip()

        if question_type == 'single_choice' or question_type == 'judge':
            # 单选题和判断题：直接比较
            is_correct = student_answer.upper() == correct_answer.upper()
            return (1 if is_correct else 0, None)  # 分数在保存时根据is_correct计算

        elif question_type == 'multiple_choice':
            # 多选题：比较选项集合（忽略顺序）
            student_set = set([x.strip().upper() for x in student_answer.split(',')])
            correct_set = set([x.strip().upper() for x in correct_answer.split(',')])
            is_correct = student_set == correct_set
            return (1 if is_correct else 0, None)

        elif question_type == 'fill_blank':
            # 填空题：简单字符串比较（可以后续优化为模糊匹配）
            is_correct = student_answer.strip() == correct_answer.strip()
            return (1 if is_correct else 0, None)

        elif question_type == 'essay':
            # 解答题：不自动判题，返回None
            return (None, None)

        return (None, '0')

    @staticmethod
    def save_answer(exam_record_id: int, question_id: int, student_answer: str):
        """保存答案（自动判题）"""
        try:
            with get_db_connection() as conn:
                with conn.cursor() as cursor:
                    # 检查考试记录
                    exam_sql = "SELECT id, status FROM py_exam_record WHERE id = %s"
                    cursor.execute(exam_sql, [exam_record_id])
                    exam_record = cursor.fetchone()
                    if not exam_record:
                        return error("考试记录不存在")
                    if exam_record['status'] != 'in_progress':
                        return error("考试已结束，无法修改答案")

                    # 获取题目信息
                    question_sql = """
                        SELECT questionType, correctAnswer, score
                        FROM py_answer_record
                        WHERE examRecordId = %s AND questionId = %s
                    """
                    cursor.execute(question_sql, [exam_record_id, question_id])
                    answer_record = cursor.fetchone()
                    if not answer_record:
                        return error("答题记录不存在")

                    question_type = answer_record['questionType']
                    correct_answer = answer_record['correctAnswer']
                    question_score = answer_record['score']

                    # 自动判题（除解答题外）
                    is_correct = None
                    obtained_score = '0'
                    if question_type != 'essay':
                        is_correct, _ = ExamRecordService._auto_judge_answer(
                            question_type, student_answer, correct_answer
                        )
                        # 根据判题结果计算得分
                        if is_correct == 1:
                            obtained_score = question_score
                        else:
                            obtained_score = '0'
                    else:
                        # 解答题不自动判题，得分待老师批阅
                        obtained_score = '0'

                    # 更新答题记录
                    update_sql = """
                        UPDATE py_answer_record
                        SET studentAnswer = %s, isCorrect = %s, obtainedScore = %s, updateTime = NOW()
                        WHERE examRecordId = %s AND questionId = %s
                    """
                    print(f"执行SQL: {update_sql}, 参数: [{student_answer}, {is_correct}, {obtained_score}, {exam_record_id}, {question_id}]")
                    cursor.execute(update_sql, [student_answer, is_correct, obtained_score, exam_record_id, question_id])

                    # 更新考试记录总分
                    ExamRecordService._update_exam_record_score(conn, cursor, exam_record_id)

                    conn.commit()
                    return success({
                        'isCorrect': is_correct,
                        'obtainedScore': obtained_score
                    }, "答案保存成功")
        except Exception as e:
            print(f"保存答案失败: {str(e)}")
            return error(f"保存答案失败: {str(e)}")

    @staticmethod
    def submit_exam(exam_record_id: int):
        """提交试卷"""
        try:
            with get_db_connection() as conn:
                with conn.cursor() as cursor:
                    # 检查考试记录
                    exam_sql = "SELECT id, status FROM py_exam_record WHERE id = %s"
                    cursor.execute(exam_sql, [exam_record_id])
                    exam_record = cursor.fetchone()
                    if not exam_record:
                        return error("考试记录不存在")
                    if exam_record['status'] != 'in_progress':
                        return error("考试已提交")

                    # 对未作答的题目进行判题（记0分）
                    unanswered_sql = """
                        UPDATE py_answer_record
                        SET isCorrect = 0, obtainedScore = '0', updateTime = NOW()
                        WHERE examRecordId = %s AND (studentAnswer IS NULL OR studentAnswer = '')
                    """
                    cursor.execute(unanswered_sql, [exam_record_id])

                    # 更新考试记录总分
                    ExamRecordService._update_exam_record_score(conn, cursor, exam_record_id)

                    # 更新考试记录状态
                    update_sql = """
                        UPDATE py_exam_record
                        SET status = 'submitted', submitTime = NOW(), updateTime = NOW()
                        WHERE id = %s
                    """
                    cursor.execute(update_sql, [exam_record_id])

                    # 获取最终得分
                    score_sql = "SELECT obtainedScore FROM py_exam_record WHERE id = %s"
                    cursor.execute(score_sql, [exam_record_id])
                    final_score = cursor.fetchone()['obtainedScore']

                    conn.commit()
                    return success({
                        'obtainedScore': final_score
                    }, "试卷提交成功")
        except Exception as e:
            print(f"提交试卷失败: {str(e)}")
            return error(f"提交试卷失败: {str(e)}")

    @staticmethod
    def get_front_exam_record_list(
        student_id: int,
        page_num: int = 1,
        page_size: int = 10,
        status: Optional[str] = None,
        keyword: Optional[str] = None
    ):
        """
        获取前台用户考试记录列表（分页 + 条件）
        Args:
            student_id: 学生ID（必须）
            page_num: 页码
            page_size: 每页数量
            status: 状态筛选（in_progress/submitted/graded）
            keyword: 关键字（匹配试卷名称）
        """
        try:
            with get_db_connection() as conn:
                with conn.cursor() as cursor:
                    where_conditions = ["studentId = %s"]
                    params = [student_id]

                    if status:
                        where_conditions.append("status = %s")
                        params.append(status)

                    if keyword:
                        where_conditions.append("paperName LIKE %s")
                        params.append(f"%{keyword}%")

                    where_clause = f"WHERE {' AND '.join(where_conditions)}"

                    # total
                    count_sql = f"SELECT COUNT(*) AS total FROM py_exam_record {where_clause}"
                    print(f"执行SQL: {count_sql}, 参数: {params}")
                    cursor.execute(count_sql, params)
                    total = cursor.fetchone()["total"]

                    # rows
                    offset = (page_num - 1) * page_size
                    data_sql = f"""
                        SELECT id, paperId, paperName, studentId, studentName, startTime, endTime, submitTime,
                               totalScore, obtainedScore, status, reviewStatus, reviewerId, reviewerName,
                               reviewTime, reviewRemark, createTime, updateTime
                        FROM py_exam_record
                        {where_clause}
                        ORDER BY createTime DESC
                        LIMIT %s OFFSET %s
                    """
                    query_params = list(params) + [page_size, offset]
                    print(f"执行SQL: {data_sql}, 参数: {query_params}")
                    cursor.execute(data_sql, query_params)
                    rows = cursor.fetchall()

                    # 格式化时间
                    for row in rows:
                        if row.get('startTime'):
                            row['startTime'] = row['startTime'].strftime('%Y-%m-%d %H:%M:%S')
                        if row.get('endTime'):
                            row['endTime'] = row['endTime'].strftime('%Y-%m-%d %H:%M:%S')
                        if row.get('submitTime'):
                            row['submitTime'] = row['submitTime'].strftime('%Y-%m-%d %H:%M:%S')
                        if row.get('reviewTime'):
                            row['reviewTime'] = row['reviewTime'].strftime('%Y-%m-%d %H:%M:%S')
                        if row.get('createTime'):
                            row['createTime'] = row['createTime'].strftime('%Y-%m-%d %H:%M:%S')
                        if row.get('updateTime'):
                            row['updateTime'] = row['updateTime'].strftime('%Y-%m-%d %H:%M:%S')

                    return page_response(rows, total, page_num, page_size)
        except Exception as e:
            print(f"获取前台考试记录列表失败: {str(e)}")
            return error(f"获取前台考试记录列表失败: {str(e)}")

