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

from datetime import datetime
from fastapi import HTTPException
from fastapi import status
from sqlalchemy import select
from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession
from gryffen.db.models.users import User
from gryffen.db.models.activations import Activation
from gryffen.security import TokenBase


async def create_activation_code(
    public_id: User.public_id,
    user_id: User.id,
    email: User.email,
    db: AsyncSession,
) -> str:
    """Creates an activation code for the user.

    Args:
        public_id: The public ID of a user.
        user_id: The internal user ID.
        email: The email address of a user.
        db: The database session object.

    Returns:
        str: The activation code object.
    """
    tb = TokenBase(email=email, public_id=public_id)
    code = tb.tokenize()

    activation_code = Activation(
        activation_code=code,
        is_active=True,
        timestamp_created=datetime.utcnow(),
        owner_id=user_id,
    )
    db.add(activation_code)
    await db.commit()
    await db.refresh(activation_code)

    return code


async def verify_activation_code(
    activation_code: str,
    db: AsyncSession,
) -> TokenBase:
    """Verifies activation code.

    Args:
        activation_code: The activation code string.
        db: The database session object.

    Returns:
        TokenBase: The TokenBase object.

    Raises:
        HTTPException: If the activation code is not found.
    """
    result = (
        await db.execute(
            select(Activation)
            .where(Activation.activation_code == activation_code)
        )
    ).scalar_one_or_none()
    if not result:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Activation code not found."
        )

    tb = TokenBase(token=activation_code)
    tb.detokenize()

    return tb


async def reissue_activation_code(
    email: str,
    db: AsyncSession,
) -> str:
    """Creates a new activation code.

    Regenerates a new activation code when the old one is expired. Upon creation,
    the old activation code will be marked as inactive.

    Args:
        email: The email address of a user.
        db: The database session object.

    Returns:
        str: The activation code string.
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
        public_id=usr.public_id, user_id=usr.id, email=usr.email, db=db
    )

    return activation_code
