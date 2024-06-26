from datetime import datetime

from sqlalchemy import Column, Integer, DateTime, ForeignKey, Numeric, JSON, String
from sqlalchemy.orm import relationship

from utilities.schemas import tables
from utilities.schemas.base import Base


class ConsumerActivityLog(Base):
    __tablename__ = tables.CONSUMER_ACTIVITY_LOG
    id = Column(Integer, primary_key=True, autoincrement=True)
    level = Column(String)
    message = Column(String)
    user_id = Column(Integer)
    created_at = Column(DateTime, default=datetime.now())


class VendorActivityLog(Base):
    __tablename__ = tables.VENDOR_ACTIVITY_LOG
    id = Column(Integer, primary_key=True, autoincrement=True)
    level = Column(String)
    message = Column(String)
    user_id = Column(Integer)
    created_at = Column(DateTime, default=datetime.now())
