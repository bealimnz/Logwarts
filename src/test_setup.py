import json
import logging

from logwarts.handlers import MqttHandler


class DummyPublisher:
    def __init__(self):
        self.payloads = []
        self.shutdown_requested = False

    def enqueue_or_publish(self, payload: str) -> None:
        self.payloads.append(payload)

    def request_shutdown(self) -> None:
        self.shutdown_requested = True


def test_handler_emit_publishes_json_payload():
    publisher = DummyPublisher()
    handler = MqttHandler(publisher)

    logger = logging.getLogger("test_handler_emit_publishes_json_payload")
    logger.setLevel(logging.INFO)
    logger.addHandler(handler)

    logger.info("log de teste")

    assert len(publisher.payloads) == 1
    data = json.loads(publisher.payloads[0])
    assert data["message"] == "log de teste"
    assert data["level"] == "INFO"
    assert data["logger_name"] == "test_handler_emit_publishes_json_payload"


def test_handler_does_not_emit_after_close():
    publisher = DummyPublisher()
    handler = MqttHandler(publisher)
    handler.close()

    logger = logging.getLogger("test_handler_does_not_emit_after_close")
    logger.setLevel(logging.INFO)
    logger.addHandler(handler)

    logger.info("nao deve publicar")
    assert publisher.payloads == []
    assert publisher.shutdown_requested is True
