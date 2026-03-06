# Logwarts

Biblioteca de logging para Python com envio de eventos para MQTT.

## Status atual

- Handler síncrono compatível com `logging`.
- Publicador MQTT assíncrono com:
  - buffer em memória para modo offline;
  - flush automático ao reconectar;
  - reconexão automática com intervalo configurável;
  - shutdown com tentativa de drenar a fila.
- Testes e lint passando no ambiente `conda` `logwarts`.

## Instalação (desenvolvimento)

```bash
poetry install
```

## Exemplo de uso

```python
import asyncio
import logging

from logwarts.handlers import MqttHandler
from logwarts.models.config import LogwartsConfig
from logwarts.mqtt.publisher import MqttPublisher


async def main():
    config = LogwartsConfig.default()
    publisher = MqttPublisher(config)
    await publisher.connect()

    handler = MqttHandler(publisher)
    logger = logging.getLogger("app")
    logger.setLevel(logging.INFO)
    logger.addHandler(handler)

    logger.info("evento de teste")
    logger.warning("evento de warning")

    # Encerramento recomendado: drena fila e desconecta.
    await publisher.shutdown()


if __name__ == "__main__":
    asyncio.run(main())
```

## Configuração

`LogwartsConfig`:

- `broker.host`: host do broker MQTT.
- `broker.port`: porta do broker.
- `broker.tls`: habilita TLS.
- `publish.topic`: tópico de publicação.
- `publish.qos`: QoS da publicação.
- `publish.retain`: retain flag.
- `behavior.buffer_size`: tamanho máximo da fila offline.
- `behavior.reconnect_interval`: intervalo entre tentativas de reconexão (segundos).
- `behavior.drain_timeout`: tempo máximo para drenar fila no shutdown (segundos).
- `client_id`: client id MQTT.

## Comandos de validação

```bash
conda run -n logwarts pytest -q
conda run -n logwarts ruff check .
```
