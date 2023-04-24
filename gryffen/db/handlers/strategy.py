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

"""
This script is used to create DB handler functions for strategy-related actions.

Author: Thomas Lin (ithomaslin@gmail.com | thomas@neat.tw)
Date: 22/04/2023
"""

from typing import Dict
from datetime import datetime
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from gryffen.db.models.users import User
from gryffen.db.models.strategies import Strategy
from gryffen.web.api.v1.strategy.schema import StrategyCreationSchema


async def create_strategy(
    user_id: int,
    submission: StrategyCreationSchema,
    db: AsyncSession,
):
    """
    Writes strategy object into the DB.

    @param user_id: of who owns the strategy
    @param submission: user submission data
    @param db: DB async session
    @return:
    """

    strategy = Strategy(
        symbol=submission.symbol,
        upper_bound=submission.upper_bound,
        lower_bound=submission.lower_bound,
        grid_count=submission.grid_count,
        grid_size=submission.grid_size,
        grid_type=submission.grid_type,
        principal_balance=submission.principal_balance,
        max_drawdown=submission.max_drawdown,
        is_active=True,
        timestamp_created=datetime.utcnow(),
        timestamp_updated=datetime.utcnow(),
        owner_id=user_id,
    )

    db.add(strategy)
    await db.commit()
    await db.refresh(strategy)

    return strategy


async def get_strategies_by_token(
    decoded: Dict,
    db: AsyncSession,
    is_active: bool = True,
):
    """
    Fetch strategies of a user by access token.

    @param decoded:
    @param db:
    @param is_active:
    @return:
    """
    stmt = (
        select(User)
        .where(
            User.username == decoded.get("username")
            and User.strategies.any(Strategy.is_active == is_active),
        )
        .options(
            selectinload(User.strategies),
        )
    )
    user_obj: User = await db.scalar(stmt)
    return user_obj.strategies
