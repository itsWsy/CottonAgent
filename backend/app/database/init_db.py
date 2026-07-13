from datetime import date, timedelta

from sqlalchemy import select
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.security import hash_password
from app.database.session import engine, SessionLocal
from app.database.base import Base
from app.models import CottonField, FarmRecord, User


def init_db() -> None:
    Base.metadata.create_all(bind=engine)
    ensure_compatible_schema()
    db = SessionLocal()
    try:
        seed_data(db)
    finally:
        db.close()


def ensure_compatible_schema() -> None:
    """Small V1 compatibility migration for local SQLite demo databases."""
    if not str(engine.url).startswith("sqlite"):
        return
    with engine.begin() as conn:
        columns = {row[1] for row in conn.execute(text("PRAGMA table_info(recommendations)")).fetchall()}
        if "scoreBreakdown" not in columns:
            conn.execute(text("ALTER TABLE recommendations ADD COLUMN scoreBreakdown TEXT DEFAULT '{}'"))
        if "reasonItems" not in columns:
            conn.execute(text("ALTER TABLE recommendations ADD COLUMN reasonItems TEXT DEFAULT '[]'"))
        if "candidateSources" not in columns:
            conn.execute(text("ALTER TABLE recommendations ADD COLUMN candidateSources TEXT DEFAULT '[]'"))


def seed_data(db: Session) -> None:
    admin = db.scalar(select(User).where(User.username == "admin"))
    if not admin:
        admin = User(username="admin", passwordHash=hash_password("123456"))
        db.add(admin)
        db.flush()
    if db.scalar(select(CottonField).where(CottonField.userId == admin.id)):
        db.commit()
        return
    fields = [
        CottonField(userId=admin.id, name="1 号试验田", variety="新陆早 78 号", area=42.5, region="阿克苏", growthStage="花铃期", sowingDate=date.today() - timedelta(days=92), description="滴灌棉田，近期重点观察虫情。"),
        CottonField(userId=admin.id, name="2 号示范田", variety="新陆中 82 号", area=35.0, region="库尔勒", growthStage="蕾期", sowingDate=date.today() - timedelta(days=68), description="长势均匀，需关注落蕾风险。"),
        CottonField(userId=admin.id, name="3 号观察田", variety="新陆早 61 号", area=28.0, region="石河子", growthStage="苗期", sowingDate=date.today() - timedelta(days=36), description="苗情监测样方。"),
    ]
    db.add_all(fields)
    db.flush()
    records = [
        FarmRecord(fieldId=fields[0].id, actionCode="FIELD_SCOUTING", actionName="田间巡查", operationDate=date.today() - timedelta(days=8), description="叶片整体正常，局部有卷曲。"),
        FarmRecord(fieldId=fields[0].id, actionCode="PEST_SAMPLE", actionName="虫情采样", operationDate=date.today() - timedelta(days=4), description="发现少量蚜虫。"),
        FarmRecord(fieldId=fields[1].id, actionCode="GROWTH_ASSESSMENT", actionName="长势评估", operationDate=date.today() - timedelta(days=6), description="蕾期长势正常。"),
        FarmRecord(fieldId=fields[2].id, actionCode="WEED_MONITOR", actionName="杂草监测", operationDate=date.today() - timedelta(days=5), description="行间少量杂草。"),
    ]
    db.add_all(records)
    db.commit()
