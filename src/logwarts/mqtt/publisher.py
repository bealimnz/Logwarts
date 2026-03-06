import asyncio
import logging
from asyncio import AbstractEventLoop
from collections import deque
from contextlib import suppress

from gmqtt import Client as MQTTClient
from logwarts.models.config import LogwartsConfig

_logger = logging.getLogger(__name__)


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

        self._loop: AbstractEventLoop | None = None
        self._connected: bool = False
        self._closing: bool = False
        self._queue = deque(maxlen=config.behavior.buffer_size)
        self._flush_task: asyncio.Task | None = None
        self._reconnect_task: asyncio.Task | None = None

        self.client.on_connect = self._on_connect
        self.client.on_disconnect = self._on_disconnect

    # ========================
    # Lifecycle (async)
    # ========================

    async def connect(self) -> None:
        self._loop = asyncio.get_running_loop()
        self._closing = False
        await self._try_connect()

    async def disconnect(self) -> None:
        self._closing = True
        self._cancel_task(self._reconnect_task)
        self._cancel_task(self._flush_task)
        self._reconnect_task = None
        self._flush_task = None

        if self._connected:
            with suppress(Exception):
                await self.client.disconnect()
        self._connected = False

    async def shutdown(self) -> None:
        self._closing = True
        await self._wait_for_drain(timeout=self.config.behavior.drain_timeout)
        await self.disconnect()

    def request_shutdown(self) -> None:
        self._closing = True
        self._cancel_task(self._reconnect_task)
        self._reconnect_task = None

    # ========================
    # Callbacks MQTT
    # ========================

    def _on_connect(self, _client, _flags, _rc, _properties):
        self._capture_running_loop()
        self._connected = True
        self._cancel_task(self._reconnect_task)
        self._reconnect_task = None
        self._start_flush()

    def _on_disconnect(self, _client, _packet, _exc=None):
        self._connected = False
        if not self._closing:
            self._start_reconnect()

    # ========================
    # API usada pelo logging (SYNC SAFE)
    # ========================

    def enqueue_or_publish(self, payload: str) -> None:
        """
        Método seguro para ser chamado por logging.Handler (síncrono).
        Nunca faz await.
        """
        self._enqueue(payload)

        if self._closing:
            return

        if self._connected:
            self._start_flush()
            return

        self._start_reconnect()

    # ========================
    # Internals
    # ========================

    def _enqueue(self, payload: str) -> None:
        self._queue.append(payload)

    async def _try_connect(self) -> None:
        try:
            await self.client.connect(
                host=self.config.broker.host,
                port=self.config.broker.port,
                ssl=self.config.broker.tls,
            )
        except Exception:
            self._connected = False
            _logger.warning(
                "Failed to connect to MQTT broker host=%s port=%s tls=%s",
                self.config.broker.host,
                self.config.broker.port,
                self.config.broker.tls,
                exc_info=True,
            )
            if not self._closing:
                self._start_reconnect()

    def _start_flush(self) -> None:
        self._run_on_loop(self._start_flush_on_loop)

    def _start_reconnect(self) -> None:
        self._run_on_loop(self._start_reconnect_on_loop)

    def _start_flush_on_loop(self) -> None:
        if self._flush_task and not self._flush_task.done():
            return
        self._flush_task = asyncio.create_task(self._flush_queue())

    def _start_reconnect_on_loop(self) -> None:
        if self._closing:
            return
        if self._reconnect_task and not self._reconnect_task.done():
            return
        self._reconnect_task = asyncio.create_task(self._reconnect_loop())

    def _cancel_task(self, task: asyncio.Task | None) -> None:
        if task and not task.done():
            if self._in_loop_thread():
                task.cancel()
                return
            if self._loop and self._loop.is_running():
                self._loop.call_soon_threadsafe(task.cancel)

    def _capture_running_loop(self) -> None:
        try:
            self._loop = asyncio.get_running_loop()
        except RuntimeError:
            pass

    def _in_loop_thread(self) -> bool:
        if self._loop is None:
            return False
        try:
            return asyncio.get_running_loop() is self._loop
        except RuntimeError:
            return False

    def _run_on_loop(self, callback) -> None:
        self._capture_running_loop()
        if self._loop is None or self._loop.is_closed():
            return
        if self._in_loop_thread():
            callback()
            return
        self._loop.call_soon_threadsafe(callback)

    async def _reconnect_loop(self) -> None:
        while not self._closing and not self._connected:
            await asyncio.sleep(self.config.behavior.reconnect_interval)
            await self._try_connect()

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
                self._connected = False
                _logger.warning("Failed to publish MQTT log payload; requeueing and scheduling reconnect", exc_info=True)
                self._start_reconnect()
                break
            await asyncio.sleep(0)

    async def _wait_for_drain(self, timeout: float) -> None:
        if not self._connected:
            return

        if self._queue:
            self._start_flush()

        deadline = asyncio.get_running_loop().time() + max(timeout, 0.0)
        while self._queue and self._connected:
            if asyncio.get_running_loop().time() >= deadline:
                break
            await asyncio.sleep(0.01)
