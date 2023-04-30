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
import bisect
import websockets
from asyncio import Task
from typing import List, Any, Dict, Optional
from sqlalchemy import select, ScalarResult
from sqlalchemy.ext.asyncio import (
    AsyncSession, AsyncEngine, create_async_engine
)

from gryffen.settings import settings
from gryffen.core.websocket.schema import FinnhubWS
from gryffen.db.models.strategies import Strategy
from gryffen.core.strategies import GridStrategy, MartingaleStrategy
from gryffen.core.strategies.enum import StrategyType


class Listener:

    def __init__(self):
        """This is the constructor for the Listener class."""
        self.subscribers: List[str] = []
        self.strategy_pool: List[Dict[str, Any]] = []
        self.strategies: ScalarResult or None = None
        self.listener_task: Task or None = None
        self.engine: AsyncEngine or None = None
        self.session: AsyncSession or None = None

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

        # Adding strategy to the strategy pool
        # and sorting the list by symbol for faster future lookup
        s = grid_strategy if grid_strategy else martingale_strategy
        pool_obj = {
            "owner_id": s.owner_id,
            "symbol": s.symbol,
            "timestamp_created": s.created,
            "strategy": s
        }
        self.strategy_pool.append(pool_obj)
        self.strategy_pool = sorted(
            self.strategy_pool, key=lambda x: x["symbol"]
        )

        # Adding trading symbol to the subscriber list
        # and sorting the list by symbol for faster lookup
        self.subscribers.append(
            json.dumps({"type": "subscribe", "symbol": s.symbol})
        )
        self.subscribers = sorted(self.subscribers, key=lambda x: x["symbol"])

    async def unsubscribe(self, strategy: Strategy) -> None:
        """
        Removes trading symbols from websocket client list.
        @param strategy:
        @return: None
        """

        q = json.dumps({"type": "subscribe", "symbol": strategy.symbol})
        self.subscribers.append(q)

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
            while True:
                for subscriber in self.subscribers:
                    await websocket.send(subscriber)
                message = await websocket.recv()
                ws_obj = FinnhubWS(message)
                for signal in ws_obj.signals:
                    print(f'{signal.get("symbol")} - {signal.get("price")}')

    async def _lookup_strategy_pool(self, symbol: str) -> List[Dict[str, Any]]:
        """
        Looks up the strategy pool for the symbol.

        This is a private method that is used to look up the
        strategy pool for the symbol.

        @param symbol: Trading symbol
        @return: Strategy object
        """
        left_index = bisect.bisect_left(
            [s["symbol"] for s in self.strategy_pool], symbol
        )
        right_index = bisect.bisect_left(
            [s["symbol"] for s in self.strategy_pool], symbol
        )
        return self.strategy_pool[left_index:right_index]

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
