from typing import Any, Dict, List, Optional, Tuple
import logging
import time

from service.class_service import ClassService
from utils.auth_utils import hash_password
from utils.db_utils import execute_delete, execute_insert, execute_query, execute_update
from utils.file_utils import allowed_file, save_file

logger = logging.getLogger(__name__)


class UserService:
    """用户服务类"""

    def __init__(self) -> None:
        self.class_service = ClassService()

    def _get_effective_role(self, user_id: int, data: Dict[str, Any]) -> str:
        """获取用户最终角色"""
        if data.get("role"):
            return str(data["role"])

        sql = "SELECT role FROM py_user WHERE id = %s"
        users = execute_query(sql, (user_id,))
        if not users:
            raise ValueError("用户不存在")
        return str(users[0]["role"])

    def _resolve_class_binding(
        self,
        role: str,
        data: Dict[str, Any]
    ) -> Tuple[Optional[int], Optional[str]]:
        """解析班级绑定信息"""
        if role not in ["user", "doctor"]:
            return None, None

        class_id, class_name = self.class_service.resolve_class_binding(
            data.get("class_id"),
            data.get("class_name")
        )
        if not class_id:
            raise ValueError("学生和教师必须绑定班级信息")
        return class_id, class_name

    def get_user_list(
        self,
        page: int = 1,
        limit: int = 10,
        keyword: str = "",
        role: str = "",
        status: str = ""
    ) -> Tuple[List[Dict[str, Any]], int]:
        """获取用户列表"""
        try:
            where_conditions: List[str] = []
            params: List[Any] = []

            if keyword:
                where_conditions.append(
                    "(u.username LIKE %s OR u.nickname LIKE %s OR u.email LIKE %s OR c.class_name LIKE %s)"
                )
                keyword_param: str = f"%{keyword}%"
                params.extend([keyword_param, keyword_param, keyword_param, keyword_param])

            if role:
                where_conditions.append("u.role = %s")
                params.append(role)

            if status:
                where_conditions.append("u.status = %s")
                params.append(status)

            where_clause: str = ""
            if where_conditions:
                where_clause = "WHERE " + " AND ".join(where_conditions)

            count_sql = f"""
                SELECT COUNT(*) AS total
                FROM py_user u
                LEFT JOIN py_class c ON u.class_id = c.id
                {where_clause}
            """
            count_result = execute_query(count_sql, params)
            total: int = count_result[0]["total"] if count_result else 0

            offset: int = (page - 1) * limit
            list_sql = f"""
                SELECT u.id, u.username, u.nickname, u.avatar, u.sex, u.age, u.phone,
                       u.email, u.birthday, u.card, u.address, u.education,
                       u.profession, u.company, u.content, u.remarks, u.role,
                       u.status, u.class_id, c.class_name, u.last_login_time,
                       u.last_login_ip, u.createtime, u.updatetime
                FROM py_user u
                LEFT JOIN py_class c ON u.class_id = c.id
                {where_clause}
                ORDER BY u.createtime DESC
                LIMIT %s OFFSET %s
            """
            list_params: List[Any] = list(params)
            list_params.extend([limit, offset])
            users = execute_query(list_sql, list_params)

            for user in users:
                user.pop("card", None)

            logger.info(f"获取用户列表成功，共 {total} 条记录")
            return list(users), total
        except Exception as exc:
            logger.error(f"获取用户列表异常: {exc}")
            return [], 0

    def get_user_by_id(self, user_id: int) -> Optional[Dict[str, Any]]:
        """根据ID获取用户信息"""
        try:
            sql = """
                SELECT u.id, u.username, u.nickname, u.avatar, u.sex, u.age, u.phone,
                       u.email, u.birthday, u.card, u.address, u.education,
                       u.profession, u.company, u.content, u.remarks, u.role,
                       u.status, u.class_id, c.class_name, u.last_login_time,
                       u.last_login_ip, u.createtime, u.updatetime
                FROM py_user u
                LEFT JOIN py_class c ON u.class_id = c.id
                WHERE u.id = %s
            """
            users = execute_query(sql, (user_id,))
            if not users:
                return None

            user = dict(users[0])
            user.pop("card", None)
            return user
        except Exception as exc:
            logger.error(f"根据ID获取用户信息异常: {exc}")
            return None

    def update_user(self, user_id: int, data: Dict[str, Any]) -> bool:
        """更新用户信息"""
        try:
            update_fields: List[str] = []
            params: List[Any] = []
            allowed_fields: List[str] = [
                "nickname", "avatar", "sex", "age", "phone", "email",
                "birthday", "address", "education", "profession",
                "company", "content", "remarks", "role", "status"
            ]

            effective_role = self._get_effective_role(user_id, data)
            class_id, _ = self._resolve_class_binding(effective_role, data)

            for field in allowed_fields:
                if field in data and data[field] is not None:
                    update_fields.append(f"{field} = %s")
                    params.append(data[field])

            if effective_role in ["user", "doctor"]:
                update_fields.append("class_id = %s")
                params.append(class_id)
            elif "role" in data and data.get("role") == "admin":
                update_fields.append("class_id = %s")
                params.append(None)

            if not update_fields:
                return False

            update_fields.append("updatetime = %s")
            params.append(time.strftime("%Y-%m-%d %H:%M:%S"))
            params.append(user_id)

            sql = f"UPDATE py_user SET {', '.join(update_fields)} WHERE id = %s"
            result = execute_update(sql, params)
            if result > 0:
                logger.info(f"用户 {user_id} 信息更新成功")
                return True
            return False
        except ValueError:
            raise
        except Exception as exc:
            logger.error(f"更新用户信息异常: {exc}")
            return False

    def delete_user(self, user_id: int) -> bool:
        """删除用户"""
        try:
            sql = "DELETE FROM py_user WHERE id = %s"
            result = execute_delete(sql, (user_id,))
            if result > 0:
                logger.info(f"用户 {user_id} 删除成功")
                return True
            return False
        except Exception as exc:
            logger.error(f"删除用户异常: {exc}")
            return False

    def change_password(self, user_id: int, old_password: str, new_password: str) -> bool:
        """修改密码"""
        try:
            check_sql = "SELECT password FROM py_user WHERE id = %s"
            users = execute_query(check_sql, (user_id,))
            if not users:
                return False

            if users[0]["password"] != old_password:
                logger.warning(f"用户 {user_id} 原密码错误")
                return False

            update_sql = """
                UPDATE py_user
                SET password = %s, updatetime = %s
                WHERE id = %s
            """
            current_time: str = time.strftime("%Y-%m-%d %H:%M:%S")
            result = execute_update(update_sql, (new_password, current_time, user_id))
            if result > 0:
                logger.info(f"用户 {user_id} 密码修改成功")
                return True
            return False
        except Exception as exc:
            logger.error(f"修改密码异常: {exc}")
            return False

    def upload_avatar(self, user_id: int, file: Any) -> Optional[str]:
        """上传头像"""
        try:
            if not allowed_file(file.filename):
                logger.warning(f"不支持的文件类型: {file.filename}")
                return None

            filename = save_file(file)
            if not filename:
                return None

            avatar_url: str = f"/upload/{filename}"
            update_sql = """
                UPDATE py_user
                SET avatar = %s, updatetime = %s
                WHERE id = %s
            """
            current_time: str = time.strftime("%Y-%m-%d %H:%M:%S")
            result = execute_update(update_sql, (avatar_url, current_time, user_id))
            if result > 0:
                logger.info(f"用户 {user_id} 头像上传成功")
                return avatar_url
            return None
        except Exception as exc:
            logger.error(f"上传头像异常: {exc}")
            return None

    def add_user(self, data: Dict[str, Any]) -> bool:
        """添加用户"""
        try:
            check_sql = "SELECT id FROM py_user WHERE username = %s"
            existing_users = execute_query(check_sql, (data["username"],))
            if existing_users:
                logger.warning(f"用户名 {data['username']} 已存在")
                return False

            role: str = str(data.get("role", "user"))
            class_id, _ = self._resolve_class_binding(role, data)
            current_time: str = time.strftime("%Y-%m-%d %H:%M:%S")
            insert_sql = """
                INSERT INTO py_user
                (username, password, nickname, email, phone, sex, age, birthday,
                 address, education, profession, company, content, remarks,
                 role, status, class_id, createtime, updatetime)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                        %s, %s, %s, %s, %s)
            """
            execute_insert(
                insert_sql,
                (
                    data["username"],
                    hash_password(data["password"]),
                    data["nickname"],
                    data.get("email"),
                    data.get("phone"),
                    data.get("sex"),
                    data.get("age"),
                    data.get("birthday"),
                    data.get("address"),
                    data.get("education"),
                    data.get("profession"),
                    data.get("company"),
                    data.get("content"),
                    data.get("remarks"),
                    role,
                    data.get("status", "active"),
                    class_id,
                    current_time,
                    current_time
                )
            )
            logger.info(f"用户 {data['username']} 添加成功")
            return True
        except ValueError:
            raise
        except Exception as exc:
            logger.error(f"添加用户异常: {exc}")
            return False

    def get_user_statistics(self) -> Optional[Dict[str, Any]]:
        """获取用户统计信息"""
        try:
            total_sql = "SELECT COUNT(*) AS total FROM py_user"
            total_result = execute_query(total_sql)
            total_users: int = total_result[0]["total"] if total_result else 0

            role_sql = """
                SELECT role, COUNT(*) AS count
                FROM py_user
                WHERE status = 'active'
                GROUP BY role
            """
            role_result = execute_query(role_sql)

            status_sql = """
                SELECT status, COUNT(*) AS count
                FROM py_user
                GROUP BY status
            """
            status_result = execute_query(status_sql)

            statistics: Dict[str, Any] = {
                "total_users": total_users,
                "role_distribution": {item["role"]: item["count"] for item in role_result},
                "status_distribution": {item["status"]: item["count"] for item in status_result}
            }
            logger.info("获取用户统计信息成功")
            return statistics
        except Exception as exc:
            logger.error(f"获取用户统计信息异常: {exc}")
            return None
