"""SQLAlchemy database model definitions."""

from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, ForeignKey, Integer, JSON, String, UniqueConstraint
from sqlalchemy.orm import relationship

from app.database.database import Base


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class ResourceDB(Base):
    __tablename__ = "resources"
    __table_args__ = (
        UniqueConstraint("provider", "resource_type", "resource_id", name="uq_resource_identity"),
    )

    id = Column(Integer, primary_key=True, index=True)
    provider = Column(String(64), nullable=False, index=True)
    resource_type = Column(String(64), nullable=False, index=True)
    resource_id = Column(String(255), nullable=False, index=True)
    resource_name = Column(String(255), nullable=False)
    configuration = Column(JSON, nullable=False, default=dict)
    last_seen = Column(DateTime(timezone=True), nullable=False, default=utc_now)

    violations = relationship(
        "ViolationDB",
        back_populates="resource",
        cascade="all, delete-orphan",
    )


class ViolationDB(Base):
    __tablename__ = "violations"
    __table_args__ = (
        UniqueConstraint("resource_db_id", "rule_id", name="uq_violation_resource_rule"),
    )

    id = Column(Integer, primary_key=True, index=True)
    resource_db_id = Column(Integer, ForeignKey("resources.id", ondelete="CASCADE"), nullable=False, index=True)
    resource_id = Column(String(255), nullable=False, index=True)
    rule_id = Column(String(128), nullable=False, index=True)
    severity = Column(String(32), nullable=False, index=True)
    message = Column(String(500), nullable=False)
    status = Column(String(32), nullable=False, default="FAIL", index=True)
    detected_at = Column(DateTime(timezone=True), nullable=False, default=utc_now)

    resource = relationship("ResourceDB", back_populates="violations")
