import logging

from utilities.db_getter import get_session


class DynamicUserFilter(logging.Filter):
    def __init__(self):
        super().__init__()

    def filter(self, record):
        record.user_id = getattr(record, 'user_id', None)
        return True


class DbHandler(logging.Handler):
    def __init__(self, session, log_model, user=None):
        logging.Handler.__init__(self)
        self.session = session
        self.log_model = log_model
        if user:
            self.user_id = user.id
        else:
            self.user_id = 0 # 0 is for the anonymous user

    def emit(self, record):
        log_entry = self.format(record)
        log = self.log_model(level=record.levelname,
                             message=log_entry,
                             user_id=self.user_id)
        self.session.add(log)
        self.session.commit()


def setup_logger(logger_name, log_model, log_level=None):
    logger = logging.getLogger(logger_name)
    if not log_level:
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(log_level)
    session = get_session()
    db_handler = DbHandler(session, log_model)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    db_handler.setFormatter(formatter)
    logger.addHandler(db_handler)
    dynamic_user_filter = DynamicUserFilter()
    logger.addFilter(dynamic_user_filter)
    return logger
