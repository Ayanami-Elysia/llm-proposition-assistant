"""
题库管理 服务层
"""
import pymysql
from datetime import datetime
from typing import Optional

from utils.db_utils import get_db_connection
from utils.response import success, error, page_response
from utils.wenxin_utils import WenxinAIService


class QuestionService:
    """题库服务类"""

    @staticmethod
    def get_question_list(
        page_num: int = 1,
        page_size: int = 10,
        status: Optional[str] = None,
        keyword: Optional[str] = None,
        question_type: Optional[str] = None,
        subject: Optional[str] = None,
        grade: Optional[str] = None,
        category: Optional[str] = None,
        knowledge_id: Optional[int] = None
    ):
        """
        获取题目列表（分页 + 条件）
        Args:
            page_num: 页码
            page_size: 每页数量
            status: 状态筛选（enabled/disabled）
            keyword: 关键字（匹配题目内容）
            question_type: 题型筛选
            subject: 学科筛选
            grade: 年级筛选
            category: 题型分类筛选
            knowledge_id: 知识库ID筛选
        """
        try:
            with get_db_connection() as conn:
                with conn.cursor() as cursor:
                    where_conditions = []
                    params = []

                    if status:
                        where_conditions.append("status = %s")
                        params.append(status)

                    if question_type:
                        where_conditions.append("questionType = %s")
                        params.append(question_type)

                    if subject:
                        where_conditions.append("subject = %s")
                        params.append(subject)

                    if grade:
                        where_conditions.append("grade = %s")
                        params.append(grade)

                    if category:
                        where_conditions.append("category = %s")
                        params.append(category)

                    if knowledge_id:
                        where_conditions.append("knowledgeId = %s")
                        params.append(knowledge_id)

                    if keyword:
                        where_conditions.append("content LIKE %s")
                        params.append(f"%{keyword}%")

                    where_clause = f"WHERE {' AND '.join(where_conditions)}" if where_conditions else ""

                    # total
                    count_sql = f"SELECT COUNT(*) AS total FROM py_question_bank {where_clause}"
                    print(f"执行SQL: {count_sql}, 参数: {params}")
                    cursor.execute(count_sql, params)
                    total = cursor.fetchone()["total"]

                    # rows
                    offset = (page_num - 1) * page_size
                    data_sql = f"""
                        SELECT id, content, questionType, optionA, optionB, optionC, optionD,
                               score, imageUrl, correctAnswer, analysis, subject, grade,
                               knowledgeId, category, status, author, authorId, createTime, updateTime
                        FROM py_question_bank
                        {where_clause}
                        ORDER BY id ASC
                        LIMIT %s OFFSET %s
                    """
                    query_params = list(params) + [page_size, offset]
                    print(f"执行SQL: {data_sql}, 参数: {query_params}")
                    cursor.execute(data_sql, query_params)
                    rows = cursor.fetchall()

                    return page_response(rows, total, page_num, page_size)
        except Exception as e:
            print(f"获取题目列表失败: {str(e)}")
            return error(f"获取题目列表失败: {str(e)}")

    @staticmethod
    def get_question_by_id(question_id: int):
        """根据ID获取题目详情"""
        try:
            with get_db_connection() as conn:
                with conn.cursor() as cursor:
                    sql = """
                        SELECT id, content, questionType, optionA, optionB, optionC, optionD,
                               score, imageUrl, correctAnswer, analysis, subject, grade,
                               knowledgeId, category, status, author, authorId, createTime, updateTime
                        FROM py_question_bank
                        WHERE id = %s
                    """
                    print(f"执行SQL: {sql}, 参数: [{question_id}]")
                    cursor.execute(sql, [question_id])
                    row = cursor.fetchone()
                    if not row:
                        return error("题目不存在")
                    return success(row)
        except Exception as e:
            print(f"获取题目详情失败: {str(e)}")
            return error(f"获取题目详情失败: {str(e)}")

    @staticmethod
    def create_question(
        content: str,
        question_type: str,
        option_a: Optional[str],
        option_b: Optional[str],
        option_c: Optional[str],
        option_d: Optional[str],
        correct_answer: str,
        score: str = "10",
        image_url: Optional[str] = None,
        analysis: Optional[str] = None,
        subject: Optional[str] = None,
        grade: Optional[str] = None,
        knowledge_id: Optional[int] = None,
        category: Optional[str] = None,
        author: Optional[str] = None,
        author_id: Optional[int] = None,
        status: str = "enabled"
    ):
        """创建题目"""
        try:
            # 验证题型和选项的匹配
            if question_type == "judge":
                # 判断题只需要A、B选项
                if not option_a or not option_b:
                    return error("判断题必须提供选项A和选项B")
                option_c = None
                option_d = None
            elif question_type in ["single_choice", "multiple_choice"]:
                # 选择题需要至少A、B选项
                if not option_a or not option_b:
                    return error("选择题必须提供选项A和选项B")
            elif question_type in ["fill_blank", "essay"]:
                # 填空题和解答题不需要选项
                option_a = None
                option_b = None
                option_c = None
                option_d = None

            with get_db_connection() as conn:
                with conn.cursor() as cursor:
                    sql = """
                        INSERT INTO py_question_bank
                        (content, questionType, optionA, optionB, optionC, optionD, score, imageUrl,
                         correctAnswer, analysis, subject, grade, knowledgeId, category, status,
                         author, authorId, createTime, updateTime)
                        VALUES
                        (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW(), NOW())
                    """
                    params = [
                        content, question_type, option_a, option_b, option_c, option_d, score, image_url,
                        correct_answer, analysis, subject, grade, knowledge_id, category, status,
                        author, author_id
                    ]
                    print(f"执行SQL: {sql}, 参数: {params}")
                    cursor.execute(sql, params)
                    conn.commit()
                    new_id = cursor.lastrowid
                    return success({"id": new_id}, "题目创建成功")
        except Exception as e:
            print(f"创建题目失败: {str(e)}")
            return error(f"创建题目失败: {str(e)}")

    @staticmethod
    def update_question(
        question_id: int,
        content: str,
        question_type: str,
        option_a: Optional[str],
        option_b: Optional[str],
        option_c: Optional[str],
        option_d: Optional[str],
        correct_answer: str,
        score: str,
        image_url: Optional[str],
        analysis: Optional[str],
        subject: Optional[str],
        grade: Optional[str],
        knowledge_id: Optional[int],
        category: Optional[str],
        status: str
    ):
        """更新题目"""
        try:
            # 验证题型和选项的匹配
            if question_type == "judge":
                if not option_a or not option_b:
                    return error("判断题必须提供选项A和选项B")
                option_c = None
                option_d = None
            elif question_type in ["single_choice", "multiple_choice"]:
                if not option_a or not option_b:
                    return error("选择题必须提供选项A和选项B")
            elif question_type in ["fill_blank", "essay"]:
                option_a = None
                option_b = None
                option_c = None
                option_d = None

            with get_db_connection() as conn:
                with conn.cursor() as cursor:
                    # 存在性校验
                    check_sql = "SELECT id FROM py_question_bank WHERE id = %s"
                    print(f"执行SQL: {check_sql}, 参数: [{question_id}]")
                    cursor.execute(check_sql, [question_id])
                    if not cursor.fetchone():
                        return error("题目不存在")

                    sql = """
                        UPDATE py_question_bank
                        SET content=%s, questionType=%s, optionA=%s, optionB=%s, optionC=%s, optionD=%s,
                            score=%s, imageUrl=%s, correctAnswer=%s, analysis=%s, subject=%s, grade=%s,
                            knowledgeId=%s, category=%s, status=%s, updateTime=NOW()
                        WHERE id=%s
                    """
                    params = [
                        content, question_type, option_a, option_b, option_c, option_d, score, image_url,
                        correct_answer, analysis, subject, grade, knowledge_id, category, status, question_id
                    ]
                    print(f"执行SQL: {sql}, 参数: {params}")
                    cursor.execute(sql, params)
                    conn.commit()
                    return success(None, "题目更新成功")
        except Exception as e:
            print(f"更新题目失败: {str(e)}")
            return error(f"更新题目失败: {str(e)}")

    @staticmethod
    def delete_question(question_id: int):
        """删除题目"""
        try:
            with get_db_connection() as conn:
                with conn.cursor() as cursor:
                    check_sql = "SELECT id FROM py_question_bank WHERE id = %s"
                    print(f"执行SQL: {check_sql}, 参数: [{question_id}]")
                    cursor.execute(check_sql, [question_id])
                    if not cursor.fetchone():
                        return error("题目不存在")

                    sql = "DELETE FROM py_question_bank WHERE id = %s"
                    print(f"执行SQL: {sql}, 参数: [{question_id}]")
                    cursor.execute(sql, [question_id])
                    conn.commit()
                    return success(None, "题目删除成功")
        except Exception as e:
            print(f"删除题目失败: {str(e)}")
            return error(f"删除题目失败: {str(e)}")

    @staticmethod
    def toggle_question_status(question_id: int):
        """切换题目状态 enabled/disabled"""
        try:
            with get_db_connection() as conn:
                with conn.cursor() as cursor:
                    get_sql = "SELECT status FROM py_question_bank WHERE id = %s"
                    print(f"执行SQL: {get_sql}, 参数: [{question_id}]")
                    cursor.execute(get_sql, [question_id])
                    row = cursor.fetchone()
                    if not row:
                        return error("题目不存在")

                    current = row["status"] or "enabled"
                    new_status = "disabled" if current == "enabled" else "enabled"

                    upd_sql = "UPDATE py_question_bank SET status=%s, updateTime=NOW() WHERE id=%s"
                    print(f"执行SQL: {upd_sql}, 参数: [{new_status}, {question_id}]")
                    cursor.execute(upd_sql, [new_status, question_id])
                    conn.commit()
                    return success(None, f"状态已更新为 {new_status}")
        except Exception as e:
            print(f"切换题目状态失败: {str(e)}")
            return error(f"切换题目状态失败: {str(e)}")
    
    @staticmethod
    def ai_generate_questions(
        subject: str,
        grade: str,
        knowledge_points: str,
        question_type: str,
        count: int = 1,
        author: Optional[str] = None,
        author_id: Optional[int] = None
    ):
        """
        AI智能生成题目（AI自动评估难度）
        
        Args:
            subject: 学科
            grade: 年级
            knowledge_points: 知识点范围
            question_type: 题型
            count: 生成数量
            author: 创建人
            author_id: 创建人ID
            
        Returns:
            dict: 生成的题目列表
        """
        try:
            # 调用文心一言生成题目（不传入difficulty参数，让AI自动评估）
            questions = WenxinAIService.generate_question(
                subject=subject,
                grade=grade,
                knowledge_points=knowledge_points,
                question_type=question_type,
                count=count
            )
            
            # 为每个题目添加额外信息
            for q in questions:
                q['subject'] = subject
                q['grade'] = grade
                q['questionType'] = question_type
                q['knowledgePoints'] = knowledge_points
                q['author'] = author
                q['authorId'] = author_id
            
            return success(questions, f"成功生成{len(questions)}道题目")
            
        except Exception as e:
            print(f"AI生成题目失败: {str(e)}")
            return error(f"AI生成题目失败: {str(e)}")
    
    @staticmethod
    def ai_evaluate_difficulty(question_id: int):
        """
        AI评估题目难度
        
        Args:
            question_id: 题目ID
            
        Returns:
            dict: 难度评估结果
        """
        try:
            # 获取题目信息
            with get_db_connection() as conn:
                with conn.cursor() as cursor:
                    sql = """
                        SELECT content, questionType, optionA, optionB, optionC, optionD,
                               subject, grade
                        FROM py_question_bank
                        WHERE id = %s
                    """
                    print(f"执行SQL: {sql}, 参数: [{question_id}]")
                    cursor.execute(sql, [question_id])
                    question = cursor.fetchone()
                    
                    if not question:
                        return error("题目不存在")
                    
                    # 构建选项字典
                    options = {}
                    if question.get('optionA'):
                        options['A'] = question['optionA']
                    if question.get('optionB'):
                        options['B'] = question['optionB']
                    if question.get('optionC'):
                        options['C'] = question['optionC']
                    if question.get('optionD'):
                        options['D'] = question['optionD']
                    
                    # 调用AI评估难度
                    result = WenxinAIService.evaluate_difficulty(
                        content=question['content'],
                        question_type=question['questionType'],
                        subject=question.get('subject', '数学'),
                        grade=question.get('grade', '一年级'),
                        options=options if options else None
                    )
                    
                    return success(result, "难度评估完成")
                    
        except Exception as e:
            print(f"AI评估难度失败: {str(e)}")
            return error(f"AI评估难度失败: {str(e)}")
    
    @staticmethod
    def ai_analyze_knowledge(question_id: int):
        """
        AI分析题目知识点
        
        Args:
            question_id: 题目ID
            
        Returns:
            dict: 知识点分析结果
        """
        try:
            # 获取题目信息
            with get_db_connection() as conn:
                with conn.cursor() as cursor:
                    sql = """
                        SELECT content, questionType, optionA, optionB, optionC, optionD,
                               subject, grade
                        FROM py_question_bank
                        WHERE id = %s
                    """
                    print(f"执行SQL: {sql}, 参数: [{question_id}]")
                    cursor.execute(sql, [question_id])
                    question = cursor.fetchone()
                    
                    if not question:
                        return error("题目不存在")
                    
                    # 构建选项字典
                    options = {}
                    if question.get('optionA'):
                        options['A'] = question['optionA']
                    if question.get('optionB'):
                        options['B'] = question['optionB']
                    if question.get('optionC'):
                        options['C'] = question['optionC']
                    if question.get('optionD'):
                        options['D'] = question['optionD']
                    
                    # 调用AI分析知识点
                    result = WenxinAIService.analyze_knowledge_points(
                        content=question['content'],
                        question_type=question['questionType'],
                        subject=question.get('subject', '数学'),
                        grade=question.get('grade', '一年级'),
                        options=options if options else None
                    )
                    
                    return success(result, "知识点分析完成")
                    
        except Exception as e:
            print(f"AI分析知识点失败: {str(e)}")
            return error(f"AI分析知识点失败: {str(e)}")
    
    @staticmethod
    def batch_save_ai_questions(questions: list, author: Optional[str] = None, author_id: Optional[int] = None):
        """
        批量保存AI生成的题目（包含AI评估的难度和知识点）
        
        Args:
            questions: 题目列表
            author: 创建人
            author_id: 创建人ID
            
        Returns:
            dict: 保存结果
        """
        try:
            import json
            saved_ids = []
            
            with get_db_connection() as conn:
                with conn.cursor() as cursor:
                    for q in questions:
                        # 处理知识点列表，转为JSON字符串
                        knowledge_points = q.get('knowledgePoints', [])
                        if isinstance(knowledge_points, list):
                            kp_json = json.dumps(knowledge_points, ensure_ascii=False)
                        else:
                            kp_json = None
                        
                        # 获取难度信息
                        difficulty_level = q.get('difficultyLevel', '中等')
                        difficulty_score = q.get('difficultyScore', '0.5')
                        difficulty_analysis = q.get('difficultyAnalysis', '')
                        
                        sql = """
                            INSERT INTO py_question_bank
                            (content, questionType, optionA, optionB, optionC, optionD, score, 
                             correctAnswer, analysis, subject, grade, category, status, author, authorId,
                             difficultyLevel, difficultyScore, aiKnowledgePoints, aiAnalysis,
                             isAIGenerated, createTime, updateTime)
                            VALUES
                            (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 1, NOW(), NOW())
                        """
                        params = [
                            q.get('content', ''),
                            q.get('questionType', ''),
                            q.get('optionA'),
                            q.get('optionB'),
                            q.get('optionC'),
                            q.get('optionD'),
                            q.get('score', '10'),
                            q.get('correctAnswer', ''),
                            q.get('analysis', ''),
                            q.get('subject'),
                            q.get('grade'),
                            q.get('category'),
                            'enabled',
                            author,
                            author_id,
                            difficulty_level,
                            difficulty_score,
                            kp_json,
                            difficulty_analysis
                        ]
                        print(f"执行SQL: {sql}, 参数: {params}")
                        cursor.execute(sql, params)
                        saved_ids.append(cursor.lastrowid)
                    
                    conn.commit()
            
            return success({"ids": saved_ids, "count": len(saved_ids)}, f"成功保存{len(saved_ids)}道题目")
            
        except Exception as e:
            print(f"批量保存题目失败: {str(e)}")
            return error(f"批量保存题目失败: {str(e)}")
    
    @staticmethod
    def save_ai_difficulty_evaluation(question_id: int, difficulty: float, level: str, analysis: str):
        """
        保存AI难度评估结果到数据库
        
        Args:
            question_id: 题目ID
            difficulty: 难度系数
            level: 难度等级
            analysis: 分析说明
            
        Returns:
            dict: 保存结果
        """
        try:
            with get_db_connection() as conn:
                with conn.cursor() as cursor:
                    sql = """
                        UPDATE py_question_bank 
                        SET difficultyScore = %s, difficultyLevel = %s, aiAnalysis = %s, updateTime = NOW()
                        WHERE id = %s
                    """
                    params = [str(difficulty), level, analysis, question_id]
                    print(f"执行SQL: {sql}, 参数: {params}")
                    cursor.execute(sql, params)
                    conn.commit()
                    
                    return success(None, "难度评估结果已保存")
                    
        except Exception as e:
            print(f"保存难度评估结果失败: {str(e)}")
            return error(f"保存难度评估结果失败: {str(e)}")
    
    @staticmethod
    def save_ai_knowledge_analysis(question_id: int, knowledge_points: list, analysis: str):
        """
        保存AI知识点分析结果到数据库
        
        Args:
            question_id: 题目ID
            knowledge_points: 知识点列表
            analysis: 分析说明
            
        Returns:
            dict: 保存结果
        """
        try:
            import json
            
            with get_db_connection() as conn:
                with conn.cursor() as cursor:
                    # 将知识点列表转为JSON字符串
                    kp_json = json.dumps(knowledge_points, ensure_ascii=False)
                    
                    sql = """
                        UPDATE py_question_bank 
                        SET aiKnowledgePoints = %s, aiAnalysis = %s, updateTime = NOW()
                        WHERE id = %s
                    """
                    params = [kp_json, analysis, question_id]
                    print(f"执行SQL: {sql}, 参数: {params}")
                    cursor.execute(sql, params)
                    conn.commit()
                    
                    return success(None, "知识点分析结果已保存")
                    
        except Exception as e:
            print(f"保存知识点分析结果失败: {str(e)}")
            return error(f"保存知识点分析结果失败: {str(e)}")

