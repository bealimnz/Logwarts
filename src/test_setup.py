import logging

from logwarts.models.config import (
    LogwartsConfig,
    BrokerConfig,
    BehaviorConfig,
    PublishConfig
)
from logwarts.handlers import LogwartsMqttHandler


config = LogwartsConfig(
    broker=BrokerConfig(
        host="broker.hivemq.com",
        port=1883
    ),
    behavior=BehaviorConfig(
        buffer_size=3,
        flush_interval=2.0
    ),
    publish=PublishConfig(
        topic="logwarts/meu_teste"
    )
)

handler = LogwartsMqttHandler(config)

logger = logging.getLogger("AppPrincipal")
logger.setLevel(logging.INFO)
logger.addHandler(handler)

for i in range(6):
    logger.info(f"Log de teste número {i}")

handler.close()
print("Logs enviados. Verifique o broker!")
