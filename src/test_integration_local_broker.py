import asyncio
import os
import socket
import uuid

import pytest

from logwarts.models.config import BehaviorConfig, BrokerConfig, LogwartsConfig, PublishConfig
from logwarts.mqtt.publisher import MqttPublisher

paho_client = pytest.importorskip("paho.mqtt.client")


pytestmark = pytest.mark.integration


def _is_tcp_open(host: str, port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.settimeout(0.2)
        return sock.connect_ex((host, port)) == 0


@pytest.mark.skipif(
    os.getenv("LOGWARTS_RUN_INTEGRATION") != "1",
    reason="Set LOGWARTS_RUN_INTEGRATION=1 to run integration tests.",
)
def test_connect_publish_shutdown_with_local_broker():
    if not _is_tcp_open("127.0.0.1", 1883):
        pytest.skip("No local MQTT broker on 127.0.0.1:1883")

    async def scenario():
        topic = f"logwarts/integration/{uuid.uuid4().hex}"
        received = {"payload": None}
        done = asyncio.Event()
        loop = asyncio.get_running_loop()

        subscriber = paho_client.Client(paho_client.CallbackAPIVersion.VERSION2)

        def on_message(_client, _userdata, message):
            received["payload"] = message.payload.decode()
            loop.call_soon_threadsafe(done.set)

        subscriber.on_message = on_message
        subscriber.connect("127.0.0.1", 1883, 60)
        subscriber.subscribe(topic)
        subscriber.loop_start()

        try:
            config = LogwartsConfig(
                broker=BrokerConfig(host="127.0.0.1", port=1883, tls=False),
                publish=PublishConfig(topic=topic, qos=0, retain=False),
                behavior=BehaviorConfig(buffer_size=5, reconnect_interval=0.1, drain_timeout=0.5),
                client_id="logwarts-integration-client",
            )
            publisher = MqttPublisher(config)
            await publisher.connect()

            deadline = asyncio.get_running_loop().time() + 2.0
            while not publisher._connected and asyncio.get_running_loop().time() < deadline:
                await asyncio.sleep(0.01)
            assert publisher._connected is True

            payload = '{"kind":"integration-test"}'
            publisher.enqueue_or_publish(payload)
            await asyncio.wait_for(done.wait(), timeout=2.0)
            assert received["payload"] == payload

            await publisher.shutdown()
            assert publisher._connected is False
        finally:
            subscriber.loop_stop()
            subscriber.disconnect()

    asyncio.run(scenario())
