"""
试卷管理 控制层
"""
from flask import request, session
from service.paper_service import PaperService
from utils.auth_utils import get_current_user
from utils.response import success, error


class PaperController:
    """试卷控制器类"""

    @staticmethod
    def admin_list():
        """后台获取试卷列表（分页 + 条件）"""
        try:
            page_num = int(request.args.get('pageNum', 1))
            page_size = int(request.args.get('pageSize', 10))
            status = request.args.get('status', '').strip() or None
            keyword = request.args.get('keyword', '').strip() or None

            if page_num < 1:
                page_num = 1
            if page_size < 1 or page_size > 100:
                page_size = 10

            return PaperService.get_paper_list(
                page_num,
                page_size,
                status,
                keyword,
                get_current_user()
            )
        except Exception as e:
            print(f"获取试卷列表失败: {str(e)}")
            return error(f"获取试卷列表失败: {str(e)}")

    @staticmethod
    def admin_detail():
        """后台获取试卷详情"""
        try:
            paper_id = request.args.get('id')
            if not paper_id:
                return error("缺少试卷ID参数")
            try:
                paper_id = int(paper_id)
            except ValueError:
                return error("试卷ID格式错误")

            return PaperService.get_paper_by_id(paper_id, get_current_user())
        except Exception as e:
            print(f"获取试卷详情失败: {str(e)}")
            return error(f"获取试卷详情失败: {str(e)}")

    @staticmethod
    def admin_create():
        """后台创建试卷"""
        try:
            if 'user_id' not in session:
                return error("请先登录")

            data = request.get_json() or {}
            paper_name = (data.get('paperName') or '').strip()

            if not paper_name:
                return error("试卷名称不能为空")

            duration = int(data.get('duration', 60))
            if duration < 1:
                duration = 60

            # 处理时间字段，空字符串转为None
            start_time = (data.get('startTime') or '').strip()
            start_time = start_time if start_time else None
            
            end_time = (data.get('endTime') or '').strip()
            end_time = end_time if end_time else None

            return PaperService.create_paper(
                paper_name=paper_name,
                duration=duration,
                start_time=start_time,
                end_time=end_time,
                description=(data.get('description') or '').strip() or None,
                image_url=(data.get('imageUrl') or '').strip() or None,
                author=session.get('username', '未知用户'),
                author_id=session['user_id'],
                status=(data.get('status') or 'enabled').strip() or 'enabled',
                current_user=get_current_user()
            )
        except Exception as e:
            print(f"创建试卷失败: {str(e)}")
            return error(f"创建试卷失败: {str(e)}")

    @staticmethod
    def admin_update():
        """后台更新试卷"""
        try:
            if 'user_id' not in session:
                return error("请先登录")

            data = request.get_json() or {}
            paper_id = data.get('id')
            if not paper_id:
                return error("缺少试卷ID")
            try:
                paper_id = int(paper_id)
            except ValueError:
                return error("试卷ID格式错误")

            paper_name = (data.get('paperName') or '').strip()
            if not paper_name:
                return error("试卷名称不能为空")

            duration = int(data.get('duration', 60))
            if duration < 1:
                duration = 60

            # 处理时间字段，空字符串转为None
            start_time = (data.get('startTime') or '').strip()
            start_time = start_time if start_time else None
            
            end_time = (data.get('endTime') or '').strip()
            end_time = end_time if end_time else None

            return PaperService.update_paper(
                paper_id=paper_id,
                paper_name=paper_name,
                duration=duration,
                start_time=start_time,
                end_time=end_time,
                description=(data.get('description') or '').strip() or None,
                image_url=(data.get('imageUrl') or '').strip() or None,
                status=(data.get('status') or 'enabled').strip() or 'enabled'
            )
        except Exception as e:
            print(f"更新试卷失败: {str(e)}")
            return error(f"更新试卷失败: {str(e)}")

    @staticmethod
    def admin_delete():
        """后台删除试卷"""
        try:
            if 'user_id' not in session:
                return error("请先登录")

            paper_id = request.args.get('id')
            if not paper_id:
                return error("缺少试卷ID参数")
            try:
                paper_id = int(paper_id)
            except ValueError:
                return error("试卷ID格式错误")

            return PaperService.delete_paper(paper_id, get_current_user())
        except Exception as e:
            print(f"删除试卷失败: {str(e)}")
            return error(f"删除试卷失败: {str(e)}")

    @staticmethod
    def admin_toggle_status():
        """后台切换试卷状态"""
        try:
            if 'user_id' not in session:
                return error("请先登录")

            paper_id = request.args.get('id')
            if not paper_id:
                return error("缺少试卷ID参数")
            try:
                paper_id = int(paper_id)
            except ValueError:
                return error("试卷ID格式错误")

            return PaperService.toggle_paper_status(paper_id, get_current_user())
        except Exception as e:
            print(f"切换试卷状态失败: {str(e)}")
            return error(f"切换试卷状态失败: {str(e)}")

    @staticmethod
    def admin_get_questions():
        """获取试卷中的题目列表"""
        try:
            paper_id = request.args.get('paperId')
            if not paper_id:
                return error("缺少试卷ID参数")
            try:
                paper_id = int(paper_id)
            except ValueError:
                return error("试卷ID格式错误")

            return PaperService.get_paper_questions(paper_id, get_current_user())
        except Exception as e:
            print(f"获取试卷题目列表失败: {str(e)}")
            return error(f"获取试卷题目列表失败: {str(e)}")

    @staticmethod
    def admin_add_question():
        """手动添加题目到试卷"""
        try:
            if 'user_id' not in session:
                return error("请先登录")

            data = request.get_json() or {}
            paper_id = data.get('paperId')
            question_id = data.get('questionId')

            if not paper_id or not question_id:
                return error("缺少试卷ID或题目ID")

            try:
                paper_id = int(paper_id)
                question_id = int(question_id)
            except ValueError:
                return error("ID格式错误")

            order_num = data.get('orderNum')
            if order_num is not None:
                try:
                    order_num = int(order_num)
                except ValueError:
                    order_num = None

            score = (data.get('score') or '').strip() or None

            return PaperService.add_question_to_paper(
                paper_id,
                question_id,
                order_num,
                score,
                get_current_user()
            )
        except Exception as e:
            print(f"添加题目到试卷失败: {str(e)}")
            return error(f"添加题目到试卷失败: {str(e)}")

    @staticmethod
    def admin_remove_question():
        """从试卷中删除题目"""
        try:
            if 'user_id' not in session:
                return error("请先登录")

            data = request.get_json() or {}
            paper_id = data.get('paperId')
            paper_question_id = data.get('paperQuestionId')

            if not paper_id or not paper_question_id:
                return error("缺少试卷ID或关系ID")

            try:
                paper_id = int(paper_id)
                paper_question_id = int(paper_question_id)
            except ValueError:
                return error("ID格式错误")

            return PaperService.remove_question_from_paper(
                paper_id,
                paper_question_id,
                get_current_user()
            )
        except Exception as e:
            print(f"从试卷中删除题目失败: {str(e)}")
            return error(f"从试卷中删除题目失败: {str(e)}")

    @staticmethod
    def admin_auto_generate():
        """自动组卷"""
        try:
            if 'user_id' not in session:
                return error("请先登录")

            data = request.get_json() or {}
            paper_id = data.get('paperId')
            if not paper_id:
                return error("缺少试卷ID")

            try:
                paper_id = int(paper_id)
            except ValueError:
                return error("试卷ID格式错误")

            subject = (data.get('subject') or '').strip() or None
            grade = (data.get('grade') or '').strip() or None
            question_config = data.get('questionConfig') or {}

            # 验证题型配置
            valid_types = ['single_choice', 'multiple_choice', 'fill_blank', 'essay', 'judge']
            filtered_config = {}
            for q_type, count in question_config.items():
                if q_type in valid_types:
                    try:
                        count = int(count)
                        if count > 0:
                            filtered_config[q_type] = count
                    except (ValueError, TypeError):
                        continue

            if not filtered_config:
                return error("请至少配置一种题型的数量")

            return PaperService.auto_generate_paper(
                paper_id,
                subject,
                grade,
                filtered_config,
                get_current_user()
            )
        except Exception as e:
            print(f"自动组卷失败: {str(e)}")
            return error(f"自动组卷失败: {str(e)}")

    @staticmethod
    def front_list():
        """前台获取试卷列表"""
        try:
            page = int(request.args.get('page', 1))
            limit = int(request.args.get('limit', 10))
            keyword = request.args.get('keyword', '').strip()

            if page < 1:
                page = 1
            if limit < 1 or limit > 100:
                limit = 10

            return PaperService.get_front_paper_list(
                page,
                limit,
                keyword,
                get_current_user()
            )
        except Exception as e:
            print(f"获取前台试卷列表失败: {str(e)}")
            return error(f"获取前台试卷列表失败: {str(e)}")

    @staticmethod
    def front_detail():
        """前台获取试卷详情"""
        try:
            paper_id = request.args.get('id')
            if not paper_id:
                return error("缺少试卷ID参数")
            try:
                paper_id = int(paper_id)
            except ValueError:
                return error("试卷ID格式错误")

            return PaperService.get_front_paper_detail(paper_id, get_current_user())
        except Exception as e:
            print(f"获取前台试卷详情失败: {str(e)}")
            return error(f"获取前台试卷详情失败: {str(e)}")

