import asyncio
import logging
import logging.config

from logwarts.handlers import MqttHandler
from logwarts.models.config import BehaviorConfig, BrokerConfig, LogwartsConfig, PublishConfig
from logwarts.mqtt.publisher import MqttPublisher


async def main() -> None:
    config = LogwartsConfig(
        broker=BrokerConfig(host="127.0.0.1", port=1883, tls=False),
        publish=PublishConfig(topic="logwarts/dictconfig", qos=0, retain=False),
        behavior=BehaviorConfig(buffer_size=200, reconnect_interval=2.0, drain_timeout=1.5),
        client_id="logwarts-dictconfig-example",
    )

    publisher = MqttPublisher(config)
    await publisher.connect()

    def mqtt_handler_factory() -> MqttHandler:
        return MqttHandler(publisher)

    logging.config.dictConfig(
        {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "console": {"format": "%(asctime)s %(levelname)s %(name)s %(message)s"},
            },
            "handlers": {
                "console": {
                    "class": "logging.StreamHandler",
                    "formatter": "console",
                },
                "mqtt": {
                    "()": mqtt_handler_factory,
                    "level": "INFO",
                },
            },
            "loggers": {
                "example.dictconfig": {
                    "handlers": ["console", "mqtt"],
                    "level": "INFO",
                    "propagate": False,
                },
            },
        }
    )

    logger = logging.getLogger("example.dictconfig")
    logger.info(
        "dictConfig logger started",
        extra={"extra_data": {"component": "dictconfig", "feature": "minimal-config"}},
    )
    logger.warning("dictConfig warning", extra={"extra_data": {"component": "dictconfig", "severity": "low"}})

    await publisher.shutdown()


if __name__ == "__main__":
    asyncio.run(main())
