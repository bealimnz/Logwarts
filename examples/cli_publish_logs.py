import argparse
import asyncio
import logging

from logwarts.handlers import MqttHandler
from logwarts.models.config import BehaviorConfig, BrokerConfig, LogwartsConfig, PublishConfig
from logwarts.mqtt.publisher import MqttPublisher


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Publish logs to MQTT using Logwarts.")
    parser.add_argument("--host", default="127.0.0.1", help="MQTT broker host")
    parser.add_argument("--port", type=int, default=1883, help="MQTT broker port")
    parser.add_argument("--topic", default="logwarts/cli", help="MQTT topic")
    parser.add_argument("--client-id", default="logwarts-cli-example", help="MQTT client id")
    parser.add_argument("--tls", action="store_true", help="Enable TLS")
    return parser


async def main() -> None:
    args = build_parser().parse_args()
    config = LogwartsConfig(
        broker=BrokerConfig(host=args.host, port=args.port, tls=args.tls),
        publish=PublishConfig(topic=args.topic, qos=0, retain=False),
        behavior=BehaviorConfig(buffer_size=100, reconnect_interval=2.0, drain_timeout=1.5),
        client_id=args.client_id,
    )

    publisher = MqttPublisher(config)
    await publisher.connect()

    handler = MqttHandler(publisher)
    logger = logging.getLogger("example.cli")
    logger.setLevel(logging.INFO)
    logger.addHandler(handler)
    logger.propagate = False

    logger.info(
        "CLI started",
        extra={"extra_data": {"component": "cli", "version": "0.1.0", "mode": "example"}},
    )
    logger.warning("Example warning", extra={"extra_data": {"component": "cli", "step": "warning"}})
    logger.error("Example error", extra={"extra_data": {"component": "cli", "step": "error"}})

    await publisher.shutdown()


if __name__ == "__main__":
    asyncio.run(main())
