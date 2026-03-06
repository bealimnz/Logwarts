## Logwarts v0.1.0

Primeira release publica da biblioteca Logwarts para envio de logs Python via MQTT.

### Highlights
- Integracao com `logging` nativo via `MqttHandler`.
- Transporte MQTT assincrono via `MqttPublisher`.
- Buffer offline em memoria com flush ao reconectar.
- Reconexao automatica configuravel.
- Encerramento gracioso com tentativa de dreno de fila (`shutdown`).

### Adicoes
- Suite de testes expandida cobrindo:
  - conversao `LogRecord -> LogEvent`
  - serializacao e filtros no handler
  - comportamento offline/buffer/publicacao com mock de `gmqtt.Client`
  - teste de integracao opcional com broker local
- Exemplos prontos:
  - CLI publicando logs em topico MQTT
  - FastAPI/uvicorn capturando logs do servidor
  - configuracao com `logging.config.dictConfig`
- Documentacao completa:
  - objetivo, instalacao, quickstart
  - configuracao avancada (QoS/retain/TLS)
  - schema de payload
  - troubleshooting
  - decisoes de design
- Fluxo de release e CI:
  - changelog versionado
  - guia de release
  - workflows de CI e release por tag
  - scripts de preparo/publicacao/tag

### Alteracoes tecnicas
- `MqttHandler.close()` passou a sinalizar shutdown do publisher.
- `BehaviorConfig` expandido com:
  - `reconnect_interval`
  - `drain_timeout`
- Metadados e tarefas de build/release ajustados para Poetry.

### Requisitos
- Python `>=3.12,<4.0`

### Instalacao
```bash
pip install logwarts==0.1.0
```

### Artefatos
- Wheel: `logwarts-0.1.0-py3-none-any.whl`
- Source distribution: `logwarts-0.1.0.tar.gz`
