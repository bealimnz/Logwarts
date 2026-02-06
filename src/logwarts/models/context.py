from pydantic import BaseModel
from typing import Optional,Dict

class LogContext(BaseModel):
    service: str
    environment: str
    host: Optional[str]=None
    correlation_id: Optional[str]=None
    tags: Optional[Dict[str,str]]=None
