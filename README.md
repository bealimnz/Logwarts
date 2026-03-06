# Logwarts

Logwarts é uma biblioteca para enviar eventos de `logging` do Python para um broker MQTT com fila offline em memoria e reconexao automatica.

## Objetivo

- Integrar com o `logging` nativo sem mudar a forma de logar na aplicacao.
- Publicar logs em MQTT de forma resiliente (offline buffer + retry).
- Preservar contexto de observabilidade (`extra_data`, excecoes, metadados de host/processo/thread).

## Requisitos

- Python minimo: `3.12` (projeto configurado com `>=3.12,<4.0`).

## Instalacao

Desenvolvimento com Poetry:

```bash
poetry install
```

Uso com `pip` (quando pacote estiver publicado):

```bash
pip install logwarts
```

## Quickstart

```python
import asyncio
import logging

from logwarts.handlers import MqttHandler
from logwarts.models.config import LogwartsConfig
from logwarts.mqtt.publisher import MqttPublisher


async def main() -> None:
    config = LogwartsConfig.default()
    publisher = MqttPublisher(config)
    await publisher.connect()

    handler = MqttHandler(publisher)
    logger = logging.getLogger("app")
    logger.setLevel(logging.INFO)
    logger.addHandler(handler)
    logger.propagate = False

    logger.info(
        "application started",
        extra={"extra_data": {"service": "payments", "env": "dev", "version": "1.0.0"}},
    )

    await publisher.shutdown()


if __name__ == "__main__":
    asyncio.run(main())
```

## Configuracao

`LogwartsConfig`:

- `broker.host`: host do broker MQTT.
- `broker.port`: porta do broker.
- `broker.tls`: habilita TLS no connect.
- `publish.topic`: topico de publicacao.
- `publish.qos`: QoS (`0`, `1`, `2`).
- `publish.retain`: flag `retain`.
- `behavior.buffer_size`: limite da fila offline em memoria.
- `behavior.reconnect_interval`: intervalo de reconexao (segundos).
- `behavior.drain_timeout`: tempo maximo para tentar drenar fila no shutdown.
- `client_id`: identificador MQTT do cliente.

## Configuracao Avancada

### QoS e retain

```python
from logwarts.models.config import BehaviorConfig, BrokerConfig, LogwartsConfig, PublishConfig

config = LogwartsConfig(
    broker=BrokerConfig(host="mqtt.mycompany.local", port=1883, tls=False),
    publish=PublishConfig(topic="logs/app", qos=1, retain=False),
    behavior=BehaviorConfig(buffer_size=5000, reconnect_interval=2.0, drain_timeout=3.0),
    client_id="app-logger",
)
```

### TLS

Ative TLS com `broker.tls=True` e use a porta TLS do broker (normalmente `8883`):

```python
broker=BrokerConfig(host="mqtt.mycompany.local", port=8883, tls=True)
```

### Auth (usuario/senha)

Na versao atual (`0.1.0`), `username/password` ainda nao estao expostos na API publica de configuracao.  
Se voce precisa de auth agora, o caminho recomendado e estender `MqttPublisher` no seu projeto e aplicar credenciais no cliente `gmqtt` antes do `connect()`.

## Estrutura do Payload (Schema)

Cada `LogRecord` vira um `LogEvent` serializado em JSON:

```json
{
  "message": "application started",
  "level": "INFO",
  "logger_name": "app",
  "timestamp": "2026-03-06T12:00:00.000000",
  "host": "my-host",
  "process_id": 12345,
  "thread_name": "MainThread",
  "extra": {
    "service": "payments",
    "env": "dev",
    "version": "1.0.0"
  },
  "exception": null
}
```

Campos:

- `message`: resultado de `record.getMessage()`.
- `level`: nivel textual (`INFO`, `ERROR`, etc.).
- `logger_name`: nome do logger.
- `timestamp`: ISO8601 derivado de `record.created`.
- `host`: hostname local.
- `process_id`: PID do processo emissor.
- `thread_name`: nome da thread.
- `extra`: vem de `extra={"extra_data": {...}}`.
- `exception`: stacktrace formatada quando houver `exc_info`.

## Exemplos

- CLI publicando logs com campos extras:
  - [cli_publish_logs.py](/home/bea/Documents/Logwarts/examples/cli_publish_logs.py)
- FastAPI/uvicorn capturando logs do servidor e da aplicacao:
  - [fastapi_uvicorn_logs.py](/home/bea/Documents/Logwarts/examples/fastapi_uvicorn_logs.py)
- Configuracao com `logging.config.dictConfig`:
  - [dictconfig_example.py](/home/bea/Documents/Logwarts/examples/dictconfig_example.py)

Execucao rapida:

```bash
conda run -n logwarts python examples/cli_publish_logs.py --host 127.0.0.1 --port 1883 --topic logwarts/cli
conda run -n logwarts uvicorn examples.fastapi_uvicorn_logs:app --host 0.0.0.0 --port 8000
conda run -n logwarts python examples/dictconfig_example.py
```

## Decisoes de Design

`Handler` (`MqttHandler`) vs encapsulador:

- `MqttHandler` e a interface para o ecossistema `logging` do Python.
- `MqttPublisher` isola ciclo de vida MQTT (connect, reconnect, buffer, flush, shutdown).
- Separacao de responsabilidades:
  - codigo da app continua usando `logger.info(...)`;
  - transporte MQTT fica desacoplado e testavel.
- Esse desenho evita um "logger custom" acoplado a framework e preserva compatibilidade com `dictConfig`, filtros e handlers nativos.

## Troubleshooting

- Logs nao aparecem no broker:
  - confira `host`, `port`, `topic`, `tls`;
  - valide conectividade de rede com o broker;
  - confirme se `await publisher.connect()` foi chamado.
- Aplicacao encerra e perde mensagens:
  - finalize com `await publisher.shutdown()` para drenar fila antes de desconectar.
- Muitos logs em modo offline:
  - ajuste `behavior.buffer_size` para sua carga.
- Loop de reconexao muito agressivo:
  - aumente `behavior.reconnect_interval`.
- Campo `extra` vazio:
  - use `extra={"extra_data": {...}}` no `logger.<nivel>()`.
- FastAPI nao captura logs do uvicorn:
  - anexe o handler aos loggers `uvicorn`, `uvicorn.error` e `uvicorn.access`.

## Versionamento e release

SemVer adotado:

- `MAJOR`: quebra de compatibilidade.
- `MINOR`: nova funcionalidade compativel.
- `PATCH`: correcao sem quebra.

Tags de release:

- Sempre `vX.Y.Z` (exemplo: `v0.2.1`).

Changelog:

- Mantido em [CHANGELOG.md](/home/bea/Documents/Logwarts/CHANGELOG.md).
- Novidades entram em `Unreleased` e sao consolidadas no fechamento da versao.

Guia detalhado:

- [RELEASE.md](/home/bea/Documents/Logwarts/RELEASE.md)

Comandos uteis com Poetry:

```bash
poetry check
poetry build
poetry publish --dry-run --build
```

Scripts utilitarios:

```bash
./scripts/prepare_release.sh patch
./scripts/publish_release.sh pypi --dry-run
./scripts/publish_release.sh internal --dry-run
```

Publicacao em registry interno:

```bash
poetry config repositories.internal "$INTERNAL_PYPI_URL"
poetry config pypi-token.internal "$INTERNAL_PYPI_TOKEN"
poetry publish --build -r internal
```

## Validacao e testes

```bash
conda run -n logwarts pytest -q
conda run -n logwarts ruff check .
```

Teste de integracao opcional com broker local:

```bash
docker run --rm -d --name logwarts-mosquitto -p 1883:1883 eclipse-mosquitto:2
LOGWARTS_RUN_INTEGRATION=1 conda run -n logwarts pytest -q -m integration
```
