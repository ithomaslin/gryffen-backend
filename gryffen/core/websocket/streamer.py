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
from datetime import datetime
from typing import List, Any, Dict
from sqlalchemy import select, ScalarResult
from sqlalchemy.ext.asyncio import (
    AsyncSession, AsyncEngine, create_async_engine
)

from gryffen.settings import settings
from gryffen.core.websocket.schema import FinnhubWS
from gryffen.db.models.strategies import Strategy
from gryffen.core import strategies
from gryffen.core.strategies import GridStrategy
from gryffen.core.strategies.enum import GridType, StrategyType


class Listener:

    def __init__(self):
        """This is the constructor for the Listener class."""
        self.subscribers: List[str] = []
        self.strategies: ScalarResult or None = None
        self.listener_task: Task or None = None
        self.engine: AsyncEngine or None = None
        self.session: AsyncSession or None = None
        self.strategy_pool: List[Dict[str, Any]] or None = None

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
                    self.strategy_pool.append(
                        {
                            "owner_id": strategy.owner_id,
                            "strategy": GridStrategy(
                                strategy.upper_bound, strategy.lower_bound,
                                strategy.grid_size, strategy.strategy_type,
                                strategy.stop_loss, strategy.trade_amount,
                                strategy.owner_id
                            ),
                        }
                    )
                q = json.dumps({"type": "subscribe", "symbol": strategy.symbol})
                await self.subscribe(q)

    async def subscribe(self, q: str) -> None:
        """
        Adds trading symbols to websocket client list.
        @param q:
        @return: None
        """
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
                    pass

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
