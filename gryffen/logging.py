# Copyright (c) 2023, TradingLab
# All rights reserved.
#
# This file is part of TradingLab.app
# See https://tradinglab.app for further info.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import logging
import sys
from typing import Union

from loguru import logger

from gryffen.settings import settings


class InterceptHandler(logging.Handler):
    """
    Default handler from examples in loguru documentation.

    This handler intercepts all log requests and
    passes them to loguru.

    For more info see:
    https://loguru.readthedocs.io/en/stable/overview.html#entirely-compatible-with-standard-logging
    """

    def emit(self, record: logging.LogRecord) -> None:  # pragma: no cover
        """
        Propagates logs to loguru.

        :param record: record to log.
        """
        try:
            level: Union[str, int] = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        # Find caller from where originated the logged message
        frame, depth = logging.currentframe(), 2
        while frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back  # type: ignore
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(
            level,
            record.getMessage(),
        )


def configure_logging() -> None:  # pragma: no cover
    """Configures logging."""
    intercept_handler = InterceptHandler()

    logging.basicConfig(handlers=[intercept_handler], level=logging.NOTSET)

    for logger_name in logging.root.manager.loggerDict:
        if logger_name.startswith("uvicorn."):
            logging.getLogger(logger_name).handlers = []

    # change handler for default uvicorn logger
    logging.getLogger("uvicorn").handlers = [intercept_handler]
    logging.getLogger("uvicorn.access").handlers = [intercept_handler]

    # set logs output, level and format
    logger.remove()
    logger.add(
        sys.stdout,
        level=settings.log_level.value,
    )
