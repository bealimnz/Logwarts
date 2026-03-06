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


class ErrorOnlyFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        return record.levelno >= logging.ERROR


def test_handler_serializes_log_record_as_json():
    publisher = DummyPublisher()
    handler = MqttHandler(publisher)

    logger = logging.getLogger("test.handler.serialize")
    logger.setLevel(logging.INFO)
    logger.addHandler(handler)
    logger.propagate = False

    logger.info("mensagem com acento: olá")

    assert len(publisher.payloads) == 1
    payload = publisher.payloads[0]
    decoded = json.loads(payload)
    assert decoded["message"] == "mensagem com acento: olá"
    assert decoded["level"] == "INFO"


def test_handler_respects_filter_chain():
    publisher = DummyPublisher()
    handler = MqttHandler(publisher)
    handler.addFilter(ErrorOnlyFilter())

    logger = logging.getLogger("test.handler.filter")
    logger.setLevel(logging.INFO)
    logger.addHandler(handler)
    logger.propagate = False

    logger.info("ignored")
    logger.error("accepted")

    assert len(publisher.payloads) == 1
    decoded = json.loads(publisher.payloads[0])
    assert decoded["message"] == "accepted"
    assert decoded["level"] == "ERROR"


def test_handler_close_requests_shutdown():
    publisher = DummyPublisher()
    handler = MqttHandler(publisher)
    handler.close()

    assert publisher.shutdown_requested is True
