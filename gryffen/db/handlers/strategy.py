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

from typing import List
from fastapi import HTTPException
from fastapi import status
from datetime import datetime
from sqlalchemy import select, update
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from gryffen.db.models.users import User
from gryffen.db.models.strategies import Strategy
from gryffen.web.api.v1.strategy.schema import StrategyCreationSchema
from gryffen.security import TokenBase
from gryffen.web.lifetime import global_listener


async def create_strategy(
    user_id: User.id,
    submission: StrategyCreationSchema,
    db: AsyncSession,
) -> Strategy:
    """Creates a new strategy.

    Args:
        user_id: The owner ID whom the strategy belongs to.
        submission: The Strategy creation schema.
        db: The database session object.

    Returns:
        The strategy object.
    """

    strategy = Strategy(
        name=submission.name,
        description=submission.description,
        symbol=submission.symbol,
        risk_level=submission.risk_level,
        risk_tolerance=submission.risk_tolerance,
        principal_balance=submission.principal_balance,
        max_drawdown=submission.max_drawdown,
        is_active=submission.is_active,
        timestamp_created=datetime.utcnow(),
        timestamp_updated=datetime.utcnow(),
        owner_id=user_id,
    )

    db.add(strategy)
    await db.commit()
    await db.refresh(strategy)

    await global_listener.subscribe(strategy=strategy)

    return strategy


async def get_strategies_by_token(
    user_info: TokenBase,
    db: AsyncSession,
    is_active: bool = True,
) -> List[Strategy]:
    """Gets all strategies by access token.

    Args:
        user_info: The TokenBase object which contains user info.
        db: The database session object.
        is_active: Whether to fetch only the strategies that are active or not

    Returns:
        List of strategy objects.
    """
    stmt = (
        select(User)
        .where(
            User.public_id == user_info.public_id
            and User.strategies.any(Strategy.is_active == is_active),
        )
        .options(
            selectinload(User.strategies),
        )
    )
    user_obj: User = await db.scalar(stmt)
    return user_obj.strategies


async def get_strategy_by_id(
    strategy_id: Strategy.id,
    db: AsyncSession
) -> Strategy:
    """Gets strategy by its ID.

    Args:
        strategy_id: The ID of the strategy of which to be fetched.
        db: The database session object.

    Returns:
        The strategy object.
    """

    stmt = (
        select(Strategy)
        .where(Strategy.id == strategy_id)
    )
    strategy_obj: Strategy = await db.scalar(stmt)
    if not strategy_obj:
        raise HTTPException(status_code=404, detail="Strategy not found.")
    return strategy_obj


async def update_strategy(
    user_id: User.id,
    strategy_id: Strategy.id,
    submission: StrategyCreationSchema,
    db: AsyncSession
) -> Strategy:
    """Updates a strategy.

    Args:
        user_id: The owner ID whom the strategy belongs to.
        strategy_id: The ID of the strategy to be updated.
        submission: The Strategy creation schema.
        db: The database session object.

    Returns:
        The strategy object.
    """

    strategy = await get_strategy_by_id(strategy_id, db)

    if strategy.owner_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to update this strategy."
        )

    strategy.name = submission.name
    strategy.description = submission.description
    strategy.symbol = submission.symbol
    strategy.risk_level = submission.risk_level
    strategy.risk_tolerance = submission.risk_tolerance
    strategy.principal_balance = submission.principal_balance
    strategy.max_drawdown = submission.max_drawdown
    strategy.is_active = submission.is_active
    strategy.timestamp_updated = datetime.utcnow()

    await db.commit()
    await db.refresh(strategy)

    return strategy


async def deactivate_strategy(
    user_id: User.id,
    strategy_id: Strategy.id,
    db: AsyncSession,
) -> Strategy:
    """Deactivates a strategy.

    Args:
        user_id: The owner ID.
        strategy_id: The ID of the strategy.
        db: The database session object.

    Returns:
        The Strategy object.
    """
    stmt = (
        update(Strategy)
        .where(Strategy.id == strategy_id and Strategy.owner_id == user_id)
        .values(is_active=False)
    )
    await db.execute(stmt)
    await db.commit()

    strategy = await get_strategy_by_id(strategy_id, db)

    # Unsubscribe the symbol of the strategy to global listener.
    await global_listener.unsubscribe(strategy.symbol)

    return strategy
