"""
对话文件管理服务
本地 JSONL 文件存储：每个会话一个文件，按步骤分段，用于审计/回放
"""
import json
import logging
from pathlib import Path
from typing import List
import datetime

from app.core.config import settings

logger = logging.getLogger(__name__)


class ConversationFileManager:
    """
    管理本地 JSONL 格式的对话文件。

    文件路径：{CONVERSATIONS_DIR}/{session_id}/messages.jsonl
    每行一条消息（JSON 对象）。

    消息字段：
      - step: 步骤名称（如 "customer", "design"）
      - archived: 是否已归档（bool）
      - role: 消息角色（"user" | "assistant" | "tool" | "system"）
      - content: 消息内容（可选，部分角色使用 tool_calls 代替）
      - tool_calls: LLM 工具调用列表（assistant 角色，可选）
      - tool_call_id: 工具调用 ID（tool 角色，可选）
      - name: 工具名称（tool 角色，可选）
      - ui_metadata: UI 元数据（assistant 最终回复，可选）
      - ts: ISO 8601 时间戳
    """

    @staticmethod
    def _base_dir() -> Path:
        return Path(settings.CONVERSATIONS_DIR)

    @staticmethod
    def get_session_dir(session_id: int) -> Path:
        """返回该会话的目录，自动创建"""
        session_dir = ConversationFileManager._base_dir() / str(session_id)
        session_dir.mkdir(parents=True, exist_ok=True)
        return session_dir

    @staticmethod
    def get_file_path(session_id: int) -> Path:
        """返回该会话的 JSONL 文件路径"""
        return ConversationFileManager.get_session_dir(session_id) / "messages.jsonl"

    @staticmethod
    def append_message(session_id: int, message: dict) -> None:
        """追加一条消息到 JSONL 文件（每行一个 JSON 对象）"""
        if "ts" not in message:
            message["ts"] = datetime.datetime.utcnow().isoformat()

        file_path = ConversationFileManager.get_file_path(session_id)
        try:
            with open(file_path, "a", encoding="utf-8") as f:
                f.write(json.dumps(message, ensure_ascii=False) + "\n")
        except Exception as e:
            logger.error(f"写入对话文件失败 session_id={session_id}: {e}")

    @staticmethod
    def read_current_step_messages(session_id: int, current_step: str) -> List[dict]:
        """
        读取当前步骤（未归档）的消息，用于构建 LLM 上下文。
        跳过归档标记行，只返回普通消息对象。
        """
        file_path = ConversationFileManager.get_file_path(session_id)
        if not file_path.exists():
            return []

        messages = []
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        msg = json.loads(line)
                    except json.JSONDecodeError:
                        continue
                    # 跳过归档标记行
                    if msg.get("_archive_marker"):
                        continue
                    # 只取当前步骤且未归档的消息
                    if msg.get("step") == current_step and not msg.get("archived", False):
                        messages.append(msg)
        except Exception as e:
            logger.error(f"读取对话文件失败 session_id={session_id}: {e}")

        return messages

    @staticmethod
    def archive_step(session_id: int, step_name: str) -> None:
        """
        将指定步骤的所有消息标记为 archived。
        在原文件末尾追加一条归档标记，并重写文件将该步骤的 archived 设为 true。
        """
        file_path = ConversationFileManager.get_file_path(session_id)
        if not file_path.exists():
            return

        # 读取所有行，将匹配步骤的消息 archived 设为 true
        updated_lines = []
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        msg = json.loads(line)
                    except json.JSONDecodeError:
                        updated_lines.append(line)
                        continue
                    if msg.get("step") == step_name and not msg.get("_archive_marker"):
                        msg["archived"] = True
                    updated_lines.append(json.dumps(msg, ensure_ascii=False))
        except Exception as e:
            logger.error(f"归档步骤失败 session_id={session_id} step={step_name}: {e}")
            return

        # 重写文件
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                for line in updated_lines:
                    f.write(line + "\n")

            # 追加归档标记行
            marker = {
                "_archive_marker": True,
                "step": step_name,
                "ts": datetime.datetime.utcnow().isoformat(),
            }
            with open(file_path, "a", encoding="utf-8") as f:
                f.write(json.dumps(marker, ensure_ascii=False) + "\n")
        except Exception as e:
            logger.error(f"重写对话文件失败 session_id={session_id}: {e}")

    @staticmethod
    def read_full_history(session_id: int) -> List[dict]:
        """读取完整历史（用于回放/审计），包含所有消息和归档标记"""
        file_path = ConversationFileManager.get_file_path(session_id)
        if not file_path.exists():
            return []

        messages = []
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        messages.append(json.loads(line))
                    except json.JSONDecodeError:
                        continue
        except Exception as e:
            logger.error(f"读取完整历史失败 session_id={session_id}: {e}")

        return messages
