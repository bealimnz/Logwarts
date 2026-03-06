from dataclasses import dataclass


# ---------- Subconfigs ----------

@dataclass(frozen=True)
class BrokerConfig:
    host: str
    port: int
    tls: bool = False


@dataclass(frozen=True)
class PublishConfig:
    topic: str
    qos: int = 0
    retain: bool = False


@dataclass(frozen=True)
class BehaviorConfig:
    buffer_size: int = 1000
    reconnect_interval: float = 3.0
    drain_timeout: float = 2.0


# ---------- Main config ----------

@dataclass(frozen=True)
class LogwartsConfig:
    broker: BrokerConfig
    publish: PublishConfig
    behavior: BehaviorConfig
    client_id: str

    @classmethod
    def default(cls) -> "LogwartsConfig":
        return cls(
            broker=BrokerConfig(
                host="broker.hivemq.com",
                port=1883,
                tls=False,
            ),
            publish=PublishConfig(
                topic="logwarts/test",
                qos=0,
                retain=False,
            ),
            behavior=BehaviorConfig(
                buffer_size=1000,
                reconnect_interval=3.0,
                drain_timeout=2.0,
            ),
            client_id="logwarts-client",
        )
