"""
考试记录管理 控制层
"""
from flask import request, session
from service.exam_record_service import ExamRecordService
from utils.auth_utils import get_current_user
from utils.response import success, error


class ExamRecordController:
    """考试记录控制器类"""

    @staticmethod
    def admin_list():
        """后台获取考试记录列表（分页 + 条件）"""
        try:
            page_num = int(request.args.get('pageNum', 1))
            page_size = int(request.args.get('pageSize', 10))
            status = request.args.get('status', '').strip() or None
            review_status = request.args.get('reviewStatus', '').strip() or None
            keyword = request.args.get('keyword', '').strip() or None
            paper_id = request.args.get('paperId', '').strip() or None
            student_id = request.args.get('studentId', '').strip() or None

            if page_num < 1:
                page_num = 1
            if page_size < 1 or page_size > 100:
                page_size = 10

            paper_id_int = None
            if paper_id:
                try:
                    paper_id_int = int(paper_id)
                except ValueError:
                    paper_id_int = None

            student_id_int = None
            if student_id:
                try:
                    student_id_int = int(student_id)
                except ValueError:
                    student_id_int = None

            return ExamRecordService.get_exam_record_list(
                page_num,
                page_size,
                status,
                review_status,
                keyword,
                paper_id_int,
                student_id_int,
                get_current_user()
            )
        except Exception as e:
            print(f"获取考试记录列表失败: {str(e)}")
            return error(f"获取考试记录列表失败: {str(e)}")

    @staticmethod
    def admin_detail():
        """后台获取考试记录详情"""
        try:
            exam_record_id = request.args.get('id')
            if not exam_record_id:
                return error("缺少考试记录ID参数")
            try:
                exam_record_id = int(exam_record_id)
            except ValueError:
                return error("考试记录ID格式错误")

            return ExamRecordService.get_exam_record_by_id(exam_record_id, get_current_user())
        except Exception as e:
            print(f"获取考试记录详情失败: {str(e)}")
            return error(f"获取考试记录详情失败: {str(e)}")

    @staticmethod
    def admin_get_answers():
        """获取考试记录的答题详情"""
        try:
            exam_record_id = request.args.get('examRecordId')
            if not exam_record_id:
                return error("缺少考试记录ID参数")
            try:
                exam_record_id = int(exam_record_id)
            except ValueError:
                return error("考试记录ID格式错误")

            return ExamRecordService.get_answer_records(exam_record_id, get_current_user())
        except Exception as e:
            print(f"获取答题记录失败: {str(e)}")
            return error(f"获取答题记录失败: {str(e)}")

    @staticmethod
    def admin_review_exam():
        """批阅考试记录"""
        try:
            if 'user_id' not in session:
                return error("请先登录")

            data = request.get_json() or {}
            exam_record_id = data.get('examRecordId')
            if not exam_record_id:
                return error("缺少考试记录ID")

            try:
                exam_record_id = int(exam_record_id)
            except ValueError:
                return error("考试记录ID格式错误")

            return ExamRecordService.review_exam_record(
                exam_record_id=exam_record_id,
                reviewer_id=session['user_id'],
                reviewer_name=session.get('username', '未知用户'),
                review_remark=(data.get('reviewRemark') or '').strip() or None,
                current_user=get_current_user()
            )
        except Exception as e:
            print(f"批阅考试记录失败: {str(e)}")
            return error(f"批阅考试记录失败: {str(e)}")

    @staticmethod
    def admin_review_answer():
        """批阅单个答题记录（主观题评分）"""
        try:
            if 'user_id' not in session:
                return error("请先登录")

            data = request.get_json() or {}
            answer_record_id = data.get('answerRecordId')
            if not answer_record_id:
                return error("缺少答题记录ID")

            try:
                answer_record_id = int(answer_record_id)
            except ValueError:
                return error("答题记录ID格式错误")

            teacher_score = (data.get('teacherScore') or '').strip() or None
            teacher_remark = (data.get('teacherRemark') or '').strip() or None
            is_wrong = data.get('isWrong')
            if is_wrong is not None:
                try:
                    is_wrong = int(is_wrong)
                except (ValueError, TypeError):
                    is_wrong = None

            return ExamRecordService.review_answer(
                answer_record_id=answer_record_id,
                teacher_score=teacher_score,
                teacher_remark=teacher_remark,
                is_wrong=is_wrong,
                current_user=get_current_user()
            )
        except Exception as e:
            print(f"批阅答题记录失败: {str(e)}")
            return error(f"批阅答题记录失败: {str(e)}")

    @staticmethod
    def admin_delete():
        """后台删除考试记录"""
        try:
            if 'user_id' not in session:
                return error("请先登录")

            exam_record_id = request.args.get('id')
            if not exam_record_id:
                return error("缺少考试记录ID参数")
            try:
                exam_record_id = int(exam_record_id)
            except ValueError:
                return error("考试记录ID格式错误")

            return ExamRecordService.delete_exam_record(exam_record_id, get_current_user())
        except Exception as e:
            print(f"删除考试记录失败: {str(e)}")
            return error(f"删除考试记录失败: {str(e)}")

    # 前台接口
    @staticmethod
    def front_start_exam():
        """开始考试"""
        try:
            # 优先从session获取用户信息
            if 'user_id' in session:
                student_id = session['user_id']
                student_name = session.get('username', '未知用户')
            else:
                # 尝试从URL参数获取用户信息（前端从localStorage获取）
                student_id = request.args.get('userId')
                student_name = request.args.get('username', '未知用户')
                if not student_id:
                    # 如果没有用户信息，返回错误要求登录
                    return error("请先登录后再开始考试")
                try:
                    student_id = int(student_id)
                except (ValueError, TypeError):
                    return error("用户ID格式错误，请重新登录")

            paper_id = request.args.get('paperId')
            if not paper_id:
                return error("缺少试卷ID参数")
            try:
                paper_id = int(paper_id)
            except ValueError:
                return error("试卷ID格式错误")

            if not student_id:
                return error("无法获取用户信息，请先登录")

            return ExamRecordService.start_exam(paper_id, student_id, student_name)
        except Exception as e:
            print(f"开始考试失败: {str(e)}")
            return error(f"开始考试失败: {str(e)}")

    @staticmethod
    def front_get_questions():
        """获取考试题目"""
        try:
            exam_record_id = request.args.get('examRecordId')
            if not exam_record_id:
                return error("缺少考试记录ID参数")
            try:
                exam_record_id = int(exam_record_id)
            except ValueError:
                return error("考试记录ID格式错误")

            return ExamRecordService.get_exam_questions(exam_record_id)
        except Exception as e:
            print(f"获取考试题目失败: {str(e)}")
            return error(f"获取考试题目失败: {str(e)}")

    @staticmethod
    def front_save_answer():
        """保存答案"""
        try:
            data = request.get_json() or {}
            exam_record_id = data.get('examRecordId')
            question_id = data.get('questionId')
            student_answer = data.get('studentAnswer', '').strip()

            if not exam_record_id:
                return error("缺少考试记录ID")
            if not question_id:
                return error("缺少题目ID")

            try:
                exam_record_id = int(exam_record_id)
                question_id = int(question_id)
            except ValueError:
                return error("ID格式错误")

            return ExamRecordService.save_answer(exam_record_id, question_id, student_answer)
        except Exception as e:
            print(f"保存答案失败: {str(e)}")
            return error(f"保存答案失败: {str(e)}")

    @staticmethod
    def front_submit_exam():
        """提交试卷"""
        try:
            data = request.get_json() or {}
            exam_record_id = data.get('examRecordId')
            if not exam_record_id:
                return error("缺少考试记录ID")
            try:
                exam_record_id = int(exam_record_id)
            except ValueError:
                return error("考试记录ID格式错误")

            return ExamRecordService.submit_exam(exam_record_id)
        except Exception as e:
            print(f"提交试卷失败: {str(e)}")
            return error(f"提交试卷失败: {str(e)}")

    @staticmethod
    def front_detail():
        """前台获取考试记录详情"""
        try:
            exam_record_id = request.args.get('id')
            if not exam_record_id:
                return error("缺少考试记录ID参数")
            try:
                exam_record_id = int(exam_record_id)
            except ValueError:
                return error("考试记录ID格式错误")

            return ExamRecordService.get_exam_record_by_id(exam_record_id)
        except Exception as e:
            print(f"获取考试记录详情失败: {str(e)}")
            return error(f"获取考试记录详情失败: {str(e)}")

    @staticmethod
    def front_list():
        """前台获取当前用户的考试记录列表"""
        try:
            # 获取用户ID
            student_id = request.args.get('studentId')
            if not student_id:
                # 尝试从session获取
                if 'user_id' in session:
                    student_id = session['user_id']
                else:
                    return error("请先登录")

            try:
                student_id = int(student_id)
            except (ValueError, TypeError):
                return error("用户ID格式错误")

            page_num = int(request.args.get('page', 1))
            page_size = int(request.args.get('limit', 10))
            status = request.args.get('status', '').strip() or None
            keyword = request.args.get('keyword', '').strip() or None

            if page_num < 1:
                page_num = 1
            if page_size < 1 or page_size > 100:
                page_size = 10

            return ExamRecordService.get_front_exam_record_list(
                student_id, page_num, page_size, status, keyword
            )
        except Exception as e:
            print(f"获取前台考试记录列表失败: {str(e)}")
            return error(f"获取前台考试记录列表失败: {str(e)}")

    @staticmethod
    def front_get_answers():
        """前台获取考试记录的答题详情"""
        try:
            exam_record_id = request.args.get('examRecordId')
            if not exam_record_id:
                return error("缺少考试记录ID参数")
            try:
                exam_record_id = int(exam_record_id)
            except ValueError:
                return error("考试记录ID格式错误")

            return ExamRecordService.get_answer_records(exam_record_id)
        except Exception as e:
            print(f"获取答题记录失败: {str(e)}")
            return error(f"获取答题记录失败: {str(e)}")

