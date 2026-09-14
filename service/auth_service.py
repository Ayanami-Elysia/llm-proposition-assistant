from typing import Any, Dict, Optional
import logging
import time

from service.class_service import ClassService
from utils.db_utils import execute_insert, execute_query, execute_update

logger = logging.getLogger(__name__)


class AuthService:
    """认证服务类"""

    def __init__(self) -> None:
        self.class_service = ClassService()

    def _resolve_register_class(self, role: str, class_name: Optional[str]) -> Optional[int]:
        """解析注册班级"""
        if role not in ["user", "doctor"]:
            return None

        class_id, _ = self.class_service.resolve_class_binding(None, class_name)
        if not class_id:
            raise ValueError("学生和教师注册时必须选择班级")
        return class_id

    def login(self, username: str, password: str, role: str) -> Optional[Dict[str, Any]]:
        """用户登录验证"""
        try:
            sql = """
                SELECT u.id, u.username, u.password, u.nickname, u.avatar, u.role,
                       u.status, u.class_id, c.class_name, u.grade, u.last_login_time,
                       u.last_login_ip, u.createtime, u.updatetime
                FROM py_user u
                LEFT JOIN py_class c ON u.class_id = c.id
                WHERE u.username = %s AND u.status = 'active'
            """
            users = execute_query(sql, (username,))
            if not users:
                logger.warning(f"用户 {username} 不存在或已被禁用")
                return None

            user = users[0]
            if user["password"] != password:
                logger.warning(f"用户 {username} 密码错误")
                return None

            if role and user["role"] != role:
                logger.warning(f"用户 {username} 角色不匹配: {role} != {user['role']}")
                return None

            current_time: str = time.strftime("%Y-%m-%d %H:%M:%S")
            update_sql = """
                UPDATE py_user
                SET last_login_time = %s, last_login_ip = %s, updatetime = %s
                WHERE id = %s
            """
            execute_update(update_sql, (current_time, "127.0.0.1", current_time, user["id"]))

            return {
                "id": user["id"],
                "username": user["username"],
                "nickname": user["nickname"],
                "avatar": user["avatar"],
                "role": user["role"],
                "status": user["status"],
                "class_id": user["class_id"],
                "class_name": user["class_name"],
                "grade": user["grade"],
                "last_login_time": user["last_login_time"],
                "createtime": user["createtime"]
            }
        except Exception as exc:
            logger.error(f"用户登录验证异常: {exc}")
            return None

    def register(
        self,
        username: str,
        password: str,
        nickname: Optional[str] = None,
        email: Optional[str] = None,
        phone: Optional[str] = None,
        role: str = "user",
        class_name: Optional[str] = None,
        grade: Optional[str] = None
    ) -> bool:
        """用户注册"""
        try:
            check_sql = "SELECT id FROM py_user WHERE username = %s"
            existing_users = execute_query(check_sql, (username,))
            if existing_users:
                logger.warning(f"用户名 {username} 已存在")
                return False

            allowed_roles = ["user", "doctor"]
            if role not in allowed_roles:
                logger.warning(f"非法注册角色: {role}")
                return False

            if role == "user" and not (grade or "").strip():
                raise ValueError("学生注册时必须选择年级")

            class_id = self._resolve_register_class(role, class_name)
            normalized_grade = (grade or "").strip() or None
            current_time: str = time.strftime("%Y-%m-%d %H:%M:%S")
            insert_sql = """
                INSERT INTO py_user
                (username, password, nickname, email, phone, role, status, class_id, grade, createtime, updatetime)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            execute_insert(
                insert_sql,
                (
                    username,
                    password,
                    nickname,
                    email,
                    phone,
                    role,
                    "active",
                    class_id,
                    normalized_grade,
                    current_time,
                    current_time
                )
            )
            logger.info(f"用户 {username} 注册成功")
            return True
        except ValueError:
            raise
        except Exception as exc:
            logger.error(f"用户注册异常: {exc}")
            return False

    def check_username_exists(self, username: str) -> bool:
        """检查用户名是否存在"""
        try:
            sql = "SELECT id FROM py_user WHERE username = %s"
            users = execute_query(sql, (username,))
            return len(users) > 0
        except Exception as exc:
            logger.error(f"检查用户名存在性异常: {exc}")
            return False

    def get_user_by_username(self, username: str) -> Optional[Dict[str, Any]]:
        """根据用户名获取用户信息"""
        try:
            sql = """
                SELECT u.id, u.username, u.nickname, u.avatar, u.role, u.status,
                       u.class_id, c.class_name, u.grade, u.last_login_time, u.createtime, u.updatetime
                FROM py_user u
                LEFT JOIN py_class c ON u.class_id = c.id
                WHERE u.username = %s
            """
            users = execute_query(sql, (username,))
            if users:
                return dict(users[0])
            return None
        except Exception as exc:
            logger.error(f"根据用户名获取用户信息异常: {exc}")
            return None
