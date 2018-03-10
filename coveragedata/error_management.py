from pymongo.errors import PyMongoError, OperationFailure
import logging


def mongo_exception_manager(f):

    def wrapper(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except PyMongoError as ex:
            logging.error("PyMongo error: '{}'".format(str(ex)))
            if isinstance(ex, OperationFailure):
                logging.error(ex.details)
                # TODO: store this result somewhere in the db to keep track of it
                # TODO: rollbacks?
            raise ex

    return wrapper
