from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

from .context import LogContext
from .exception import LogException


class LogEvent(BaseModel):
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    level: str
    logger_name: str
    message: str

    context: LogContext
    exception: Optional[LogException] = None
