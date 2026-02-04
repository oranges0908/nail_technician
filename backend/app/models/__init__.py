# 导入所有模型，确保 Alembic 能够检测到
from app.db.database import Base

# 在这里导入所有模型
# from .user import User
# from .item import Item

__all__ = ["Base"]
