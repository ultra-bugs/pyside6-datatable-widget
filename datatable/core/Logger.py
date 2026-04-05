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
# This package uses loguru's global logger directly.
# Handler configuration is the host application's responsibility (see core.Logging).
from loguru import logger

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
