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
import typing
import uuid
import jwt
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status, security, Depends

from gryffen.db.models.users import User
from gryffen.db.dependencies import get_db_session
from gryffen.security import create_access_token, verify_password
from gryffen.db.handlers.activation import verify_activation_code
from gryffen.web.api.v1.user.schema import (
    UserCreationSchema, UserAuthenticationSchema
)
from gryffen.settings import settings
from gryffen.logging import logger


oauth2_schema = security.OAuth2PasswordBearer(tokenUrl='/api/token')


async def create_user(
    submission: UserCreationSchema,
    db: AsyncSession,
) -> User:
    """
    User creation DB handler.

    @param submission: UserCreationSchema
    @param db: DB session
    @return: user
    """
    user = User(
        username=submission.email,
        password=submission.password,
        email=submission.email,
        public_id=str(uuid.uuid4()),
        register_via=submission.register_via,
        external_uid=submission.external_uid,
        timestamp_created=datetime.utcnow(),
        timestamp_updated=datetime.utcnow(),
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)

    logger.info(f"[{datetime.utcnow()}] User {user.username} created successfully.")
    return user


async def check_user_exist(
    user: UserCreationSchema,
    db: AsyncSession
) -> bool:
    """
    A pre-check method to verify if a user is already existed.

    @param user:
    @param db:
    @return:
    """
    stmt = select(User).where(User.email == user.email)
    result = await db.execute(stmt)
    if result.scalar():
        logger.info(f"[{datetime.utcnow()}] User {user.email} already exists.")
        return True

    logger.info(f"[{datetime.utcnow()}] User {user.email} does not exist.")
    return False


async def authenticate_user(
    email: str,
    password: str,
    db: AsyncSession
) -> Optional[User]:
    """
    User authenticate function.

    @param email:
    @param password:
    @param db:
    @return:
    """
    response: Dict = await get_user_by_email(email, db)
    if not type(response.get("data")):
        return None

    user = response.get("data")["user"]
    if user and verify_password(password, user.password):
        return user
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Password mismatched."
        )


async def social_authenticate_user(
    email: str,
    uid: str,
    db: AsyncSession
) -> Optional[User]:
    response: Dict = await get_user_by_email(email, db)
    user = response.get("data")["user"]
    if not user:
        return None
    if user and verify_password(uid, user.external_uid):
        return user


async def get_user_by_token(
    current_user: Dict[str, Any],
    db: AsyncSession
) -> Dict[str, Any]:
    """
    Fetch the info of a user by access token.

    @param current_user:
    @param db:
    @return:
    """
    stmt = select(User).where(User.username == current_user.get("username"))
    usr: User = await db.scalar(stmt)
    if usr:
        logger.info(
            f"[{datetime.utcnow()}] User {usr.username} fetched successfully."
        )
        return {
            "status": "success",
            "message": "User fetched successfully.",
            "data": {
                "user": usr,
            },
        }

    logger.info(f"[{datetime.utcnow()}] User {current_user.get('username')} not found.")
    return {
        "status": "failed",
        "message": "User not found.",
        "data": {},
    }


async def get_user_by_email(
    user_email: str,
    db: AsyncSession
) -> Dict[str, Any]:
    """
    Fetch the info of a user by user email.

    @param user_email:
    @param db:
    @return:
    """
    stmt = select(User).where(User.email == user_email)
    usr: User = await db.scalar(stmt)
    if usr:
        logger.info(
            f"[{datetime.utcnow()}] User {usr.username} fetched successfully."
        )
        return {
            "status": "success",
            "message": "User fetched successfully.",
            "data": {
                "user": usr,
            },
        }
    return {
        "status": "failed",
        "message": "User not found.",
        "data": None,
    }


async def activate_user(
    activation_code: str,
    db: AsyncSession
) -> Dict[str, Any]:
    """
    Activate a user.

    @param activation_code:
    @param db:
    @return:
    """
    decoded_token = await verify_activation_code(activation_code, db)
    usr = await db.execute(
        select(User).where(User.id == decoded_token.get("user_id")),
    )

    if usr.scalar():
        access_token = create_access_token(
            {
                "id": decoded_token.get("user_id"),
                "username": decoded_token.get("username"),
                "email": decoded_token.get("email"),
            },
        )
        stmt = (
            update(User)
            .where(User.id == decoded_token.get("user_id"))
            .values(
                access_token=access_token,
                is_active=True,
                timestamp_updated=datetime.utcnow(),
            )
        )
        await db.execute(stmt)
        await db.commit()
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The activation code is invalid or expired."
        )
    return {
        "status": "success",
        "message": "User activated successfully.",
        "data": {
            "username": decoded_token.get("username"),
            "email": decoded_token.get("email"),
            "access_token": access_token,
        }
    }


async def promote_user(
    current_user: Dict[str, Any],
    public_id: str,
    db: AsyncSession
) -> Dict[str, Any]:
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
        .values(
            is_superuser=True,
            timestamp_updated=datetime.utcnow()
        )
    )
    await db.execute(stmt)
    await db.commit()
    return {
        "status": "success",
        "message": "User promoted successfully.",
        "data": {
            "username": current_user.get("username"),
            "public_id": public_id,
        },
    }


async def create_new_api_key(
    email: str,
    db: AsyncSession
) -> Dict[str, Any]:
    """
    Create a new access token for a user.

    @param email:
    @param db:
    @return:
    """
    stmt = select(User).where(User.email == email)
    current_user: User = await db.scalar(stmt)
    if current_user:
        new_token = create_access_token({
            "id": current_user.id,
            "username": current_user.username,
            "email": current_user.email,
        })
        stmt = (
            update(User)
            .where(User.id == current_user.id)
            .values(
                access_token=new_token,
                timestamp_updated=datetime.utcnow(),
            )
        )
        await db.execute(stmt)
        await db.commit()
    else:
        raise HTTPException(status_code=404, detail="User not found.")
    return {
        "status": "success",
        "message": "New access token created successfully.",
        "data": {
            "username": current_user.username,
            "email": current_user.email,
            "access_token": new_token,
        }
    }


"""
*** Beginning of OAuth methods ***

This section is enclosed with all OAuth-related methods
"""


async def oauth_get_current_user(
    token: str = Depends(oauth2_schema),
    db: AsyncSession = Depends(get_db_session)
):
    try:
        payload = jwt.decode(token, settings.gryffen_security_key, algorithms=["HS256"])
        if datetime.fromtimestamp(payload.get("expires")) < datetime.utcnow():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Access token expired."
            )
        user: User = await db.scalar(
            select(User).where(User.email == payload.get("email"))
        )
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unable to authenticate."
        )

    return user


async def oauth_create_token(
    user: User
) -> Dict[str, str]:
    """
    Generate oauth token for user.

    @param user:
    @return:
    """
    user_obj = UserAuthenticationSchema.from_orm(user)
    refresh_token = jwt.encode(
        user_obj.dict(),
        settings.gryffen_security_key,
        settings.access_token_hash_algorithm
    )

    expire = datetime.utcnow() + timedelta(
        minutes=int(settings.oauth_token_duration_minute)
    )
    to_encode = user_obj.dict()
    to_encode.update(expires=int(datetime.timestamp(expire)))
    access_token = jwt.encode(
        to_encode,
        settings.gryffen_security_key,
        settings.access_token_hash_algorithm
    )

    return dict(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=int(settings.oauth_token_duration_minute),
        token_type="bearer"
    )


async def oauth_refresh_token(
    token: str,
    db: AsyncSession
):
    payload = jwt.decode(token, settings.gryffen_security_key, algorithms=["HS256"])
    user: User = await db.scalar(
        select(User).where(User.email == payload.get("email"))
    )
    return await oauth_create_token(user)


"""    End of OAuth methods    """
