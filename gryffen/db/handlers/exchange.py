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

"""Exchange handlers."""

from typing import Dict
from datetime import datetime
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from gryffen.db.models.users import User
from gryffen.db.models.exchanges import Exchange
from gryffen.web.api.v1.exchange.schema import ExchangeCreationSchema


async def create_exchange(
    user_id: int,
    submission: ExchangeCreationSchema,
    db: AsyncSession,
):
    """
    Writes exchange object into the DB.

    @param user_id:
    @param submission:
    @param db:
    @return:
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
    decoded_token: Dict,
    db: AsyncSession,
    is_active: bool = True,
):
    """
    Retrieves exchange object from the DB by token.
    @param decoded_token:
    @param db:
    @param is_active:
    @return:
    """
    stmt = (
        select(User)
        .where(
            User.username == decoded_token.get("username")
            and User.exchanges.any(Exchange.is_active == is_active)
        )
        .options(selectinload(User.exchanges))
    )
    user_obj: User = await db.scalar(stmt)
    return user_obj.exchanges
