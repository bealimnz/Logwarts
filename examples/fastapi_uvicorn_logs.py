import asyncio
import logging

from fastapi import FastAPI

from logwarts.handlers import MqttHandler
from logwarts.models.config import BehaviorConfig, BrokerConfig, LogwartsConfig, PublishConfig
from logwarts.mqtt.publisher import MqttPublisher


app = FastAPI(title="Logwarts FastAPI Example")

_publisher: MqttPublisher | None = None
_handler: MqttHandler | None = None


def _attach_handler(logger_name: str, handler: MqttHandler) -> None:
    logger = logging.getLogger(logger_name)
    logger.setLevel(logging.INFO)
    if handler not in logger.handlers:
        logger.addHandler(handler)


@app.on_event("startup")
async def startup() -> None:
    global _publisher, _handler
    config = LogwartsConfig(
        broker=BrokerConfig(host="127.0.0.1", port=1883, tls=False),
        publish=PublishConfig(topic="logwarts/fastapi", qos=0, retain=False),
        behavior=BehaviorConfig(buffer_size=500, reconnect_interval=2.0, drain_timeout=1.5),
        client_id="logwarts-fastapi-example",
    )
    _publisher = MqttPublisher(config)
    await _publisher.connect()

    _handler = MqttHandler(_publisher)
    _attach_handler("uvicorn", _handler)
    _attach_handler("uvicorn.error", _handler)
    _attach_handler("uvicorn.access", _handler)
    _attach_handler("app.fastapi", _handler)

    logging.getLogger("app.fastapi").info(
        "FastAPI app started",
        extra={"extra_data": {"component": "fastapi", "phase": "startup"}},
    )


@app.on_event("shutdown")
async def shutdown() -> None:
    if _publisher is not None:
        await _publisher.shutdown()


@app.get("/health")
async def health() -> dict:
    logging.getLogger("app.fastapi").info(
        "health endpoint called",
        extra={"extra_data": {"component": "fastapi", "endpoint": "/health"}},
    )
    await asyncio.sleep(0)
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("examples.fastapi_uvicorn_logs:app", host="0.0.0.0", port=8000, reload=False)
