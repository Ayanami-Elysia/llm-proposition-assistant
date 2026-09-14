from typing import Any, Dict, List, Optional, Tuple
import logging
import time

from utils.db_utils import execute_insert, execute_query

logger = logging.getLogger(__name__)


class ClassService:
    """班级服务类"""

    def get_class_options(self, keyword: str = "") -> List[Dict[str, Any]]:
        """获取班级选项列表"""
        try:
            params: List[Any] = []
            where_clause: str = ""

            if keyword:
                where_clause = "WHERE class_name LIKE %s"
                params.append(f"%{keyword}%")

            sql = f"""
                SELECT id, class_name, description, status
                FROM py_class
                {where_clause}
                ORDER BY class_name ASC
            """
            return list(execute_query(sql, params))
        except Exception as exc:
            logger.error(f"获取班级列表异常: {exc}")
            return []

    def resolve_class_binding(
        self,
        class_id: Optional[Any] = None,
        class_name: Optional[str] = None
    ) -> Tuple[Optional[int], Optional[str]]:
        """解析班级绑定信息，不存在时自动创建班级"""
        try:
            normalized_name: str = (class_name or "").strip()
            normalized_id: Optional[int] = None

            if class_id not in (None, ""):
                normalized_id = int(class_id)

            if normalized_id is not None:
                sql = """
                    SELECT id, class_name
                    FROM py_class
                    WHERE id = %s
                    LIMIT 1
                """
                records = execute_query(sql, (normalized_id,))
                if records:
                    record = records[0]
                    return record["id"], record["class_name"]

            if not normalized_name:
                return None, None

            query_sql = """
                SELECT id, class_name
                FROM py_class
                WHERE class_name = %s
                LIMIT 1
            """
            records = execute_query(query_sql, (normalized_name,))
            if records:
                record = records[0]
                return record["id"], record["class_name"]

            current_time: str = time.strftime("%Y-%m-%d %H:%M:%S")
            insert_sql = """
                INSERT INTO py_class (class_name, status, createtime, updatetime)
                VALUES (%s, %s, %s, %s)
            """
            new_id = execute_insert(
                insert_sql,
                (normalized_name, "active", current_time, current_time)
            )
            return new_id, normalized_name
        except (TypeError, ValueError) as exc:
            logger.error(f"班级编号格式异常: {exc}")
            raise ValueError("班级编号格式不正确")
        except Exception as exc:
            logger.error(f"解析班级绑定异常: {exc}")
            raise ValueError("班级信息处理失败")
