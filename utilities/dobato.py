import asyncio
import json
import logging
import math

from flask import g, request, jsonify
from flask.views import MethodView
from flask_jwt_extended import verify_jwt_in_request, get_current_user
from flask_jwt_extended.exceptions import NoAuthorizationError
from sqlalchemy.exc import SQLAlchemyError

from utilities.db_getter import Session, get_session
from utilities.log_utils import setup_logger
from utilities.responses import bad_request_error
from utilities.schemas.models import UserType, VendorProfile
from utilities.schemas.log_models import ConsumerActivityLog, VendorActivityLog


def load_current_user():
    try:
        verify_jwt_in_request()
    except NoAuthorizationError:
        return None
    try:
        return get_current_user()
    except Exception as e:
        logging.getLogger('Dobato Logger').error(f"Error loading current user: {e}")
        return None


class DobatoApi(MethodView):
    _page = None
    _per_page = None
    _user = None

    def __init__(self, auth=None):
        self._user = None
        self.db_session = g.db_session()
        self.consumer_logger = setup_logger(logger_name="CONSUMER_LOGGER", log_model=ConsumerActivityLog)
        self.vendor_logger = setup_logger(logger_name="VENDOR_LOGGER", log_model=VendorActivityLog)
        self.general_logger = logging.getLogger("DOBATO_LOGGER")

    @property
    def user(self):
        if self._user is None:
            user = load_current_user()
            if user is None:
                return None
            self._user = user
        g.user_id = self._user.id
        return self._user

    def get_type_id(self, type_name):
        try:
            user_type = self.db_session.query(UserType).filter(UserType.type_name == type_name).first()
            if user_type:
                return user_type.id
        except SQLAlchemyError as e:
            self.logger.error(f"Database error while fetching {type_name} type ID: {e}")
            return None

    # def get_vendor_status(self, user_id):
    #     try:
    #         vendor_profile = self.db_session.query(VendorProfile).filter(
    #             VendorProfile.user_id == user_id).first()
    #         if not vendor_profile:
    #             return bad_request_error("Vendor profile doesn't exists")
    #         is_sa_verified = vendor_profile.is_sa_verified
    #         return is_sa_verified
    #     except SQLAlchemyError as e:
    #         self.logger.error(f"Database error while fetching vendor verification status: {e}")
    #         return None

    def get_consumer_type_id(self):
        return self.get_type_id('Consumer')

    def get_vendor_type_id(self):
        return self.get_type_id('Vendor')

    def get_super_admin_type_id(self):
        return self.get_type_id('SuperAdmin')

    def is_consumer(self, type_id):
        return type_id == self.get_consumer_type_id()

    def is_vendor(self, type_id):
        return type_id == self.get_vendor_type_id()

    def is_super_admin(self, type_id):
        return type_id == self.get_super_admin_type_id()

    def is_vendor_verified(self, vendor_profile):
        status = vendor_profile.is_sa_verified
        return status

    @staticmethod
    def make_obj_serializable(rows):
        if isinstance(rows, list):
            dict_rows = []
            for row in rows:
                dict_row = row.__dict__
                dict_row.pop('_sa_instance_state')
                dict_rows.append(dict_row)
            return dict_rows
        else:
            dict_row = rows.__dict__
            dict_row.pop('_sa_instance_state')
            return dict_row

    async def send_message(self, msg, port):
        # Open connection and send message
        try:
            json_msg = json.dumps(msg)  # serialize before sending message
            reader, writer = await asyncio.open_connection('localhost', port)
            writer.write(json_msg.encode())  # Encode JSON string before sending
            await writer.drain()  # Ensure the message is written before closing
        except Exception as e:
            print(f"Failed to send message: {e}")
        finally:
            if 'writer' in locals() and not writer.is_closing():
                writer.close()

    def commit(self):
        try:
            self.db_session.commit()
        except SQLAlchemyError as e:
            self.general_logger.error(f"Commit error: {e}")
            self.db_session.rollback()

    def page(self):
        if self._page is not None:
            return self._page
        page = request.args.get('page', 1)
        try:
            page = int(page)
        except ValueError:
            page = 1
        if page < 0:
            page = 1
        self._page = page
        return self._page

    def limit(self):
        if self._per_page is not None:
            return self._per_page
        per_page = request.args.get('per_page', 100)
        try:
            per_page = int(per_page)
        except ValueError:
            per_page = 100
        if per_page < 0:
            per_page = 100
        self._per_page = per_page
        return self._per_page

    def offset(self):
        previous_page = self.page() - 1
        return previous_page * self.limit()

    def pagination_meta(self, count, limit=None):
        if limit is None:
            limit = self.limit()
        pages = max(int(math.ceil(float(count) / limit)), 1)
        pagination = '{page}/{pages}'.format(page=self.page(), pages=pages)
        return {
            'total_count': count,
            'pagination': pagination,
            'requested_count': limit
        }

    def list_response(self, rows, count=None, limit=None):
        if count is None:
            count = len(rows)
        meta = self.pagination_meta(count, limit)
        meta['data_count'] = len(rows)
        response = {
            'data': {
                'rows': rows
            },
            'meta': meta
        }

        return jsonify(response)

    @staticmethod
    def detail_response(data):
        response = {
            'data': data
        }
        return jsonify(response)

    @property
    def db(self) -> Session:
        return self.db_session

    def log_message(self, message, _type='INFO'):
        logger = self.general_logger
        if self.user:
            if self.is_consumer(self.user.user_type_id):
                logger = logging.LoggerAdapter(self.consumer_logger, {'user_id': self.user.id})
            elif self.is_vendor(self.user.user_type_id):
                logger = logging.LoggerAdapter(self.vendor_logger, {'user_id': self.user.id})
        if _type == 'INFO':
            logger.info(message)
        elif _type == 'DEBUG':
            logger.debug(message)
        elif _type == 'ERROR':
            logger.error(message)

    @staticmethod
    def session() -> Session:
        try:
            return get_session()
        except Exception as e:
            logging.getLogger('Dobato Logger').error(f"Error creating DB session: {e}")
            return None
