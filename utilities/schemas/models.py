import datetime

from flask import current_app

from sqlalchemy import Column, Integer, String, Boolean, Text, Date, Time, DateTime, Numeric, ForeignKey, DECIMAL, JSON
from sqlalchemy.orm import relationship
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import URLSafeTimedSerializer as Serializer
from utilities.schemas import tables
from utilities.schemas.base import Base


# TODO: Check Relationships
class User(Base):
    __tablename__ = tables.USERS

    id = Column(Integer, primary_key=True, autoincrement=True)
    fullname = Column(String, nullable=False)
    email = Column(String, nullable=False, unique=True)
    password = Column(String, nullable=False)
    phone_number = Column(String)
    # logged_in_at = Column(DateTime)
    # logged_out_at = Column(DateTime)
    is_verified = Column(Boolean)
    verification_code = Column(String)
    created_at = Column(DateTime)
    user_type_id = Column(Integer, ForeignKey('user_type.id'), nullable=False)


    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

    def generate_reset_token(self):
        s = Serializer(current_app.secret_key)
        token = s.dumps({'user_id': self.id})
        return token


class UserType(Base):
    __tablename__ = tables.USER_TYPE

    id = Column(Integer, primary_key=True, autoincrement=True)
    type_name = Column(String)

    users = relationship("User", backref=tables.USER_TYPE)


class UserLogs(Base):
    __tablename__ = tables.USER_LOGS

    id = Column(Integer, primary_key=True, autoincrement=True)
    action_performed = Column(String)
    action_time = Column(DateTime)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False, index=True)


class ConsumerProfile(Base):
    __tablename__ = tables.CONSUMER_PROFILE

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False, unique=True, index=True)
    image = Column(String)
    gender = Column(String)
    last_updated = Column(Date, nullable=False, index=True)

    users = relationship("User", backref=tables.CONSUMER_PROFILE)


class VendorProfile(Base):
    __tablename__ = tables.VENDOR_PROFILE

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False, unique=True)
    # business_name = Column(String)
    # description = Column(Text)  # check for datatype
    vendor_type = Column(String)
    # defines the vendor industry type example, venues, catering.....should be dropdown(fixed options by saahitt)
    industry_id = Column(Integer, ForeignKey('vendor_industry.id', ondelete='CASCADE'), nullable=False,
                         index=True)

    # additional changes in schema for vendor profile

    estd_date = Column(Date)  # years of service/years in the industry(date of establishment)
    location = Column(String)
    profile_image = Column(String)
    # base_price = Column(String)
    pan_number = Column(String, unique=True)
    pan_image = Column(String)
    pan_holder_citizenship = Column(String)
    pan_holder_photo = Column(String)
    # rating & review and gallery models to be created
    last_updated = Column(Date)
    is_sa_verified = Column(Boolean, nullable=False, default=False)


class VendorIndustry(Base):
    __tablename__ = tables.VENDOR_INDUSTRY

    id = Column(Integer, primary_key=True, autoincrement=True)
    industry_name = Column(String, nullable=False)
    additional_fields = Column(JSON)

    # vendor_profile = relationship("VendorProfile", back_populates="vendor_industry", cascade="all, delete")
    venues = relationship("Venue", back_populates=tables.VENDOR_INDUSTRY, cascade="all, delete")


class Venue(Base):
    __tablename__ = tables.VENUES

    id = Column(Integer, primary_key=True, autoincrement=True)
    venue_name = Column(String)
    location = Column(String)
    mandatory_catering = Column(Boolean)
    venue_type = Column(String)
    parking_capacity = Column(Integer)
    industry_id = Column(Integer, ForeignKey('vendor_industry.id'), nullable=False)
    vendor_profile_id = Column(Integer, ForeignKey('vendor_profile.id'), nullable=False)
    vendor_industry = relationship("VendorIndustry", back_populates=tables.VENUES)
    spaces = relationship("VenueSpace", back_populates=tables.VENUES, cascade="all, delete")
    # menu = relationship("Menu", back_populates=tables.VENUES, cascade="all, delete")


class Menu(Base):
    __tablename__ = tables.MENU
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String)
    cuisine = Column(String)
    description = Column(String)
    rate = Column(Numeric)
    no_of_items = Column(Numeric)
    vendor_profile_id = Column(Integer, ForeignKey('vendor_profile.id'), nullable=False)

    # venues = relationship("Venue", back_populates=tables.MENU)
    # food_items = relationship("FoodItem", secondary=tables.MENU, cascade="all, delete")


class FoodItem(Base):
    __tablename__ = tables.FOOD_ITEMS
    id = Column(Integer, primary_key=True, autoincrement=True)
    item_name = Column(String)
    item_price = Column(Numeric)
    item_description = Column(String)
    type = Column(String)
    vendor_profile_id = Column(Integer, ForeignKey('vendor_profile.id'), nullable=False)


class MenuItemTable(Base):
    __tablename__ = tables.MENU_FOOD_ITEMS
    id = Column(Integer, primary_key=True, autoincrement=True)
    item_id = Column(Integer, ForeignKey('food_items.id'), nullable=False)
    menu_id = Column(Integer, ForeignKey('menu.id'), nullable=False)


class VenueSpace(Base):
    __tablename__ = tables.SPACES

    id = Column(Integer, primary_key=True, autoincrement=True)
    space_name = Column(String)
    space_type = Column(String)  # i.e outdoor, indoor, poolside etc.
    description = Column(String)
    rate = Column(Numeric)
    type_of_charge = Column(String)  # hourly, fixed, period_of_time which is the charge based on
    seating_capacity = Column(Integer)
    floating_capacity = Column(Integer)
    venue_id = Column(Integer, ForeignKey('venues.id'), nullable=False)

    venues = relationship("Venue", back_populates=tables.SPACES)
    # schedule = relationship("Schedule", back_populates="spaces", cascade="all, delete")


# class Schedule(Base):
#     __tablename__ = tables.SCHEDULE
#
#     id = Column(Integer, primary_key=True, autoincrement=True)
#     date = Column(Date)
#     time_range = Column(Time)
#     space_id = Column(Integer, ForeignKey('spaces.id'), nullable=False)

    # space = relationship("Spaces", back_populates="schedule")


class CateringPackage(Base):
    __tablename__ = tables.CATERING_PACKAGE

    id = Column(Integer, primary_key=True, autoincrement=True)
    package_name = Column(String)
    price = Column(Numeric)
    type = Column(String)
    variety_qty = Column(Integer)


class VenueBooking(Base):
    __tablename__ = tables.VENUE_BOOKINGS

    id = Column(Integer, primary_key=True, autoincrement=True)
    booked_date = Column(DateTime)
    booked_quantity = Column(Integer)
    status = Column(String)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    space_id = Column(Integer, ForeignKey('spaces.id'), nullable=False)
    menu_id = Column(Integer, ForeignKey('menu.id'), nullable=False)

    # users = relationship("User", back_populates=tables.VENUE_BOOKINGS)


class Invoice(Base):
    __tablename__ = tables.INVOICE

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_name = Column(String)
    issued_date = Column(DateTime)
    total_price = Column(DECIMAL)  # to change to decimal


class VenueType(Base):
    __tablename__ = tables.VENUE_TYPES
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)


# class ConsumerActivityLog(Base):
#     __tablename__ = tables.CONSUMER_ACTIVITY_LOG
#     id = Column(Integer, primary_key=True, autoincrement=True)
#     level = Column(String)
#     message = Column(String)
#     user_id = Column(Integer)
#     created_at = Column(DateTime, default=datetime.datetime.now())
#
#
# class VendorActivityLog(Base):
#     __tablename__ = tables.VENDOR_ACTIVITY_LOG
#     id = Column(Integer, primary_key=True, autoincrement=True)
#     level = Column(String)
#     message = Column(String)
#     user_id = Column(Integer)
#     created_at = Column(DateTime, default=datetime.datetime.now())

class VendorDynamicFormTable(Base):
    __tablename__ = tables.VENDOR_DYNAMIC_FORM
    id = Column(Integer, primary_key=True, autoincrement=True)
    form_name = Column(String)
    schema = Column(JSON)
    vendor_id = Column(Integer, ForeignKey(User.id), nullable=False)

