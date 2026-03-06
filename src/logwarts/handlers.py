import json
import logging
from dataclasses import asdict

from logwarts.mqtt.publisher import MqttPublisher
from logwarts.models.log_event import LogEvent


class MqttHandler(logging.Handler):
    """
    Handler de logging síncrono que:
    - Converte LogRecord em LogEvent
    - Serializa para JSON
    - Publica via MqttPublisher
    """

    def __init__(self, publisher: MqttPublisher):
        super().__init__()
        self.publisher = publisher
        self._closed = False

    def emit(self, record: logging.LogRecord) -> None:
        if self._closed:
            return

        try:
            event = LogEvent.from_record(record)
            payload = json.dumps(asdict(event), ensure_ascii=False)
            self.publisher.enqueue_or_publish(payload)
        except Exception:
            self.handleError(record)

    def flush(self) -> None:
        # logging espera método síncrono
        pass

    def close(self) -> None:
        self._closed = True
        self.publisher.request_shutdown()
        super().close()
