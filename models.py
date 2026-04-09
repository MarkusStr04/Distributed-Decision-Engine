from sqlalchemy import Column, Integer, Float, String, DateTime
from sqlalchemy.dialects.postgresql import JSONB
from datetime import datetime, timezone
from database import Base

class Decision(Base):
    __tablename__ = "decisions"

    # unique identifier for each row, auto-incremented by Postgres
    id = Column(Integer, primary_key=True, autoincrement=True)
    # raw request payload stored as JSONB for flexible querying
    payload = Column(JSONB, nullable=False)

    score = Column(Float, nullable=False)
    decision = Column(String(10), nullable=False)

    # lambda ensures the timestamp is evaluated at insert time, not at startup
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))