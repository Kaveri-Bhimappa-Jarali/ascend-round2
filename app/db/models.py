from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class ResourceSnapshot(Base):
    __tablename__ = "resource_snapshots"
    __table_args__ = (
        UniqueConstraint("provider", "resource_type", "resource_id", name="uq_resource_identity"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    provider: Mapped[str] = mapped_column(String(32), index=True)
    resource_type: Mapped[str] = mapped_column(String(64), index=True)
    resource_id: Mapped[str] = mapped_column(String(255), index=True)
    name: Mapped[str] = mapped_column(String(255))
    region: Mapped[str | None] = mapped_column(String(128), nullable=True)
    configuration_json: Mapped[str] = mapped_column(Text, default="{}")
    last_seen: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    violations: Mapped[list["Violation"]] = relationship(
        back_populates="resource_snapshot",
        cascade="all, delete-orphan",
    )

    def to_dict(self) -> dict[str, object]:
        return {
            "id": self.id,
            "provider": self.provider,
            "resource_type": self.resource_type,
            "resource_id": self.resource_id,
            "name": self.name,
            "region": self.region,
            "configuration_json": self.configuration_json,
            "last_seen": self.last_seen.isoformat() if self.last_seen else None,
        }


class Violation(Base):
    __tablename__ = "violations"
    __table_args__ = (
        UniqueConstraint(
            "resource_snapshot_id",
            "rule_id",
            name="uq_violation_resource_snapshot_rule",
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    resource_snapshot_id: Mapped[int] = mapped_column(
        ForeignKey("resource_snapshots.id"),
        index=True,
    )
    rule_id: Mapped[str] = mapped_column(String(128), index=True)
    status: Mapped[str] = mapped_column(String(32), index=True)
    severity: Mapped[str] = mapped_column(String(32), index=True)
    message: Mapped[str] = mapped_column(Text)
    detected_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    resource_snapshot: Mapped[ResourceSnapshot] = relationship(back_populates="violations")

    def to_dict(self) -> dict[str, object]:
        resource = self.resource_snapshot

        return {
            "id": self.id,
            "provider": resource.provider if resource else None,
            "resource_type": resource.resource_type if resource else None,
            "resource_id": resource.resource_id if resource else None,
            "rule_id": self.rule_id,
            "status": self.status,
            "severity": self.severity,
            "message": self.message,
            "detected_at": self.detected_at.isoformat() if self.detected_at else None,
        }
