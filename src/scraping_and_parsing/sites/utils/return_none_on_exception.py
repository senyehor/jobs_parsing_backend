from functools import wraps
from logging import Logger
from typing import Callable


def return_none_on_exception_and_log(log_message: str, logger: Logger) -> Callable:
    def outer_wrapper(func: Callable):
        @wraps(func)
        def inner_wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                logger.error(log_message, e, exc_info=True)
                return None

        return inner_wrapper

    return outer_wrapper
