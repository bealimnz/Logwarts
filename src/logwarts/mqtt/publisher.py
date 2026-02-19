import asyncio
from collections import deque
from typing import Optional

from gmqtt import Client as MQTTClient
from logwarts.models.config import LogwartsConfig


class MqttPublisher:
    """
    Responsável por:
    - Conectar e desconectar do broker MQTT
    - Publicar mensagens
    - Manter fila em memória quando offline
    """

    def __init__(self, config: LogwartsConfig):
        self.config = config
        self.client = MQTTClient(config.client_id)

        self._connected: bool = False
        self._queue = deque(maxlen=config.behavior.buffer_size)

        self.client.on_connect = self._on_connect
        self.client.on_disconnect = self._on_disconnect

    # ========================
    # Lifecycle (async)
    # ========================

    async def connect(self) -> None:
        try:
            await self.client.connect(
                host=self.config.broker.host,
                port=self.config.broker.port,
                ssl=self.config.broker.tls,
            )
        except Exception:
            # falha inicial não derruba a aplicação
            self._connected = False

    async def disconnect(self) -> None:
        if self._connected:
            await self.client.disconnect()
            self._connected = False

    # ========================
    # Callbacks MQTT
    # ========================

    def _on_connect(self, _client, _flags, _rc, _properties):
        self._connected = True
        asyncio.create_task(self._flush_queue())

    def _on_disconnect(self, _client, _packet, _exc=None):
        self._connected = False

    # ========================
    # API usada pelo logging (SYNC SAFE)
    # ========================

    def enqueue_or_publish(self, payload: str) -> None:
        """
        Método seguro para ser chamado por logging.Handler (síncrono).
        Nunca faz await.
        """
        if not self._connected:
            self._enqueue(payload)
            return

        try:
            self.client.publish(
                self.config.publish.topic,
                payload,
                qos=self.config.publish.qos,
                retain=self.config.publish.retain,
            )
        except Exception:
            self._enqueue(payload)

    # ========================
    # Internals
    # ========================

    def _enqueue(self, payload: str) -> None:
        self._queue.append(payload)

    async def _flush_queue(self) -> None:
        while self._queue and self._connected:
            payload = self._queue.popleft()
            try:
                self.client.publish(
                    self.config.publish.topic,
                    payload,
                    qos=self.config.publish.qos,
                    retain=self.config.publish.retain,
                )
            except Exception:
                # se falhar, devolve para a fila e sai
                self._queue.appendleft(payload)
                break
