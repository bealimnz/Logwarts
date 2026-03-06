import logging

from logwarts.models.config import LogwartsConfig
from logwarts.mqtt.publisher import MqttPublisher
from logwarts.handlers import MqttHandler


def test_default_config_is_usable():
    config = LogwartsConfig.default()
    publisher = MqttPublisher(config)
    handler = MqttHandler(publisher)

    logger = logging.getLogger("test_default_config_is_usable")
    logger.setLevel(logging.INFO)
    logger.addHandler(handler)

    logger.info("mensagem de teste")
    assert len(publisher._queue) == 1
