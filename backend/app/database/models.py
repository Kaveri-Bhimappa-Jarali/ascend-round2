"""
SQLAlchemy database model definitions.
"""
from sqlalchemy import Column, Integer, String, DateTime, JSON
from app.database.database import Base

class ResourceDB(Base):
    __tablename__ = "resources"
    id = Column(Integer, primary_key=True, index=True)
    # Fields to define

class ComplianceResultDB(Base):
    __tablename__ = "compliance_results"
    id = Column(Integer, primary_key=True, index=True)
    # Fields to define

class ViolationDB(Base):
    __tablename__ = "violations"
    id = Column(Integer, primary_key=True, index=True)
    # Fields to define
