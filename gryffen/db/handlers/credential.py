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
This script is used to create DB handler functions for credential-related actions.

Author: Thomas Lin (ithomaslin@gmail.com | thomas@neat.tw)
Date: 22/04/2023
"""

from typing import Dict
from datetime import datetime
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from gryffen.db.models.users import User
from gryffen.db.models.exchanges import Exchange
from gryffen.db.models.credentials import Credential
from gryffen.web.api.v1.credential.schema import CredentialCreationSchema


async def create_credential(
    user_id: User.id,
    submission: CredentialCreationSchema,
    db: AsyncSession,
):
    """
    Writes credential object into the DB.

    @param user_id:
    @param submission:
    @param db:
    @return:
    """
    credential = Credential(
        exchange_id=submission.exchange_id,
        credential=submission.credential,
        type=submission.type,
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
    decoded: Dict,
    db: AsyncSession
):
    """
    Get credential objects by token.

    @param decoded:
    @param db:
    @return:
    """
    stmt = (
        select(User)
        .where(
            User.username == decoded.get("username")
        )
        .options(
            selectinload(User.credentials)
        )
    )
    user_obj: User = await db.scalar(stmt)
    return user_obj.credentials


async def get_credential_by_exchange_id(
    exchange_id: Exchange.id,
    db: AsyncSession
):
    """
    Get credential objects by exchange_id.

    @param exchange_id:
    @param db:
    @return:
    """
    stmt = (
        select(Credential)
        .where(
            Credential.exchange_id == exchange_id
        )
    )
    credential_obj: Credential = await db.scalar(stmt)
    return credential_obj
