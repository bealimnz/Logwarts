import asyncio

from logwarts.models.config import BehaviorConfig, BrokerConfig, LogwartsConfig, PublishConfig
from logwarts.mqtt.publisher import MqttPublisher


class FakeClient:
    def __init__(self, _client_id: str):
        self.published = []
        self.disconnected = False
        self.connect_calls = 0
        self.fail_connect_times = 0
        self.fail_publish = False
        self.on_connect = None
        self.on_disconnect = None

    async def connect(self, host: str, port: int, ssl: bool) -> None:
        _ = (host, port, ssl)
        self.connect_calls += 1
        if self.fail_connect_times > 0:
            self.fail_connect_times -= 1
            raise RuntimeError("connect failed")
        if self.on_connect:
            self.on_connect(self, None, 0, None)

    async def disconnect(self) -> None:
        self.disconnected = True
        if self.on_disconnect:
            self.on_disconnect(self, None, None)

    def publish(self, topic: str, payload: str, qos: int, retain: bool) -> None:
        if self.fail_publish:
            raise RuntimeError("publish failed")
        self.published.append((topic, payload, qos, retain))


def make_config(*, reconnect_interval: float = 0.01, drain_timeout: float = 0.05) -> LogwartsConfig:
    return LogwartsConfig(
        broker=BrokerConfig(host="localhost", port=1883, tls=False),
        publish=PublishConfig(topic="logwarts/test", qos=1, retain=False),
        behavior=BehaviorConfig(
            buffer_size=2,
            reconnect_interval=reconnect_interval,
            drain_timeout=drain_timeout,
        ),
        client_id="test-client",
    )


def test_enqueue_when_disconnected(monkeypatch):
    monkeypatch.setattr("logwarts.mqtt.publisher.MQTTClient", FakeClient)
    publisher = MqttPublisher(make_config())

    publisher.enqueue_or_publish("msg-1")
    publisher.enqueue_or_publish("msg-2")

    assert list(publisher._queue) == ["msg-1", "msg-2"]
    assert publisher.client.published == []


def test_publish_when_connected(monkeypatch):
    monkeypatch.setattr("logwarts.mqtt.publisher.MQTTClient", FakeClient)
    publisher = MqttPublisher(make_config())
    publisher._connected = True

    publisher.enqueue_or_publish("msg-online")

    assert list(publisher._queue) == []
    assert publisher.client.published == [("logwarts/test", "msg-online", 1, False)]


def test_queue_has_max_size(monkeypatch):
    monkeypatch.setattr("logwarts.mqtt.publisher.MQTTClient", FakeClient)
    publisher = MqttPublisher(make_config())

    publisher.enqueue_or_publish("old")
    publisher.enqueue_or_publish("new")
    publisher.enqueue_or_publish("latest")

    assert list(publisher._queue) == ["new", "latest"]


def test_reconnect_attempts_after_initial_connect_failure(monkeypatch):
    async def scenario():
        monkeypatch.setattr("logwarts.mqtt.publisher.MQTTClient", FakeClient)
        publisher = MqttPublisher(make_config(reconnect_interval=0.001))
        publisher.client.fail_connect_times = 1

        await publisher.connect()
        await asyncio.sleep(0.01)

        assert publisher.client.connect_calls >= 2
        assert publisher._connected is True
        await publisher.disconnect()

    asyncio.run(scenario())


def test_shutdown_drains_queue_when_connected(monkeypatch):
    async def scenario():
        monkeypatch.setattr("logwarts.mqtt.publisher.MQTTClient", FakeClient)
        publisher = MqttPublisher(make_config())
        publisher._connected = True
        publisher._queue.append("queued")

        await publisher.shutdown()

        assert publisher.client.published == [("logwarts/test", "queued", 1, False)]
        assert publisher.client.disconnected is True

    asyncio.run(scenario())
