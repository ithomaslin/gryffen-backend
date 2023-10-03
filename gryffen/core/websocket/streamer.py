# Copyright (c) 2023, TradingLab
# All rights reserved.
#
# This file is part of TradingLab.app
# See https://tradinglab.app for further info.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import json
import asyncio
import websockets
from asyncio import Task
from fastapi import HTTPException
from fastapi import status
from pydantic import BaseModel
from typing import List
from typing import Any
from typing import Dict
from typing import Set
from sqlalchemy import select
from sqlalchemy import ScalarResult
from sqlalchemy.exc import OperationalError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.asyncio import AsyncEngine
from sqlalchemy.ext.asyncio import create_async_engine
from gryffen.settings import settings
from gryffen.core.websocket.schema import FinnhubWS
from gryffen.db.models.strategies import Strategy
from gryffen.logging import logger


# class Strategy(BaseModel):
#
#     owner_id: int
#     symbol: str


class Listener:

    def __init__(self):
        """This is the constructor for the Listener class."""
        self.subscribers: Set[str] = set()
        self.strategy_pool: Dict[str, List[Strategy]] = {}
        self.strategies: ScalarResult or None = None
        self.listener_task: Task | None = None
        self.engine: AsyncEngine | None = None
        self.session: AsyncSession | None = None
        self.socket: websockets.WebSocketClientProtocol | None = None

    async def init(self) -> None:
        """
        Initializes the listener.

        This is an async method that is used to initialize the
        subscriber list for the websocket client.

        @return: None
        """
        self.engine = create_async_engine(str(settings.db_url), echo=False)
        self.session = AsyncSession(self.engine)
        self.strategies = await self._get_strategies(self.session)

        if self.strategies:
            # Subscribing to all strategies
            for strategy in self.strategies.fetchall():
                await self.subscribe(strategy=strategy)
        else:
            # This section is intentionally left blank
            pass

    async def subscribe(self, strategy: Strategy) -> bool:

        # First check if the strategy is already subscribed,
        # if yes then return False
        for strategy_pool_item in self.strategy_pool.get(strategy.symbol, []):
            if strategy_pool_item.id == strategy.id:
                return False

        self.strategy_pool.setdefault(strategy.symbol, []).append(strategy)

        # Adds the trading symbol to the subscriber list and sorts the list by
        # symbol alphabetically for faster lookup; the `self.subscribers` is a
        # set data type to prevent duplicates.
        self.subscribers.add(
            json.dumps({
                "type": "subscribe",
                "symbol": strategy.symbol
            })
        )
        self.subscribers = sorted(self.subscribers, key=lambda x: x["symbol"])
        return True

    async def unsubscribe(self, strategy: Strategy) -> None:
        """Unsubscribes the symbol from the source web socket

        Args:
            strategy:

        Returns:

        """
        # Pops out item from the strategy pool
        for strategy_pool_item in self.strategy_pool.get(strategy.symbol, []):
            if strategy_pool_item.id == strategy.id:
                self.strategy_pool[strategy.symbol].remove(strategy_pool_item)
                break

        # If the strategy pool for the specific symbol is empty then
        # unsubscribe the symbol
        if not self.strategy_pool.get(strategy.symbol, []):
            self.subscribers.discard(
                json.dumps({"type": "subscribe", "symbol": strategy.symbol})
            )

        # Send unsubscribe message to the websocket client
        q = json.dumps({"type": "unsubscribe", "symbol": strategy.symbol})
        await self.socket.send(q)

    async def start_listening(self) -> None:
        """Starts the websocket client .

        This function is used to start the websocket client by
        adding the listener task to the async IO task pool.

        @return: None
        """
        self.listener_task = asyncio.create_task(self._listen())

    async def _listen(self) -> None:
        """
        Listens to the websocket client.

        This is an actual websocket listener that listens to the
        websocket and take actions accordingly.

        @return:
        """
        async with websockets.connect(
            f'{settings.finnhub_ws_endpoint}?token={settings.finnhub_api_key}'
        ) as websocket:
            self.socket = websocket
            while True:
                for subscriber in self.subscribers:
                    await websocket.send(subscriber)
                stream = await websocket.recv()
                message = FinnhubWS(stream)
                for signal in message.signals:
                    logger.info(f'{signal.get("symbol")} - {signal.get("price")}')
                    _strategies = await self._lookup_strategy_pool(signal.get("symbol"))
                    for _strategy in _strategies:
                        # TODO: Implement strategy logic
                        pass

    async def _lookup_strategy_pool(self, symbol: str) -> List[Dict[str, Any]]:
        """
        Looks up the strategy pool for the symbol.

        This is a private method that is used to look up the
        strategy pool for the symbol.

        @param symbol: Trading symbol
        @return: Strategy object
        """
        return self.strategy_pool.get(symbol, [])

    @staticmethod
    async def _get_strategies(session: AsyncSession) -> ScalarResult[Any]:
        """
        Gets all active strategies.

        This is a static method that is used to get all active
        strategies from the Gryffen database.

        @param session: DB async session
        @return:
        """
        try:
            stmt = (
                select(Strategy)
                .where(Strategy.is_active == 1)
                .distinct(Strategy.symbol)
            )
            strategies = await session.scalars(stmt)
        except OperationalError:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database connection error."
            )
        return strategies
