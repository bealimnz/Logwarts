import json
import logging

from logwarts.models.log_event import LogEvent


def make_record(
    *,
    message: str = "default-message",
    level: int = logging.INFO,
    extra_data: dict | None = None,
):
    logger = logging.getLogger("test.logevent")
    record = logger.makeRecord(
        name=logger.name,
        level=level,
        fn="test_file.py",
        lno=42,
        msg=message,
        args=(),
        exc_info=None,
    )
    if extra_data is not None:
        record.extra_data = extra_data
    return record


def test_from_record_maps_core_fields_and_extra_data():
    record = make_record(message="hello", level=logging.WARNING, extra_data={"k": "v"})

    event = LogEvent.from_record(record)

    assert event.message == "hello"
    assert event.level == "WARNING"
    assert event.logger_name == "test.logevent"
    assert event.thread_name == record.threadName
    assert event.extra == {"k": "v"}
    assert event.exception is None
    assert event.timestamp.endswith("+00:00")


def test_from_record_formats_exception():
    logger = logging.getLogger("test.logevent.exc")
    try:
        raise ValueError("bad input")
    except ValueError:
        record = logger.makeRecord(
            name=logger.name,
            level=logging.ERROR,
            fn="test_file.py",
            lno=99,
            msg="will fail",
            args=(),
            exc_info=True,
        )
        record.exc_info = __import__("sys").exc_info()

    event = LogEvent.from_record(record)
    assert event.exception is not None
    assert "ValueError" in event.exception
    assert "bad input" in event.exception


def test_to_json_is_serializable():
    record = make_record(message="olá", extra_data={"attempt": 1})
    event = LogEvent.from_record(record)

    payload = event.to_json()
    encoded = json.dumps(payload, ensure_ascii=False)

    assert isinstance(payload, dict)
    assert payload["message"] == "olá"
    assert payload["extra"] == {"attempt": 1}
    assert "olá" in encoded
