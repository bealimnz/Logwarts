import asyncio
import logging

from logwarts.models.config import LogwartsConfig
from logwarts.mqtt.publisher import MqttPublisher
from logwarts.handlers import MqttHandler


async def main():
    # Config padrão
    config = LogwartsConfig.default()

    # Publisher (async)
    publisher = MqttPublisher(config)
    await publisher.connect()

    # Handler (SYNC)
    handler = MqttHandler(publisher)

    logger = logging.getLogger("app")
    logger.setLevel(logging.INFO)
    logger.addHandler(handler)

    logger.info("Primeiro log via Logwarts 🚀")
    logger.warning("Segundo log")
    logger.error("Terceiro log")

    # Dá um tempo para o MQTT enviar
    await asyncio.sleep(1)

    await publisher.disconnect()


if __name__ == "__main__":
    asyncio.run(main())
