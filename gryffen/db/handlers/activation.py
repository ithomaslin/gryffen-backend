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
This script is used to create DB handler functions for activation_code-related actions.

Author: Thomas Lin (ithomaslin@gmail.com | thomas@neat.tw)
Date: 22/04/2023
"""

import jwt
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException
from schema import Schema

from gryffen.db.models.users import User
from gryffen.db.models.activations import Activation
from gryffen.settings import settings


class ActivationCode:

    def __init__(self, user_id=None, username=None, email=None):
        """
        Initializes the activation code class.

        @param user_id:
        @param username:
        @param email:
        """
        self.data = {"user_id": user_id, "username": username, "email": email}
        self.schema = Schema({
            "user_id": int,
            "username": str,
            "email": str,
            "expires": int
        })

    def encode(self, expire_delta: timedelta = timedelta(minutes=15)) -> str:
        """
        Encodes the activation code.

        @param expire_delta:
        @return:
        """
        assert expire_delta >= timedelta(minutes=15)
        to_encode = self.data.copy()
        expire = datetime.utcnow() + expire_delta
        to_encode.update({"expires": int(datetime.timestamp(expire))})
        activation_code = jwt.encode(
            to_encode,
            settings.gryffen_security_key,
            algorithm=settings.access_token_hash_algorithm,
        )
        return activation_code

    def decode(self, code: str) -> Optional[Dict[str, Any]]:
        """
        Decodes the activation code.

        @param code:
        @return:
        """
        try:
            payload = jwt.decode(
                code,
                settings.gryffen_security_key,
                algorithms=settings.access_token_hash_algorithm,
            )
            expires: datetime = datetime.fromtimestamp(payload.get("expires"))
            if datetime.utcnow() >= expires:
                raise HTTPException(
                    status_code=400,
                    detail="Activation code expired."
                )
            elif not self.schema.is_valid(payload):
                raise HTTPException(
                    status_code=400,
                    detail="Credential details unmatched."
                )
        except jwt.PyJWTError:
            raise HTTPException(
                status_code=400,
                detail="Invalid activation code."
            )
        return payload


async def create_activation_code(
    user_id: User.id,
    username: User.username,
    email: User.email,
    db: AsyncSession,
) -> Activation:
    """
    Creates an activation code for the user.

    @param user_id: of the user
    @param username: of the user
    @param email: of the user
    @param db: DB async session
    @return: activation code
    """
    activation_code = ActivationCode(user_id, username, email)

    activation_code = Activation(
        activation_code=activation_code.encode(),
        is_active=True,
        timestamp_created=datetime.utcnow(),
        owner_id=user_id,
    )
    db.add(activation_code)
    await db.commit()
    await db.refresh(activation_code)

    return activation_code


async def verify_activation_code(
    activation_code: str,
    db: AsyncSession,
) -> Dict[str, Any]:
    """
    Verifies the activation code.

    @param activation_code: activation code
    @param db: DB async session
    @return: activation code
    """
    result = (
        await db.execute(
            select(Activation)
            .where(Activation.activation_code == activation_code)
        )
    ).scalar_one_or_none()
    if not result:
        raise HTTPException(status_code=404, detail="Activation code not found.")

    ac = ActivationCode()
    decoded_token = ac.decode(activation_code)

    return decoded_token


async def reissue_activation_code(
    email: str,
    db: AsyncSession,
) -> Activation:
    """
    Reissues an activation code for the user.

    @param email: of the user
    @param db: Async DB session
    @return:
    """
    usr: User = await db.scalar(select(User).where(User.email == email))
    if not usr:
        raise HTTPException(status_code=404, detail="User not found.")

    stmt = (
        update(Activation)
        .where(Activation.owner_id == usr.id)
        .values(is_active=False)
    )
    await db.execute(stmt)
    await db.commit()
    activation_code = await create_activation_code(
        usr.id, usr.username, usr.email, db
    )
    return activation_code
