"""
知识库管理 控制层
"""
import json
from flask import request, session
from service.knowledge_service import KnowledgeService
from utils.response import success, error


class KnowledgeController:
    """知识库控制器类"""

    @staticmethod
    def admin_list():
        """后台获取知识库列表（分页 + 条件）"""
        try:
            page_num = int(request.args.get('pageNum', 1))
            page_size = int(request.args.get('pageSize', 10))
            status = request.args.get('status', '').strip() or None
            keyword = request.args.get('keyword', '').strip() or None
            subject = request.args.get('subject', '').strip() or None
            grade = request.args.get('grade', '').strip() or None

            if page_num < 1:
                page_num = 1
            if page_size < 1 or page_size > 100:
                page_size = 10

            return KnowledgeService.get_knowledge_list(page_num, page_size, status, keyword, subject, grade)
        except Exception as e:
            print(f"获取知识库列表失败: {str(e)}")
            return error(f"获取知识库列表失败: {str(e)}")

    @staticmethod
    def admin_detail():
        """后台获取知识库详情"""
        try:
            knowledge_id = request.args.get('id')
            if not knowledge_id:
                return error("缺少知识库ID参数")
            try:
                knowledge_id = int(knowledge_id)
            except ValueError:
                return error("知识库ID格式错误")

            return KnowledgeService.get_knowledge_by_id(knowledge_id)
        except Exception as e:
            print(f"获取知识库详情失败: {str(e)}")
            return error(f"获取知识库详情失败: {str(e)}")

    # 前台接口
    @staticmethod
    def front_list():
        """前台获取知识库列表"""
        try:
            page_num = int(request.args.get('page', 1))
            page_size = int(request.args.get('limit', 10))
            keyword = request.args.get('keyword', '').strip() or None
            subject = request.args.get('subject', '').strip() or None
            grade = request.args.get('grade', '').strip() or None

            if page_num < 1:
                page_num = 1
            if page_size < 1 or page_size > 100:
                page_size = 10

            return KnowledgeService.get_front_knowledge_list(page_num, page_size, keyword, subject, grade)
        except Exception as e:
            print(f"获取前台知识库列表失败: {str(e)}")
            return error(f"获取前台知识库列表失败: {str(e)}")

    @staticmethod
    def front_detail():
        """前台获取知识库详情"""
        try:
            knowledge_id = request.args.get('id')
            if not knowledge_id:
                return error("缺少知识库ID参数")
            try:
                knowledge_id = int(knowledge_id)
            except ValueError:
                return error("知识库ID格式错误")

            return KnowledgeService.get_front_knowledge_detail(knowledge_id)
        except Exception as e:
            print(f"获取前台知识库详情失败: {str(e)}")
            return error(f"获取前台知识库详情失败: {str(e)}")

    @staticmethod
    def admin_create():
        """后台创建知识库"""
        try:
            if 'user_id' not in session:
                return error("请先登录")

            data = request.get_json() or {}
            title = (data.get('title') or '').strip()

            if not title:
                return error("标题不能为空")

            subject = (data.get('subject') or '').strip()
            if not subject:
                return error("学科不能为空")

            grade = (data.get('grade') or '').strip()
            if not grade:
                return error("年级不能为空")

            # 处理知识点（可能是数组或字符串）
            knowledge_point = data.get('knowledgePoint')
            if isinstance(knowledge_point, str):
                try:
                    knowledge_point = json.loads(knowledge_point)
                except:
                    # 如果不是JSON，尝试按逗号分割
                    knowledge_point = [k.strip() for k in knowledge_point.split(',') if k.strip()]
            elif not isinstance(knowledge_point, list):
                knowledge_point = []

            # 处理附件URL（可能是数组或字符串）
            attachment_url = data.get('attachmentUrl')
            if isinstance(attachment_url, str):
                try:
                    attachment_url = json.loads(attachment_url)
                except:
                    attachment_url = [attachment_url] if attachment_url else []
            elif not isinstance(attachment_url, list):
                attachment_url = []

            return KnowledgeService.create_knowledge(
                title=title,
                summary=(data.get('summary') or '').strip() or None,
                knowledge_point=knowledge_point if knowledge_point else None,
                subject=subject,
                grade=grade,
                attachment_url=attachment_url if attachment_url else None,
                content=(data.get('content') or '').strip() or None,
                author=session.get('username', '未知用户'),
                author_id=session['user_id'],
                status=(data.get('status') or 'enabled').strip() or 'enabled'
            )
        except Exception as e:
            print(f"创建知识库失败: {str(e)}")
            return error(f"创建知识库失败: {str(e)}")

    @staticmethod
    def admin_update():
        """后台更新知识库"""
        try:
            if 'user_id' not in session:
                return error("请先登录")

            data = request.get_json() or {}
            knowledge_id = data.get('id')
            if not knowledge_id:
                return error("缺少知识库ID")
            try:
                knowledge_id = int(knowledge_id)
            except ValueError:
                return error("知识库ID格式错误")

            title = (data.get('title') or '').strip()
            if not title:
                return error("标题不能为空")

            subject = (data.get('subject') or '').strip()
            if not subject:
                return error("学科不能为空")

            grade = (data.get('grade') or '').strip()
            if not grade:
                return error("年级不能为空")

            # 处理知识点
            knowledge_point = data.get('knowledgePoint')
            if isinstance(knowledge_point, str):
                try:
                    knowledge_point = json.loads(knowledge_point)
                except:
                    knowledge_point = [k.strip() for k in knowledge_point.split(',') if k.strip()]
            elif not isinstance(knowledge_point, list):
                knowledge_point = []

            # 处理附件URL
            attachment_url = data.get('attachmentUrl')
            if isinstance(attachment_url, str):
                try:
                    attachment_url = json.loads(attachment_url)
                except:
                    attachment_url = [attachment_url] if attachment_url else []
            elif not isinstance(attachment_url, list):
                attachment_url = []

            return KnowledgeService.update_knowledge(
                knowledge_id=knowledge_id,
                title=title,
                summary=(data.get('summary') or '').strip() or None,
                knowledge_point=knowledge_point if knowledge_point else None,
                subject=subject,
                grade=grade,
                attachment_url=attachment_url if attachment_url else None,
                content=(data.get('content') or '').strip() or None,
                status=(data.get('status') or 'enabled').strip() or 'enabled'
            )
        except Exception as e:
            print(f"更新知识库失败: {str(e)}")
            return error(f"更新知识库失败: {str(e)}")

    @staticmethod
    def admin_delete():
        """后台删除知识库"""
        try:
            if 'user_id' not in session:
                return error("请先登录")

            knowledge_id = request.args.get('id')
            if not knowledge_id:
                return error("缺少知识库ID参数")
            try:
                knowledge_id = int(knowledge_id)
            except ValueError:
                return error("知识库ID格式错误")

            return KnowledgeService.delete_knowledge(knowledge_id)
        except Exception as e:
            print(f"删除知识库失败: {str(e)}")
            return error(f"删除知识库失败: {str(e)}")

    @staticmethod
    def admin_toggle_status():
        """后台切换知识库状态"""
        try:
            if 'user_id' not in session:
                return error("请先登录")

            knowledge_id = request.args.get('id')
            if not knowledge_id:
                return error("缺少知识库ID参数")
            try:
                knowledge_id = int(knowledge_id)
            except ValueError:
                return error("知识库ID格式错误")

            return KnowledgeService.toggle_knowledge_status(knowledge_id)
        except Exception as e:
            print(f"切换知识库状态失败: {str(e)}")
            return error(f"切换知识库状态失败: {str(e)}")

    @staticmethod
    def admin_get_relations():
        """获取知识库关联关系"""
        try:
            knowledge_id = request.args.get('id')
            if not knowledge_id:
                return error("缺少知识库ID参数")
            try:
                knowledge_id = int(knowledge_id)
            except ValueError:
                return error("知识库ID格式错误")

            return KnowledgeService.get_knowledge_relations(knowledge_id)
        except Exception as e:
            print(f"获取知识关联关系失败: {str(e)}")
            return error(f"获取知识关联关系失败: {str(e)}")

    @staticmethod
    def admin_create_relation():
        """创建知识关联关系"""
        try:
            if 'user_id' not in session:
                return error("请先登录")

            data = request.get_json() or {}
            source_id = data.get('sourceId')
            target_id = data.get('targetId')
            relation_type = (data.get('relationType') or 'related').strip()
            weight = float(data.get('weight', 1.0))

            if not source_id or not target_id:
                return error("缺少源知识ID或目标知识ID")

            try:
                source_id = int(source_id)
                target_id = int(target_id)
            except ValueError:
                return error("知识ID格式错误")

            return KnowledgeService.create_knowledge_relation(source_id, target_id, relation_type, weight)
        except Exception as e:
            print(f"创建知识关联关系失败: {str(e)}")
            return error(f"创建知识关联关系失败: {str(e)}")

    @staticmethod
    def admin_delete_relation():
        """删除知识关联关系"""
        try:
            if 'user_id' not in session:
                return error("请先登录")

            relation_id = request.args.get('id')
            if not relation_id:
                return error("缺少关联ID参数")
            try:
                relation_id = int(relation_id)
            except ValueError:
                return error("关联ID格式错误")

            return KnowledgeService.delete_knowledge_relation(relation_id)
        except Exception as e:
            print(f"删除知识关联关系失败: {str(e)}")
            return error(f"删除知识关联关系失败: {str(e)}")

