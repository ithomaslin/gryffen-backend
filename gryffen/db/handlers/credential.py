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
from gryffen.security import TokenBase
from gryffen.db.models.users import User
from gryffen.db.models.exchanges import Exchange
from gryffen.db.models.credentials import Credential
from gryffen.web.api.v1.credential.schema import CredentialCreationSchema


async def create_credential(
    user_id: User.id,
    submission: CredentialCreationSchema,
    db: AsyncSession,
) -> Credential:
    """Creates a new credential for a specific exchange under a user.

    Args:
        user_id: The ID of the user.
        submission: The schema object that contains the credential data.
        db: The database session object.

    Returns:
        The created credential.
    """
    credential = Credential(
        exchange_id=submission.exchange_id,
        credential=submission.credential,
        type=submission.type,
        scope=submission.scope,
        expires_at=submission.expires_at,
        timestamp_created=datetime.utcnow(),
        timestamp_updated=datetime.utcnow(),
        owner_id=user_id
    )

    db.add(credential)
    await db.commit()
    await db.refresh(credential)

    return credential


async def get_credentials_by_token(
    user_info: TokenBase,
    db: AsyncSession
) -> List[Credential]:
    """Gets all credentials under a user.

    Args:
        user_info: The TokenBase object that contains user info.
        db: The database session object.

    Returns:
        The list of credentials.
    """
    stmt = (
        select(User)
        .where(User.public_id == user_info.public_id)
        .options(
            selectinload(User.credentials)
        )
    )
    user_obj: User = await db.scalar(stmt)
    return user_obj.credentials


async def get_credential_by_exchange_id(
    exchange_id: Exchange.id,
    db: AsyncSession
) -> Credential:
    """Gets Credential by exchange ID.

    Args:
        exchange_id: The ID of the exchange broker.
        db: The database session object.

    Returns:
        The exchange object.
    """
    stmt = (
        select(Credential)
        .where(Credential.exchange_id == exchange_id)
    )
    credential_obj: Credential = await db.scalar(stmt)
    return credential_obj
