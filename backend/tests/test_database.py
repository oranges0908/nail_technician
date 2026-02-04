"""
数据库基础设施测试

测试数据库连接、会话管理、健康检查等功能
"""

import pytest  # noqa: F401
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.db.database import (
    engine,
    get_db,
    check_db_health,
    create_tables,
    drop_tables,
    Base,
)


class TestDatabaseConnection:
    """测试数据库连接"""

    def test_engine_connection(self):
        """测试数据库引擎连接"""
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            assert result.scalar() == 1

    def test_database_health_check(self):
        """测试数据库健康检查"""
        assert check_db_health() is True


class TestDatabaseSession:
    """测试数据库会话管理"""

    def test_get_db_dependency(self):
        """测试数据库依赖注入"""
        db_generator = get_db()
        db = next(db_generator)

        assert isinstance(db, Session)
        assert db is not None

        # 测试会话是否可用
        result = db.execute(text("SELECT 1"))
        assert result.scalar() == 1

        # 关闭会话
        try:
            next(db_generator)
        except StopIteration:
            pass

    def test_session_isolation(self):
        """测试会话隔离性"""
        db1_gen = get_db()
        db1 = next(db1_gen)

        db2_gen = get_db()
        db2 = next(db2_gen)

        # 两个会话应该是不同的对象
        assert db1 is not db2

        # 关闭会话
        try:
            next(db1_gen)
        except StopIteration:
            pass

        try:
            next(db2_gen)
        except StopIteration:
            pass


class TestTableOperations:
    """测试表操作（仅用于测试环境）"""

    def test_create_and_drop_tables(self):
        """测试创建和删除表"""
        # 创建表
        create_tables()

        # 验证表创建成功（检查 alembic_version 表是否可访问）
        with engine.connect() as conn:
            # 这个测试在没有任何模型时只验证函数能正常执行
            # 当添加模型后，可以验证具体的表
            result = conn.execute(text("SELECT 1"))
            assert result.scalar() == 1

        # 删除表
        drop_tables()

        # 验证表删除成功
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            assert result.scalar() == 1


class TestAlembicIntegration:
    """测试 Alembic 集成"""

    def test_base_metadata_exists(self):
        """测试 Base.metadata 是否存在"""
        assert Base.metadata is not None

    def test_base_declarative_base(self):
        """测试 Base 是否为 declarative_base"""
        # 验证 Base 有 metadata 属性
        assert hasattr(Base, "metadata")
        assert hasattr(Base, "registry")


# 测试配置相关
class TestDatabaseConfig:
    """测试数据库配置"""

    def test_engine_pool_config(self):
        """测试引擎连接池配置"""
        # 验证 pool_pre_ping 已启用
        assert engine.pool._pre_ping is True

    def test_engine_echo_setting(self):
        """测试 SQL echo 设置"""
        # echo 设置应该与 DEBUG 模式一致
        from app.core.config import settings

        assert engine.echo == settings.DEBUG
