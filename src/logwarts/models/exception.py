from pydantic import BaseModel
from typing import Optional

class LogException(BaseModel):
    type: str
    message: str
    stacktrace: Optional[str] = None