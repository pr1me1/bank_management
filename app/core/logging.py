# import json
# import logging
# import sys
# from datetime import datetime
# from pathlib import Path
# from typing import (
#     Any,
#     List,
# )
#
# import structlog
#
# from app.core.configs import settings
#
# logging.getLogger("httpx").setLevel(logging.WARNING)
# logging.getLogger("httpcore").setLevel(logging.WARNING)
#
# logging.getLogger("multipart").setLevel(logging.WARNING)
#
# settings.LOG_DIR.mkdir(parents=True, exist_ok=True)
#
#
# def get_log_file_path() -> Path:
#     env_prefix = settings.ENVIRONMENT.value
#     return settings.LOG_DIR / f"{env_prefix}-{datetime.now().strftime('%Y-%m-%d')}.jsonl"
#
#
# class JsonlFileHandler(logging.Handler):
#     """Custom handler for writing JSONL logs to daily files."""
#
#     def __init__(self, file_path: Path):
#         super().__init__()
#         self.file_path = file_path
#
#     def emit(self, record: logging.LogRecord) -> None:
#         """Emit a record to the JSONL file."""
#         try:
#             log_entry = {
#                 "timestamp": datetime.fromtimestamp(record.created).isoformat(),
#                 "level": record.levelname,
#                 "message": record.getMessage(),
#                 "module": record.module,
#                 "function": record.funcName,
#                 "filename": record.pathname,
#                 "line": record.lineno,
#                 "environment": settings.ENVIRONMENT.value,
#             }
#             if hasattr(record, "extra"):
#                 log_entry.update(record.extra)
#
#             with open(self.file_path, "a", encoding="utf-8") as f:
#                 f.write(json.dumps(log_entry) + "\n")
#         except Exception:
#             self.handleError(record)
#
#     def close(self) -> None:
#         """Close the handler."""
#         super().close()
#
#
# def get_structlog_processors(include_file_info: bool = True) -> List[Any]:
#     processors = [
#         structlog.stdlib.filter_by_level,
#         structlog.stdlib.add_logger_name,
#         structlog.stdlib.add_log_level,
#         structlog.stdlib.PositionalArgumentsFormatter(),
#         structlog.processors.TimeStamper(fmt="iso"),
#         structlog.processors.StackInfoRenderer(),
#         structlog.processors.format_exc_info,
#         structlog.processors.UnicodeDecoder(),
#     ]
#
#     if include_file_info:
#         processors.append(
#             structlog.processors.CallsiteParameterAdder(
#                 {
#                     structlog.processors.CallsiteParameter.FILENAME,
#                     structlog.processors.CallsiteParameter.FUNC_NAME,
#                     structlog.processors.CallsiteParameter.LINENO,
#                     structlog.processors.CallsiteParameter.MODULE,
#                     structlog.processors.CallsiteParameter.PATHNAME,
#                 }
#             )
#         )
#
#     processors.append(lambda _, __, event_dict: {**event_dict, "environment": settings.ENVIRONMENT.value})
#
#     return processors
#
#
# def setup_logging() -> None:
#     file_handler = JsonlFileHandler(get_log_file_path())
#     file_handler.setLevel(settings.LOG_LEVEL)
#
#     console_handler = logging.StreamHandler(sys.stdout)
#     console_handler.setLevel(settings.LOG_LEVEL)
#
#     shared_processors = get_structlog_processors()
#
#     logging.basicConfig(
#         format="%(message)s",
#         level=settings.LOG_LEVEL,
#         handlers=[file_handler, console_handler],
#     )
#
#     if settings.LOG_FORMAT == "console":
#         structlog.configure(
#             processors=[
#                 *shared_processors,
#                 structlog.dev.ConsoleRenderer(),
#             ],
#             wrapper_class=structlog.stdlib.BoundLogger,
#             logger_factory=structlog.stdlib.LoggerFactory(),
#             cache_logger_on_first_use=True,
#         )
#     else:
#         structlog.configure(
#             processors=[
#                 *shared_processors,
#                 structlog.processors.JSONRenderer(),
#             ],
#             wrapper_class=structlog.stdlib.BoundLogger,
#             logger_factory=structlog.stdlib.LoggerFactory(),
#             cache_logger_on_first_use=True,
#         )
#
#
# setup_logging()
#
# logger = structlog.get_logger()
# logger.info(
#     "logging_initialized",
#     environment=settings.ENVIRONMENT.value,
#     log_level=settings.LOG_LEVEL,
#     log_format=settings.LOG_FORMAT,
# )
