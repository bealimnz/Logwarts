# Changelog

Todas as mudanças relevantes deste projeto serão documentadas neste arquivo.

O formato é baseado em [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
e este projeto segue [Versionamento Semântico](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.1] - 2026-03-06

### Changed
- Ajustado o comportamento do publisher para sempre enfileirar primeiro e realizar flush assíncrono no event loop proprietário.

### Fixed
- Reforçada a segurança de loop/thread do publisher MQTT ao agendar reconexão/flush no event loop proprietário.
- Padronizado `LogEvent.timestamp` em UTC tanto na criação padrão quanto no `from_record`.
- Atualizados os testes de publisher/integração para refletir o comportamento assíncrono de fila+flush e validação real de entrega em broker local.

## [0.1.0] - 2026-03-06

### Added
- Estrutura inicial do pacote Logwarts.
- Publicação MQTT via `MqttPublisher` com reforço de ciclo de vida (loop de reconexão e shutdown gracioso).
- Integração com logging via `MqttHandler` (incluindo sinalização em `MqttHandler.close()`).
- Testes dedicados para conversão `LogRecord -> LogEvent` e buffer offline.
- Exemplos de uso para CLI, FastAPI/uvicorn e `dictConfig`.
- Documentação, scripts e workflows de CI/release para automação de releases.
- Modelo de configuração expandido (intervalo de reconexão, timeout de dreno e tamanho de buffer).

---

[0.1.1]: https://github.com/bealimnz/Logwarts/compare/v0.1.0...v0.1.1
[0.1.0]: https://github.com/bealimnz/Logwarts/releases/tag/v0.1.0
