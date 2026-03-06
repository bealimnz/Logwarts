import datetime
import socket
import os
from dataclasses import dataclass, field, asdict
from typing import Any, Dict, Optional


@dataclass
class LogEvent:
    """Representa a estrutura de um evento de log enviado via MQTT."""
    message: str
    level: str
    logger_name: str
    timestamp: str = field(default_factory=lambda: datetime.datetime.now(datetime.UTC).isoformat())

    host: str = field(default_factory=socket.gethostname)
    process_id: int = field(default_factory=os.getpid)
    thread_name: str = field(default_factory=lambda: "main")  # Atualizado no factory se necessário

    extra: Dict[str, Any] = field(default_factory=dict)
    exception: Optional[str] = None

    @classmethod
    def from_record(cls, record: Any) -> "LogEvent":
        """
        Converte um logging.LogRecord do Python em um LogEvent.
        """
        # Captura de exceção formatada, se existir
        exc_info = None
        if record.exc_info:
            import traceback
            exc_info = "".join(traceback.format_exception(*record.exc_info))

        return cls(
            message=record.getMessage(),
            level=record.levelname,
            logger_name=record.name,
            timestamp=datetime.datetime.fromtimestamp(record.created, tz=datetime.UTC).isoformat(),
            thread_name=record.threadName,
            exception=exc_info,
            extra=getattr(record, "extra_data", {})  # Suporte a dados customizados
        )

    def to_json(self) -> Dict[str, Any]:
        """Converte o evento para um dicionário pronto para serialização JSON."""
        return asdict(self)
