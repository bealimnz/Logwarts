# Changelog

All notable changes to this project will be documented in this file.

The format is based on Keep a Changelog and this project follows Semantic Versioning (SemVer).

## [Unreleased]

### Added
- Dedicated tests for `LogRecord -> LogEvent` conversion, handler serialization/filtering, publisher offline buffer/reconnect, and optional local-broker integration.
- Usage examples for CLI, FastAPI/uvicorn, and `dictConfig`.
- Release automation docs, scripts, and CI/release workflows.

### Changed
- MQTT publisher lifecycle hardened with reconnect loop and graceful shutdown drain.
- `MqttHandler.close()` now signals publisher shutdown.
- Expanded behavior configuration (`reconnect_interval`, `drain_timeout`).

## [0.1.0] - 2026-03-06

### Added
- Initial Logwarts package structure.
- MQTT publishing via `MqttPublisher`.
- Logging integration via `MqttHandler`.
- Basic configuration model and log event model.
