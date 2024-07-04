from sqlalchemy.orm import sessionmaker, scoped_session

from super_admin.config import DB_URL
from utilities.db_setup import database_factory

Session = database_factory(DB_URL)
scoped = scoped_session(Session)

def get_session():
    """ Get a scoped session # simply gets the scope session and returns it to the
    methods or class where it has been called."""
    return scoped