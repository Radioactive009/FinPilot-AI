import logging
import sys
from pathlib import Path
import structlog
from app.core.config import settings


def setup_logging():
    # Enforce directory existence (already handled by config, but safe check)
    log_dir = settings.LOGS_DIR or Path("storage/logs")
    log_dir.mkdir(parents=True, exist_ok=True)
    log_file = log_dir / "app.log"

    # Set up basic handlers
    console_handler = logging.StreamHandler(sys.stdout)
    file_handler = logging.FileHandler(str(log_file))

    logging.basicConfig(
        format="%(message)s",
        level=logging.INFO,
        handlers=[console_handler, file_handler]
    )

    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.processors.JSONRenderer(),
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )


logger = structlog.get_logger()
