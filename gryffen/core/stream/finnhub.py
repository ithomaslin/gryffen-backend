import asyncio
import json
import ssl
from asyncio import Queue, Task
from typing import Any

import websocket
from dotenv import load_dotenv

load_dotenv()


class FinnhubWS:
    def __init__(self, stream_data) -> None:
        data = json.loads(stream_data)
        self.signals = []

        self.type = data["type"]
        if self.type == "trade":
            for row in data["data"]:
                d = {
                    "price": row["p"],
                    "timestamp": row["t"],
                    "symbol": row["s"],
                    "volume": row["v"],
                }
                self.signals.append(d)


class FinnhubListener:
    def __init__(self):
        self.subscribers: list[Queue] = []
        self.listener_task: Task = None

    async def subscribe(self, q: Queue):
        self.subscribers.append(q)

    async def receive_message(self, msg: Any):
        for q in self.subscribers:
            try:
                q.put_nowait(str(msg))
            except Exception as e:
                raise e

    async def start_listening(self, conn):
        self.listener_task = asyncio.create_task(self._listener(conn=conn))

    async def _listener(self, conn) -> None:
        while True:
            websocket.enableTrace(False)
            socket = websocket.WebSocketApp(
                url=conn,
                on_message=self.on_message,
                on_error=self.on_error,
                on_close=self.on_close,
            )
            socket.on_open = self.on_open
            socket.run_forever(sslopt={"cert_reqs": ssl.CERT_NONE})

    @staticmethod
    def on_open(socket):
        socket.send('{"type":"subscribe","symbol":"BINANCE:BTCUSDT"}')

    @staticmethod
    async def on_message(socket, message):
        socket_data = FinnhubWS(message)
        if socket_data.signals:
            for signal in socket_data.signals:
                print(signal.get("price"))

    @staticmethod
    def on_error(socket, error):
        print(error)

    @staticmethod
    def on_close(socket):
        print("### connection closed ###")
