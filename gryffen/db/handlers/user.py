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
This script is used to create DB handler functions for user-related actions.

Author: Thomas Lin (ithomaslin@gmail.com | thomas@neat.tw)
Date: 22/04/2023
"""

import uuid
from typing import Dict, Any
from datetime import datetime
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException

from gryffen.db.models.users import User
from gryffen.security import create_access_token
from gryffen.web.api.v1.user.schema import UserCreationSchema


async def create_user(
    submission: UserCreationSchema,
    db: AsyncSession,
):
    """
    User creation DB handler.

    @param submission: UserCreationSchema
    @param db: DB session
    @return: user
    """
    user = User(
        username=submission.username,
        password=submission.password,
        email=submission.email,
        public_id=str(uuid.uuid4()),
        timestamp_created=datetime.utcnow(),
        timestamp_updated=datetime.utcnow(),
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)

    return user


async def check_user_exist(user: UserCreationSchema, db: AsyncSession):
    """
    A pre-check method to verify if a user is already existed.

    @param user:
    @param db:
    @return:
    """
    stmt = select(User).where(
        User.email == user.email or User.username == user.username,
    )
    result = await db.execute(stmt)
    if result.scalar():
        return True
    return False


async def get_user_by_token(current_user: Dict[str, Any], db: AsyncSession):
    """
    Fetch the info of a user by access token.

    @param current_user:
    @param db:
    @return:
    """
    stmt = select(User).where(User.username == current_user.get("username"))
    result: User = await db.scalar(stmt)
    if result:
        return result
    return None


async def activate_user(public_id: str, db: AsyncSession):
    """
    Activate a user.

    @param public_id:
    @param db:
    @return:
    """
    usr: User = await db.scalar(
        select(User).where(User.public_id == public_id),
    )

    if usr:
        stmt = (
            update(User)
            .where(User.public_id == public_id)
            .values(
                access_token=create_access_token(
                    {
                        "id": usr.id,
                        "username": usr.username,
                        "email": usr.email,
                    },
                ),
                is_active=True,
                timestamp_updated=datetime.utcnow(),
            )
        )
        await db.execute(stmt)
        await db.commit()
    else:
        raise HTTPException
    return True


async def promote_user(current_user: Dict[str, Any], public_id: str, db: AsyncSession):
    """
    Promote a user to superuser.

    @param current_user:
    @param public_id:
    @param db:
    @return:
    """
    stmt = (
        update(User)
        .where(
            User.username == current_user.get("username")
            and User.public_id == public_id,
        )
        .values(is_superuser=True, timestamp_updated=datetime.utcnow())
    )
    await db.execute(stmt)
    await db.commit()
    return True
