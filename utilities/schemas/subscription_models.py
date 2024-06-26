from datetime import datetime

from sqlalchemy import Column, Integer, DateTime, ForeignKey, Numeric, JSON, String
from sqlalchemy.orm import relationship

from utilities.schemas import tables
from utilities.schemas.base import Base


#Album model for all albums for all users i.e. vendor
class Album(Base):
    __tablename__ = tables.ALBUM

    id = Column(Integer, primary_key=True, autoincrement=True)
    album_name = Column(String, nullable=False)
    num_image = Column(Integer)
    album_type = Column(String)  # profile album, wedding1, venue-space-1
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)


#Image Model for all image storage
class Image(Base):
    __tablename__ = tables.IMAGE
    id = Column(Integer, primary_key=True, autoincrement=True)
    url = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow())
    user_id = Column(Integer, ForeignKey('users.id'), nullable=True)
    album_id = Column(Integer, ForeignKey('album.id'), nullable=True)
    image_type = Column(String, nullable=False)  # e.g., 'profile', 'gallery'


class Subscription(Base):
    __tablename__ = tables.SUBSCRIPTION
    id = Column(Integer, primary_key=True, autoincrement=True)
    subscription_name = Column(String, nullable=False)
    num_images_allowed = Column(Integer, nullable=False)
    sub_price = Column(Numeric, nullable=False, default=0)
    features_incl = Column(String, nullable=False)
    billing_cycle = Column(String, nullable=False)
    sub_duration = Column(String, nullable=False)  # define how long each subscription lasts
    sub_category = Column(String)  # premium/...
    description = Column(String)
    industry_id = Column(Integer, ForeignKey('vendor_industry.id', ondelete='CASCADE'), nullable=False,
                         index=True)


class VendorSubscription(Base):
    __tablename__ = tables.VENDOR_SUBSCRIPTION
    id = Column(Integer, primary_key=True, autoincrement=True)
    subscription_id = Column(Integer, ForeignKey('subscription.id'), nullable=False, index=True)
    vendor_id = Column(Integer, ForeignKey('vendor_profile.id'), nullable=False, index=True)

    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)
    billing_status = Column(String, nullable=False)
    active_status = Column(String, nullable=False)
    exceptions = Column(JSON)
    addn_rates = Column(JSON)
    approved_on = Column(DateTime, nullable=False)
