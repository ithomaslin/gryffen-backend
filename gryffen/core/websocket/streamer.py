# -*- encoding: utf-8 -*-
# Copyright (c) 2023, Neat Digital
# All rights reserved.
#
# This file is part of Gryffen.
# See https://neat.tw for further info.
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
from fastapi import HTTPException, status
from typing import List, Any, Dict, Optional, Set
from sqlalchemy import select, ScalarResult
from sqlalchemy.ext.asyncio import (
    AsyncSession, AsyncEngine, create_async_engine
)

from gryffen.settings import settings
from gryffen.core.websocket.schema import FinnhubWS
from gryffen.db.models.strategies import Strategy
from gryffen.core.strategies import GridStrategy, MartingaleStrategy
from gryffen.core.strategies.enum import StrategyType
from gryffen.logging import logger


class Listener:

    def __init__(self):
        """This is the constructor for the Listener class."""
        self.subscribers: Set[str] = set()
        self.strategy_pool: Dict[str, List[Dict[str, Any]]] = {}
        self.strategies: ScalarResult or None = None
        self.listener_task: Task or None = None
        self.engine: AsyncEngine or None = None
        self.session: AsyncSession or None = None
        self.socket: websockets.WebSocketClientProtocol or None = None

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
                if strategy.strategy_type == StrategyType.GRID:
                    _strategy = GridStrategy(
                        symbol=strategy.symbol,
                        upper_bound=strategy.upper_bound,
                        lower_bound=strategy.lower_bound,
                        grid_size=strategy.grid_size,
                        grid_type=strategy.grid_type,
                        max_drawdown=strategy.max_drawdown,
                        owner_id=strategy.owner_id,
                        principal_balance=strategy.principal_balance
                    )
                    await self.subscribe(grid_strategy=_strategy)
                else:
                    _strategy = MartingaleStrategy(
                        symbol=strategy.symbol,
                        upper_bound=strategy.upper_bound,
                        lower_bound=strategy.lower_bound,
                        grid_size=strategy.grid_size,
                        grid_type=strategy.grid_type,
                        max_drawdown=strategy.max_drawdown,
                        owner_id=strategy.owner_id,
                        principal_balance=strategy.principal_balance
                    )
                    await self.subscribe(martingale_strategy=_strategy)
        else:
            # This section is intentionally left blank
            pass

    async def subscribe(
        self,
        grid_strategy: Optional[GridStrategy] = None,
        martingale_strategy: Optional[MartingaleStrategy] = None
    ) -> None:
        """
        Adds trading symbols to websocket client list.
        @param grid_strategy: Grid strategy object
        @param martingale_strategy: Martingale strategy object
        @return: None
        """
        assert grid_strategy or martingale_strategy, \
            "At least one strategy must not be None."

        s = grid_strategy if grid_strategy else martingale_strategy
        for item in self.strategy_pool.get(s.symbol, []):
            if item.get("owner_id") == s.owner_id:
                raise HTTPException(
                    status_code=status.HTTP_406_NOT_ACCEPTABLE,
                    detail=f"Strategy for symbol {s.symbol} already exists."
                )

        strategy_obj = {
            "owner_id": s.owner_id,
            "symbol": s.symbol,
            "timestamp_created": s.created,
            "strategy": s
        }
        self.strategy_pool.setdefault(s.symbol, []).append(strategy_obj)

        # Adding trading symbol to the subscriber list
        # and sorting the list by symbol for faster lookup
        self.subscribers.add(
            json.dumps({"type": "subscribe", "symbol": s.symbol})
        )
        self.subscribers = sorted(self.subscribers, key=lambda x: x["symbol"])

    async def unsubscribe(self, strategy: Strategy) -> None:
        """
        Removes trading symbols from websocket client list.
        @param strategy:
        @return: None
        """
        # Pops out item from the strategy pool
        for item in self.strategy_pool.get(strategy.symbol, []):
            if item.get("owner_id") == strategy.owner_id:
                self.strategy_pool[strategy.symbol].remove(item)
                break

        # Check if the strategy pool still has any items
        # for the symbol
        if not self.strategy_pool.get(strategy.symbol, []):
            self.subscribers.discard(
                json.dumps({"type": "subscribe", "symbol": strategy.symbol})
            )

        # Send unsubscribe message to the websocket client
        q = json.dumps({"type": "unsubscribe", "symbol": strategy.symbol})
        await self.socket.send(q)

    async def start_listening(self) -> None:
        """
        Starts the websocket client.

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
        stmt = (
            select(Strategy)
            .where(Strategy.is_active == 1)
            .distinct(Strategy.symbol)
        )
        return await session.scalars(stmt)
