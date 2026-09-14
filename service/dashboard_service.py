from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple

from utils.db_utils import get_db_connection


class DashboardService:
    """仪表盘服务类"""

    @staticmethod
    def _build_exam_scope(
        current_user: Optional[Dict[str, Any]],
        paper_id: Optional[int] = None,
        subject: Optional[str] = None,
        alias_record: str = "er",
        alias_user: str = "u"
    ) -> Tuple[str, List[Any]]:
        """构建考试统计范围"""
        where_clauses: List[str] = []
        params: List[Any] = []

        if current_user and current_user.get("role") == "doctor":
            class_id = current_user.get("class_id")
            if not class_id:
                user_id = current_user.get("id")
                where_clauses.append(f"""
                    EXISTS (
                        SELECT 1
                        FROM py_paper p
                        WHERE p.id = {alias_record}.paperId
                          AND p.authorId = %s
                    )
                """)
                params.append(user_id)
            else:
                where_clauses.append(f"""
                    EXISTS (
                        SELECT 1
                        FROM py_user su
                        WHERE su.id = {alias_record}.studentId
                          AND (su.class_id = %s OR su.class_id IS NULL)
                    )
                """)
                params.append(class_id)

        if paper_id:
            where_clauses.append(f"{alias_record}.paperId = %s")
            params.append(paper_id)

        if subject:
            where_clauses.append(f"""
                EXISTS (
                    SELECT 1
                    FROM py_paper_question pq
                    LEFT JOIN py_question_bank q ON pq.questionId = q.id
                    WHERE pq.paperId = {alias_record}.paperId AND q.subject = %s
                )
            """)
            params.append(subject)

        where_sql = ""
        if where_clauses:
            where_sql = "WHERE " + " AND ".join(where_clauses)
        return where_sql, params

    @staticmethod
    def get_user_statistics() -> Dict[str, Any]:
        """获取用户统计数据"""
        try:
            with get_db_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("""
                        SELECT COUNT(*) AS total
                        FROM py_user
                        WHERE role IN ('doctor', 'user') AND status = 'active'
                    """)
                    total_users = cursor.fetchone()["total"]

                    cursor.execute("""
                        SELECT COUNT(*) AS teacher_count
                        FROM py_user
                        WHERE role = 'doctor' AND status = 'active'
                    """)
                    teacher_users = cursor.fetchone()["teacher_count"]

                    cursor.execute("""
                        SELECT COUNT(*) AS student_count
                        FROM py_user
                        WHERE role = 'user' AND status = 'active'
                    """)
                    student_users = cursor.fetchone()["student_count"]

                    today = datetime.now().strftime("%Y-%m-%d")
                    cursor.execute("""
                        SELECT COUNT(*) AS today_count
                        FROM py_user
                        WHERE role IN ('doctor', 'user')
                          AND status = 'active'
                          AND DATE(createtime) = %s
                    """, (today,))
                    today_users = cursor.fetchone()["today_count"]

                    return {
                        "total_users": total_users,
                        "teacher_users": teacher_users,
                        "student_users": student_users,
                        "today_users": today_users
                    }
        except Exception as exc:
            print(f"获取用户统计失败: {exc}")
            return {
                "total_users": 0,
                "teacher_users": 0,
                "student_users": 0,
                "today_users": 0
            }

    @staticmethod
    def get_user_trend_data(days: int = 30) -> Dict[str, Any]:
        """获取用户注册趋势数据"""
        try:
            with get_db_connection() as conn:
                with conn.cursor() as cursor:
                    end_date = datetime.now()
                    start_date = end_date - timedelta(days=days - 1)
                    date_list: List[str] = []
                    trend_data: List[int] = []
                    current_date = start_date

                    while current_date <= end_date:
                        date_str = current_date.strftime("%Y-%m-%d")
                        date_list.append(date_str)
                        cursor.execute("""
                            SELECT COUNT(*) AS count
                            FROM py_user
                            WHERE role IN ('doctor', 'user')
                              AND DATE(createtime) = %s
                              AND status = 'active'
                        """, (date_str,))
                        trend_data.append(cursor.fetchone()["count"])
                        current_date += timedelta(days=1)

                    return {"dates": date_list, "data": trend_data}
        except Exception as exc:
            print(f"获取用户趋势失败: {exc}")
            return {"dates": [], "data": []}

    @staticmethod
    def get_role_distribution() -> List[Dict[str, Any]]:
        """获取用户角色分布"""
        try:
            with get_db_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("""
                        SELECT role, COUNT(*) AS count
                        FROM py_user
                        WHERE role IN ('doctor', 'user') AND status = 'active'
                        GROUP BY role
                    """)
                    role_map = {
                        "doctor": "老师用户",
                        "user": "学生用户"
                    }
                    return [{
                        "name": role_map.get(item["role"], item["role"]),
                        "value": item["count"]
                    } for item in cursor.fetchall()]
        except Exception as exc:
            print(f"获取角色分布失败: {exc}")
            return []

    @staticmethod
    def get_dashboard_overview() -> Dict[str, Any]:
        """获取仪表盘总览"""
        try:
            return {
                "user_stats": DashboardService.get_user_statistics(),
                "announcement_stats": 0,
                "user_trend": DashboardService.get_user_trend_data(7),
                "role_distribution": DashboardService.get_role_distribution(),
                "recent_activities": 0
            }
        except Exception as exc:
            print(f"获取仪表盘总览失败: {exc}")
            return {
                "user_stats": {"total_users": 0, "teacher_users": 0, "student_users": 0, "today_users": 0},
                "announcement_stats": {"total_announcements": 0, "today_announcements": 0, "top_announcements": 0},
                "user_trend": {"dates": [], "data": []},
                "role_distribution": [],
                "recent_activities": []
            }

    @staticmethod
    def get_exam_options(current_user: Optional[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """获取考试选项"""
        try:
            with get_db_connection() as conn:
                with conn.cursor() as cursor:
                    where_sql, params = DashboardService._build_exam_scope(current_user)
                    sql = f"""
                        SELECT er.paperId AS paper_id, er.paperName AS paper_name, COUNT(*) AS exam_count
                        FROM py_exam_record er
                        LEFT JOIN py_user u ON er.studentId = u.id
                        {where_sql}
                        GROUP BY er.paperId, er.paperName
                        ORDER BY MAX(er.createTime) DESC, er.paperId DESC
                    """
                    cursor.execute(sql, params)
                    return [{
                        "paperId": item["paper_id"],
                        "paperName": item["paper_name"],
                        "examCount": item["exam_count"]
                    } for item in cursor.fetchall()]
        except Exception as exc:
            print(f"获取考试选项失败: {exc}")
            return []

    @staticmethod
    def get_subject_options() -> List[str]:
        """获取学科选项"""
        try:
            with get_db_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("""
                        SELECT DISTINCT subject
                        FROM py_question_bank
                        WHERE subject IS NOT NULL AND subject != ''
                        ORDER BY subject ASC
                    """)
                    return [item["subject"] for item in cursor.fetchall()]
        except Exception as exc:
            print(f"获取学科选项失败: {exc}")
            return []

    @staticmethod
    def get_exam_statistics(
        current_user: Optional[Dict[str, Any]] = None,
        paper_id: Optional[int] = None,
        subject: Optional[str] = None
    ) -> Dict[str, Any]:
        """获取考试统计数据"""
        try:
            with get_db_connection() as conn:
                with conn.cursor() as cursor:
                    where_sql, params = DashboardService._build_exam_scope(current_user, paper_id, subject)

                    cursor.execute(f"""
                        SELECT COUNT(*) AS total
                        FROM py_exam_record er
                        LEFT JOIN py_user u ON er.studentId = u.id
                        {where_sql}
                    """, params)
                    total_exams = cursor.fetchone()["total"]

                    cursor.execute(f"""
                        SELECT COUNT(*) AS submitted
                        FROM py_exam_record er
                        LEFT JOIN py_user u ON er.studentId = u.id
                        {where_sql} {'AND' if where_sql else 'WHERE'} er.status IN ('submitted', 'graded')
                    """, params)
                    submitted_exams = cursor.fetchone()["submitted"]

                    cursor.execute(f"""
                        SELECT COUNT(*) AS graded
                        FROM py_exam_record er
                        LEFT JOIN py_user u ON er.studentId = u.id
                        {where_sql} {'AND' if where_sql else 'WHERE'} er.status = 'graded'
                    """, params)
                    graded_exams = cursor.fetchone()["graded"]

                    cursor.execute(f"""
                        SELECT COUNT(*) AS in_progress
                        FROM py_exam_record er
                        LEFT JOIN py_user u ON er.studentId = u.id
                        {where_sql} {'AND' if where_sql else 'WHERE'} er.status = 'in_progress'
                    """, params)
                    in_progress_exams = cursor.fetchone()["in_progress"]

                    today = datetime.now().strftime("%Y-%m-%d")
                    today_params = list(params) + [today]
                    cursor.execute(f"""
                        SELECT COUNT(*) AS today_count
                        FROM py_exam_record er
                        LEFT JOIN py_user u ON er.studentId = u.id
                        {where_sql} {'AND' if where_sql else 'WHERE'} DATE(er.createTime) = %s
                    """, today_params)
                    today_exams = cursor.fetchone()["today_count"]

                    cursor.execute(f"""
                        SELECT AVG(CAST(COALESCE(NULLIF(er.obtainedScore, ''), '0') AS DECIMAL(10,2))) AS avg_score
                        FROM py_exam_record er
                        LEFT JOIN py_user u ON er.studentId = u.id
                        {where_sql} {'AND' if where_sql else 'WHERE'}
                        er.status IN ('submitted', 'graded')
                        AND er.obtainedScore IS NOT NULL
                        AND er.obtainedScore != ''
                    """, params)
                    avg_score_result = cursor.fetchone()
                    avg_score = float(avg_score_result["avg_score"]) if avg_score_result["avg_score"] else 0

                    return {
                        "total_exams": total_exams,
                        "submitted_exams": submitted_exams,
                        "graded_exams": graded_exams,
                        "in_progress_exams": in_progress_exams,
                        "today_exams": today_exams,
                        "avg_score": round(avg_score, 2)
                    }
        except Exception as exc:
            print(f"获取考试统计失败: {exc}")
            return {
                "total_exams": 0,
                "submitted_exams": 0,
                "graded_exams": 0,
                "in_progress_exams": 0,
                "today_exams": 0,
                "avg_score": 0
            }

    @staticmethod
    def get_exam_trend_data(
        days: int = 30,
        current_user: Optional[Dict[str, Any]] = None,
        paper_id: Optional[int] = None,
        subject: Optional[str] = None
    ) -> Dict[str, Any]:
        """获取考试趋势数据"""
        try:
            with get_db_connection() as conn:
                with conn.cursor() as cursor:
                    end_date = datetime.now()
                    start_date = end_date - timedelta(days=days - 1)
                    date_list: List[str] = []
                    trend_data: List[int] = []
                    current_date = start_date

                    while current_date <= end_date:
                        date_str = current_date.strftime("%Y-%m-%d")
                        date_list.append(date_str)
                        where_sql, params = DashboardService._build_exam_scope(current_user, paper_id, subject)
                        params.append(date_str)
                        cursor.execute(f"""
                            SELECT COUNT(*) AS count
                            FROM py_exam_record er
                            LEFT JOIN py_user u ON er.studentId = u.id
                            {where_sql} {'AND' if where_sql else 'WHERE'} DATE(er.createTime) = %s
                        """, params)
                        trend_data.append(cursor.fetchone()["count"])
                        current_date += timedelta(days=1)

                    return {"dates": date_list, "data": trend_data}
        except Exception as exc:
            print(f"获取考试趋势失败: {exc}")
            return {"dates": [], "data": []}

    @staticmethod
    def get_paper_usage_statistics(
        current_user: Optional[Dict[str, Any]] = None,
        paper_id: Optional[int] = None,
        subject: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """获取试卷使用统计"""
        try:
            with get_db_connection() as conn:
                with conn.cursor() as cursor:
                    where_sql, params = DashboardService._build_exam_scope(current_user, paper_id, subject)
                    cursor.execute(f"""
                        SELECT er.paperId AS paper_id, er.paperName AS paper_name,
                               COUNT(er.id) AS exam_count,
                               AVG(CAST(COALESCE(NULLIF(er.obtainedScore, ''), '0') AS DECIMAL(10,2))) AS avg_score
                        FROM py_exam_record er
                        LEFT JOIN py_user u ON er.studentId = u.id
                        {where_sql}
                        GROUP BY er.paperId, er.paperName
                        ORDER BY exam_count DESC, er.paperId DESC
                        LIMIT 10
                    """, params)
                    return [{
                        "paperName": item["paper_name"],
                        "examCount": item["exam_count"] or 0,
                        "avgScore": round(float(item["avg_score"]) if item["avg_score"] else 0, 2)
                    } for item in cursor.fetchall()]
        except Exception as exc:
            print(f"获取试卷使用统计失败: {exc}")
            return []

    @staticmethod
    def get_exam_status_distribution(
        current_user: Optional[Dict[str, Any]] = None,
        paper_id: Optional[int] = None,
        subject: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """获取考试状态分布"""
        try:
            with get_db_connection() as conn:
                with conn.cursor() as cursor:
                    where_sql, params = DashboardService._build_exam_scope(current_user, paper_id, subject)
                    cursor.execute(f"""
                        SELECT er.status AS status, COUNT(*) AS count
                        FROM py_exam_record er
                        LEFT JOIN py_user u ON er.studentId = u.id
                        {where_sql}
                        GROUP BY er.status
                    """, params)
                    status_map = {
                        "in_progress": "进行中",
                        "submitted": "已提交",
                        "graded": "已批阅"
                    }
                    return [{
                        "name": status_map.get(item["status"], item["status"]),
                        "value": item["count"]
                    } for item in cursor.fetchall()]
        except Exception as exc:
            print(f"获取考试状态分布失败: {exc}")
            return []

    @staticmethod
    def get_score_distribution(
        current_user: Optional[Dict[str, Any]] = None,
        paper_id: Optional[int] = None,
        subject: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """获取分数分布"""
        try:
            with get_db_connection() as conn:
                with conn.cursor() as cursor:
                    where_sql, params = DashboardService._build_exam_scope(current_user, paper_id, subject)
                    cursor.execute(f"""
                        SELECT
                            CASE
                                WHEN CAST(COALESCE(NULLIF(er.obtainedScore, ''), '0') AS DECIMAL(10,2)) >= 90 THEN '优秀(90-100)'
                                WHEN CAST(COALESCE(NULLIF(er.obtainedScore, ''), '0') AS DECIMAL(10,2)) >= 80 THEN '良好(80-89)'
                                WHEN CAST(COALESCE(NULLIF(er.obtainedScore, ''), '0') AS DECIMAL(10,2)) >= 70 THEN '中等(70-79)'
                                WHEN CAST(COALESCE(NULLIF(er.obtainedScore, ''), '0') AS DECIMAL(10,2)) >= 60 THEN '及格(60-69)'
                                ELSE '不及格(<60)'
                            END AS score_range,
                            COUNT(*) AS count
                        FROM py_exam_record er
                        LEFT JOIN py_user u ON er.studentId = u.id
                        {where_sql} {'AND' if where_sql else 'WHERE'}
                        er.status IN ('submitted', 'graded')
                        AND er.obtainedScore IS NOT NULL
                        AND er.obtainedScore != ''
                        GROUP BY score_range
                    """, params)
                    return [{
                        "name": item["score_range"],
                        "value": item["count"]
                    } for item in cursor.fetchall()]
        except Exception as exc:
            print(f"获取分数分布失败: {exc}")
            return []

    @staticmethod
    def get_question_type_statistics(
        current_user: Optional[Dict[str, Any]] = None,
        paper_id: Optional[int] = None,
        subject: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """获取题型统计"""
        try:
            with get_db_connection() as conn:
                with conn.cursor() as cursor:
                    where_sql, params = DashboardService._build_exam_scope(
                        current_user,
                        paper_id,
                        subject,
                        alias_record="er",
                        alias_user="u"
                    )
                    cursor.execute(f"""
                        SELECT q.questionType AS question_type,
                               COUNT(*) AS total_count,
                               SUM(CASE WHEN ar.isCorrect = 1 THEN 1 ELSE 0 END) AS correct_count,
                               AVG(CAST(COALESCE(NULLIF(ar.obtainedScore, ''), '0') AS DECIMAL(10,2))) AS avg_score
                        FROM py_answer_record ar
                        LEFT JOIN py_exam_record er ON ar.examRecordId = er.id
                        LEFT JOIN py_user u ON er.studentId = u.id
                        LEFT JOIN py_question_bank q ON ar.questionId = q.id
                        {where_sql} {'AND' if where_sql else 'WHERE'} ar.isCorrect IS NOT NULL
                        GROUP BY q.questionType
                    """, params)
                    type_map = {
                        "single_choice": "单选题",
                        "multiple_choice": "多选题",
                        "fill_blank": "填空题",
                        "essay": "解答题",
                        "judge": "判断题"
                    }
                    rows = []
                    for item in cursor.fetchall():
                        total = item["total_count"] or 0
                        correct = item["correct_count"] or 0
                        rows.append({
                            "type": type_map.get(item["question_type"], item["question_type"]),
                            "total": total,
                            "correct": correct,
                            "accuracy": round((correct / total * 100) if total > 0 else 0, 2),
                            "avgScore": round(float(item["avg_score"]) if item["avg_score"] else 0, 2)
                        })
                    return rows
        except Exception as exc:
            print(f"获取题型统计失败: {exc}")
            return []

    @staticmethod
    def get_teacher_teaching_statistics(
        current_user: Optional[Dict[str, Any]] = None,
        subject: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """获取教师教学情况对比"""
        try:
            with get_db_connection() as conn:
                with conn.cursor() as cursor:
                    params: List[Any] = []
                    where_clauses: List[str] = []

                    if current_user and current_user.get("role") == "doctor":
                        class_id = current_user.get("class_id")
                        if not class_id:
                            user_id = current_user.get("id")
                            where_clauses.append("tu.id = %s")
                            params.append(user_id)
                        else:
                            where_clauses.append("(tu.class_id = %s OR tu.class_id IS NULL)")
                            params.append(class_id)

                    if subject:
                        where_clauses.append("""
                            EXISTS (
                                SELECT 1
                                FROM py_paper_question pq
                                LEFT JOIN py_question_bank q ON pq.questionId = q.id
                                WHERE pq.paperId = er.paperId AND q.subject = %s
                            )
                        """)
                        params.append(subject)

                    where_sql = ""
                    if where_clauses:
                        where_sql = "WHERE " + " AND ".join(where_clauses)

                    cursor.execute(f"""
                        SELECT COALESCE(p.author, '未署名教师') AS teacher_name,
                               COALESCE(p.authorId, 0) AS teacher_id,
                               COUNT(er.id) AS exam_count,
                               COUNT(DISTINCT er.studentId) AS student_count,
                               AVG(CAST(COALESCE(NULLIF(er.obtainedScore, ''), '0') AS DECIMAL(10,2))) AS avg_score
                        FROM py_exam_record er
                        LEFT JOIN py_paper p ON er.paperId = p.id
                        LEFT JOIN py_user tu ON p.authorId = tu.id
                        {where_sql}
                        GROUP BY p.authorId, p.author
                        ORDER BY avg_score DESC, exam_count DESC
                        LIMIT 10
                    """, params)
                    return [{
                        "teacherName": item["teacher_name"],
                        "teacherId": item["teacher_id"],
                        "examCount": item["exam_count"] or 0,
                        "studentCount": item["student_count"] or 0,
                        "avgScore": round(float(item["avg_score"]) if item["avg_score"] else 0, 2)
                    } for item in cursor.fetchall()]
        except Exception as exc:
            print(f"获取教师教学情况失败: {exc}")
            return []

    @staticmethod
    def get_recent_activities(limit: int = 10) -> List[Dict[str, Any]]:
        """获取最近活动"""
        try:
            return []
        except Exception as exc:
            print(f"获取最近活动失败: {exc}")
            return []
