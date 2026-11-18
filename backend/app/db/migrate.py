"""针对 SQLite 的轻量级结构迁移。

项目使用 `create_all` 建表，但对已存在的表不会自动新增列。这里在启动时
检查缺失的列并用 `ALTER TABLE ADD COLUMN` 补齐，避免丢失既有数据。
"""

from sqlalchemy import inspect, text

from app.db.session import engine


def _column_statements() -> dict[str, str]:
    return {
        "recipient": "ALTER TABLE stock_movements ADD COLUMN recipient VARCHAR(64)",
        "placement_location": (
            "ALTER TABLE stock_movements ADD COLUMN placement_location VARCHAR(128)"
        ),
        "is_return": (
            "ALTER TABLE stock_movements ADD COLUMN is_return BOOLEAN NOT NULL DEFAULT 0"
        ),
        "return_of_id": "ALTER TABLE stock_movements ADD COLUMN return_of_id INTEGER",
    }


def run_lightweight_migrations() -> None:
    if engine.dialect.name != "sqlite":
        return
    inspector = inspect(engine)
    if "stock_movements" not in inspector.get_table_names():
        return

    existing = {col["name"] for col in inspector.get_columns("stock_movements")}
    pending = [sql for name, sql in _column_statements().items() if name not in existing]
    if not pending:
        return

    with engine.begin() as conn:
        for statement in pending:
            conn.execute(text(statement))
