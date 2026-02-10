#                  M""""""""`M            dP
#                  Mmmmmm   .M            88
#                  MMMMP  .MMM  dP    dP  88  .dP   .d8888b.
#                  MMP  .MMMMM  88    88  88888"    88'  `88
#                  M' .MMMMMMM  88.  .88  88  `8b.  88.  .88
#                  M         M  `88888P'  dP   `YP  `88888P'
#                  MMMMMMMMMMM    -*-  Created by Zuko  -*-
#
#                  * * * * * * * * * * * * * * * * * * * * *
#                  * -    - -   F.R.E.E.M.I.N.D   - -    - *
#                  * -  Copyright © 2026 (Z) Programing  - *
#                  *    -  -  All Rights Reserved  -  -    *
#                  * * * * * * * * * * * * * * * * * * * * *

import sys
from functools import wraps

from loguru import logger

if True:
    import better_exceptions

    better_exceptions.hook()
    _original_exception = logger.exception

    @wraps(_original_exception)
    def better_exception_wrapper(*args, **kwargs):
        exc_type, exc_value, tb = sys.exc_info()
        print(exc_type)
        print(exc_value)
        if not isinstance(exc_type, (KeyboardInterrupt, SystemExit)):
            formatted = ''.join(better_exceptions.format_exception(exc_type, exc_value, tb))
            logger.opt(exception=exc_value).error('BetterException Stacktrace:\n{}', formatted)
        return _original_exception(*args, **kwargs)

    logger.exception = better_exception_wrapper


def setupLogging():
    """Setup application logging"""
    logger.remove()
    isHasStdErrHandler = False
    from pathlib import Path
    logDir = Path(__file__).parent.parent
    if True:
        logger.add(
            sys.stderr,
            format='<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <green>T:{thread.name}</green>|<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | <level>{message}</level>',
            level='DEBUG',
        )
        isHasStdErrHandler = True
    logger.add(
        logDir.joinpath('app.log'),
        rotation='1 day',
        retention='7 days',
        compression='zip',
        format='{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | T:{thread} | {name}:{function}:{line} | {message}',
        level='DEBUG',
    )
    logger.add(
        logDir.joinpath('error.log'),
        rotation='1 day',
        retention='30 days',
        compression='zip',
        format='{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | T:{thread} | {name}:{function}:{line} | {message}',
        level='ERROR',
    )
    if not isHasStdErrHandler:
        logger.add(sys.stderr, format='{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | T:{thread} | {name}:{function}:{line} | {message}', level='ERROR')
    return logger


logger = setupLogging()

from contextlib import contextmanager


@contextmanager
def logContext(**kwargs):
    """
    Temporary logging context.
    Usage:
        with logContext(taskId=uuid, userId=123):
            logger.info('Processing')  # Includes taskId and userId
    """
    logger_with_context = logger.bind(**kwargs)
    try:
        yield logger_with_context
    finally:
        pass
