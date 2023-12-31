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
from datetime import datetime
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from gryffen.db.models.exchanges import Exchange
from gryffen.db.models.users import User
from gryffen.security import TokenBase
from gryffen.web.api.v1.exchange.schema import ExchangeCreationSchema


async def create_exchange(
    user_id: int,
    submission: ExchangeCreationSchema,
    db: AsyncSession,
) -> Exchange:
    """Creates a new exchange broker.

    Args:
        user_id: The user id.
        submission: The exchange submission.
        db: The database session object.

    Returns:
        The created exchange.
    """
    exchange = Exchange(
        name=submission.name,
        type=submission.type,
        account_id=submission.account_id,
        timestamp_created=datetime.utcnow(),
        timestamp_updated=datetime.utcnow(),
        owner_id=user_id,
    )

    db.add(exchange)
    await db.commit()
    await db.refresh(exchange)

    return exchange


async def get_exchanges_by_token(
    user_info: TokenBase,
    db: AsyncSession,
    is_active: bool = True,
) -> List[Exchange]:
    """Gets exchanges by the TokenBase object.

    Args:
        user_info: The TokenBase object that contains user info.
        db: The database session object.
        is_active: Whether to fetch only active exchanges or not; default to True

    Returns:
        The list of exchanges.
    """
    stmt = (
        select(User)
        .where(
            User.public_id == user_info.public_id
            and User.exchanges.any(Exchange.is_active == is_active)
        )
        .options(selectinload(User.exchanges))
    )
    user_obj: User = await db.scalar(stmt)
    return user_obj.exchanges
