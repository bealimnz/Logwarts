import asyncio
from logwarts.models.config import LogwartsConfig
from logwarts.mqtt.publisher import MqttPublisher


async def main():
    config = LogwartsConfig.from_dict({
        "broker": {
            "client_id": "logwarts-test-client",
            "host": "broker.hivemq.com",
            "port": 1883,
            "tls": False
        },
        "publish": {
            "topic": "logwarts/test/publisher",
            "qos": 1,
            "retain": False
        },
        "behavior": {
            "buffer_size": 5
        }
    })

    publisher = MqttPublisher(config)

    await publisher.connect()

    for i in range(3):
        await publisher.publish({
            "test": "publisher",
            "counter": i
        })

    await asyncio.sleep(1)

    await publisher.disconnect()
    print("Teste finalizado")


if __name__ == "__main__":
    asyncio.run(main())
