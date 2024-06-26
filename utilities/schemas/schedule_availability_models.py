from sqlalchemy import Column, Integer, Date, Time, ForeignKey, Numeric, JSON, String
from sqlalchemy.orm import relationship

from utilities.schemas import tables
from utilities.schemas.base import Base


class Shift(Base):
    __tablename__ = tables.SHIFTS
    id = Column(Integer, primary_key=True, autoincrement=True)
    shift_name = Column(String)
    shift_time = Column(Time)
    booking_capacity = Column(Integer, default=1)
    vendor_profile_id = Column(Integer, ForeignKey('vendor_profile.id'), nullable=False)
    space_id = Column(Integer, ForeignKey('spaces.id'), nullable=True)


class Schedule(Base):
    __tablename__ = tables.SCHEDULE
    id = Column(Integer, primary_key=True, autoincrement=True)
    schedule = Column(JSON)
    vendor_profile_id = Column(Integer, ForeignKey('vendor_profile.id'), nullable=False)
    space_id = Column(Integer, ForeignKey('spaces.id'), nullable=True)


class Availability(Base):
    __tablename__ = tables.AVAILABILITY
    id = Column(Integer, primary_key=True, autoincrement=True)
    date = Column(Date)
    status = Column(String)
    shift_id = Column(Integer, ForeignKey('shifts.id'), nullable=False)
    vendor_profile_id = Column(Integer, ForeignKey('vendor_profile.id'), nullable=False)
    space_id = Column(Integer, ForeignKey('spaces.id'), nullable=True)
