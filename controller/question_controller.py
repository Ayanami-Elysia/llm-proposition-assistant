"""
题库管理 控制层
"""
from flask import request, session
from service.question_service import QuestionService
from utils.response import success, error


class QuestionController:
    """题库控制器类"""

    @staticmethod
    def admin_list():
        """后台获取题目列表（分页 + 条件）"""
        try:
            page_num = int(request.args.get('pageNum', 1))
            page_size = int(request.args.get('pageSize', 10))
            status = request.args.get('status', '').strip() or None
            keyword = request.args.get('keyword', '').strip() or None
            question_type = request.args.get('questionType', '').strip() or None
            subject = request.args.get('subject', '').strip() or None
            grade = request.args.get('grade', '').strip() or None
            category = request.args.get('category', '').strip() or None
            knowledge_id = request.args.get('knowledgeId', '').strip() or None

            if page_num < 1:
                page_num = 1
            if page_size < 1 or page_size > 100:
                page_size = 10

            knowledge_id_int = None
            if knowledge_id:
                try:
                    knowledge_id_int = int(knowledge_id)
                except ValueError:
                    knowledge_id_int = None

            return QuestionService.get_question_list(
                page_num, page_size, status, keyword, question_type, 
                subject, grade, category, knowledge_id_int
            )
        except Exception as e:
            print(f"获取题目列表失败: {str(e)}")
            return error(f"获取题目列表失败: {str(e)}")

    @staticmethod
    def admin_detail():
        """后台获取题目详情"""
        try:
            question_id = request.args.get('id')
            if not question_id:
                return error("缺少题目ID参数")
            try:
                question_id = int(question_id)
            except ValueError:
                return error("题目ID格式错误")

            return QuestionService.get_question_by_id(question_id)
        except Exception as e:
            print(f"获取题目详情失败: {str(e)}")
            return error(f"获取题目详情失败: {str(e)}")

    @staticmethod
    def admin_create():
        """后台创建题目"""
        try:
            if 'user_id' not in session:
                return error("请先登录")

            data = request.get_json() or {}
            content = (data.get('content') or '').strip()
            question_type = (data.get('questionType') or '').strip()
            correct_answer = (data.get('correctAnswer') or '').strip()

            if not content:
                return error("题目内容不能为空")
            if not question_type:
                return error("题型不能为空")
            if not correct_answer:
                return error("正确答案不能为空")

            # 验证题型
            valid_types = ['single_choice', 'multiple_choice', 'fill_blank', 'essay', 'judge']
            if question_type not in valid_types:
                return error(f"题型必须是：{', '.join(valid_types)}")

            return QuestionService.create_question(
                content=content,
                question_type=question_type,
                option_a=(data.get('optionA') or '').strip() or None,
                option_b=(data.get('optionB') or '').strip() or None,
                option_c=(data.get('optionC') or '').strip() or None,
                option_d=(data.get('optionD') or '').strip() or None,
                correct_answer=correct_answer,
                score=(data.get('score') or '10').strip() or '10',
                image_url=(data.get('imageUrl') or '').strip() or None,
                analysis=(data.get('analysis') or '').strip() or None,
                subject=(data.get('subject') or '').strip() or None,
                grade=(data.get('grade') or '').strip() or None,
                knowledge_id=int(data.get('knowledgeId')) if data.get('knowledgeId') else None,
                category=(data.get('category') or '').strip() or None,
                author=session.get('username', '未知用户'),
                author_id=session['user_id'],
                status=(data.get('status') or 'enabled').strip() or 'enabled'
            )
        except Exception as e:
            print(f"创建题目失败: {str(e)}")
            return error(f"创建题目失败: {str(e)}")

    @staticmethod
    def admin_update():
        """后台更新题目"""
        try:
            if 'user_id' not in session:
                return error("请先登录")

            data = request.get_json() or {}
            question_id = data.get('id')
            if not question_id:
                return error("缺少题目ID")
            try:
                question_id = int(question_id)
            except ValueError:
                return error("题目ID格式错误")

            content = (data.get('content') or '').strip()
            question_type = (data.get('questionType') or '').strip()
            correct_answer = (data.get('correctAnswer') or '').strip()

            if not content:
                return error("题目内容不能为空")
            if not question_type:
                return error("题型不能为空")
            if not correct_answer:
                return error("正确答案不能为空")

            # 验证题型
            valid_types = ['single_choice', 'multiple_choice', 'fill_blank', 'essay', 'judge']
            if question_type not in valid_types:
                return error(f"题型必须是：{', '.join(valid_types)}")

            return QuestionService.update_question(
                question_id=question_id,
                content=content,
                question_type=question_type,
                option_a=(data.get('optionA') or '').strip() or None,
                option_b=(data.get('optionB') or '').strip() or None,
                option_c=(data.get('optionC') or '').strip() or None,
                option_d=(data.get('optionD') or '').strip() or None,
                correct_answer=correct_answer,
                score=(data.get('score') or '10').strip() or '10',
                image_url=(data.get('imageUrl') or '').strip() or None,
                analysis=(data.get('analysis') or '').strip() or None,
                subject=(data.get('subject') or '').strip() or None,
                grade=(data.get('grade') or '').strip() or None,
                knowledge_id=int(data.get('knowledgeId')) if data.get('knowledgeId') else None,
                category=(data.get('category') or '').strip() or None,
                status=(data.get('status') or 'enabled').strip() or 'enabled'
            )
        except Exception as e:
            print(f"更新题目失败: {str(e)}")
            return error(f"更新题目失败: {str(e)}")

    @staticmethod
    def admin_delete():
        """后台删除题目"""
        try:
            if 'user_id' not in session:
                return error("请先登录")

            question_id = request.args.get('id')
            if not question_id:
                return error("缺少题目ID参数")
            try:
                question_id = int(question_id)
            except ValueError:
                return error("题目ID格式错误")

            return QuestionService.delete_question(question_id)
        except Exception as e:
            print(f"删除题目失败: {str(e)}")
            return error(f"删除题目失败: {str(e)}")

    @staticmethod
    def admin_toggle_status():
        """后台切换题目状态"""
        try:
            if 'user_id' not in session:
                return error("请先登录")

            question_id = request.args.get('id')
            if not question_id:
                return error("缺少题目ID参数")
            try:
                question_id = int(question_id)
            except ValueError:
                return error("题目ID格式错误")

            return QuestionService.toggle_question_status(question_id)
        except Exception as e:
            print(f"切换题目状态失败: {str(e)}")
            return error(f"切换题目状态失败: {str(e)}")
    
    @staticmethod
    def ai_generate():
        """AI智能生成题目（AI自动评估难度）"""
        try:
            if 'user_id' not in session:
                return error("请先登录")
            
            data = request.get_json() or {}
            
            subject = (data.get('subject') or '').strip()
            grade = (data.get('grade') or '').strip()
            knowledge_points = (data.get('knowledgePoints') or '').strip()
            question_type = (data.get('questionType') or '').strip()
            count = int(data.get('count', 1))
            
            # 参数验证
            if not subject:
                return error("请选择学科")
            if not grade:
                return error("请选择年级")
            if not knowledge_points:
                return error("请输入知识点范围")
            if not question_type:
                return error("请选择题型")
            
            if count < 1 or count > 10:
                return error("生成数量必须在1-10之间")
            
            # 验证题型
            valid_types = ['single_choice', 'multiple_choice', 'fill_blank', 'essay', 'judge']
            if question_type not in valid_types:
                return error(f"题型必须是：{', '.join(valid_types)}")
            
            return QuestionService.ai_generate_questions(
                subject=subject,
                grade=grade,
                knowledge_points=knowledge_points,
                question_type=question_type,
                count=count,
                author=session.get('username', '未知用户'),
                author_id=session['user_id']
            )
            
        except Exception as e:
            print(f"AI生成题目失败: {str(e)}")
            return error(f"AI生成题目失败: {str(e)}")
    
    @staticmethod
    def ai_evaluate_difficulty():
        """AI评估题目难度"""
        try:
            if 'user_id' not in session:
                return error("请先登录")
            
            question_id = request.args.get('id')
            if not question_id:
                return error("缺少题目ID参数")
            
            try:
                question_id = int(question_id)
            except ValueError:
                return error("题目ID格式错误")
            
            return QuestionService.ai_evaluate_difficulty(question_id)
            
        except Exception as e:
            print(f"AI评估难度失败: {str(e)}")
            return error(f"AI评估难度失败: {str(e)}")
    
    @staticmethod
    def ai_analyze_knowledge():
        """AI分析题目知识点"""
        try:
            if 'user_id' not in session:
                return error("请先登录")
            
            question_id = request.args.get('id')
            if not question_id:
                return error("缺少题目ID参数")
            
            try:
                question_id = int(question_id)
            except ValueError:
                return error("题目ID格式错误")
            
            return QuestionService.ai_analyze_knowledge(question_id)
            
        except Exception as e:
            print(f"AI分析知识点失败: {str(e)}")
            return error(f"AI分析知识点失败: {str(e)}")
    
    @staticmethod
    def ai_batch_save():
        """批量保存AI生成的题目"""
        try:
            if 'user_id' not in session:
                return error("请先登录")
            
            data = request.get_json() or {}
            questions = data.get('questions', [])
            
            if not questions or not isinstance(questions, list):
                return error("缺少题目数据")
            
            if len(questions) > 20:
                return error("单次最多保存20道题目")
            
            return QuestionService.batch_save_ai_questions(
                questions=questions,
                author=session.get('username', '未知用户'),
                author_id=session['user_id']
            )
            
        except Exception as e:
            print(f"批量保存题目失败: {str(e)}")
            return error(f"批量保存题目失败: {str(e)}")

