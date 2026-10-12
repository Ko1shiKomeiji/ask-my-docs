import logging

import structlog
from structlog.processors import CallsiteParameter
from structlog.typing import Processor

from ask_my_docs_api.core.config import Settings


def configure_logging(settings: Settings) -> None:
    shared: list[Processor] = [
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso", utc=True),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.CallsiteParameterAdder(
            {CallsiteParameter.MODULE, CallsiteParameter.FUNC_NAME, CallsiteParameter.LINENO}
        ),
    ]

    renderer: list[Processor]
    if settings.log_json:
        renderer = [
            structlog.processors.format_exc_info,
            structlog.processors.JSONRenderer(),
        ]
    else:
        renderer = [structlog.dev.ConsoleRenderer(colors=True)]

    level = logging.getLevelNamesMapping()[settings.log_level]

    structlog.configure(
        processors=[*shared, *renderer],
        wrapper_class=structlog.make_filtering_bound_logger(level),
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=True,
    )
