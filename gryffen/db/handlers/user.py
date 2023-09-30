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
from gryffen.security import hashing
from gryffen.logging import logger


oauth2_schema = security.OAuth2PasswordBearer(tokenUrl='/api/token')


async def create_user(
    submission: UserCreationSchema,
    db: AsyncSession,
) -> User:
    """Creates a new user.

    Creates a new user object and adds it to the database.

    Args:
        submission: The user creation schema.
        db: The database session object.

    Returns:
        User: The newly created user object.
    """
    user = User(
        username=submission.email,
        password=hashing(submission.password),
        email=submission.email,
        public_id=str(uuid.uuid4()),
        register_via=submission.register_via,
        external_uid=hashing(submission.external_uid),
        timestamp_created=datetime.utcnow(),
        timestamp_updated=datetime.utcnow(),
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)

    logger.info(f"[{datetime.utcnow()}] User {user.username} created successfully.")
    return user


async def check_user_exist(
    email: str,
    db: AsyncSession
) -> bool:
    """Checks if user exists.

    Args:
        email: The email address to be verified.
        db: The database session object.

    Returns:
        bool: True if user exists, False otherwise.
    """
    stmt = select(User).where(User.email == email)
    result = await db.execute(stmt)
    if result.scalar():
        logger.info(f"[{datetime.utcnow()}] User {email} already exists.")
        return True

    logger.info(f"[{datetime.utcnow()}] User {email} does not exist.")
    return False


async def authenticate_user(
    email: str,
    password: str,
    db: AsyncSession
) -> Optional[User]:
    """Checks password and returns user object.

    Checks if user exists and password matches. If so, returns the user object.
    Otherwise, returns None.

    Note:
        This function is used by the fastapi-jwt-auth library.

    Raises:
        HTTPException: If user does not exist.
        HTTPException: If password does not match.

    Returns:
        User: The user object.
    """
    try:
        usr: User = await get_user_by_email(email, db)
    except HTTPException:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found."
        )

    if usr and verify_password(password, usr.password):
        return usr
    else:
        return None


async def social_authenticate_user(
    email: str,
    uid: str,
    db: AsyncSession
) -> Optional[User]:
    """Third-party authentication function.

    Args:
        email: The user's email address.
        uid: The user's external uid.
        db: The database session.

    Returns:
        The user object.
    """
    try:
        usr: User = await get_user_by_email(email, db)
    except HTTPException:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found."
        )

    if usr and verify_password(uid, usr.external_uid):
        return usr
    else:
        return None


async def get_user_by_token(
    current_user: Dict[str, Any],
    db: AsyncSession
) -> Optional[User]:
    """Fetches user object by token.

    Fetches the user object by the token. If the token is valid, the user object
    is returned. Otherwise, None is returned.

    Args:
        current_user: The current user object.
        db: The database session.

    Returns:
        User: The user object.
    """
    stmt = select(User).where(User.username == current_user.get("username"))
    usr: User = await db.scalar(stmt)
    if usr:
        logger.info(
            f"[{datetime.utcnow()}] User {usr.username} fetched successfully."
        )
        return usr

    logger.info(f"[{datetime.utcnow()}] User {current_user.get('username')} not found.")
    return None


async def get_user_by_email(
    user_email: str,
    db: AsyncSession
) -> Optional[User]:
    """Fetches user object by email.

    Fetches the user object by the email. If the user exists, the user object
    is returned. Otherwise, None is returned.

    Args:
        user_email: The user's email address.
        db: The database session.

    Returns:
        User: The user object.
    """
    stmt = select(User).where(User.email == user_email)
    usr: User = await db.scalar(stmt)
    if usr:
        logger.info(
            f"[{datetime.utcnow()}] User {usr.username} fetched successfully."
        )
        return usr

    return None


async def activate_user(
    activation_code: str,
    db: AsyncSession
) -> tuple:
    """Activates user account.

    Args:
        activation_code: The activation code.
        db: The database session.

    Raises:
        HTTPException: If the activation code is invalid or expired.

    Returns:
        Tuple: Tuple of username, email and access token.
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
    return decoded_token.get("username"), decoded_token.get("email"), access_token


async def promote_user(
    current_user: Dict[str, Any],
    public_id: str,
    db: AsyncSession
) -> bool:
    """Promotes a user

    Args:
        current_user: User who performs this action.
        public_id: The public ID of the user to be promoted.
        db: The database session.

    Raises:
        HTTPException: If the user is not a superuser.

    Returns:
        bool: True if the user is successfully promoted.
    """
    stmt = select(User).where(User.username == current_user.get("username"))

    usr: User = await db.scalar(stmt)
    if not usr.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You're not authorized to promote a user."
        )

    update_stmt = (
        update(User)
        .where(User.public_id == public_id)
        .values(
            is_superuser=True,
            timestamp_updated=datetime.utcnow(),
        )
    )
    await db.execute(update_stmt)
    await db.commit()
    return True


async def create_new_api_key(
    email: str,
    db: AsyncSession
) -> str:
    """Creates API key for a user.

    Args:
        email: The email address of the user.
        db: The database session object.

    Returns:
        The `api_key` for the user.
    """
    stmt = select(User).where(User.email == email)
    current_user: User = await db.scalar(stmt)
    if current_user:
        api_key = create_access_token({
            "id": current_user.id,
            "username": current_user.username,
            "email": current_user.email,
        })
        stmt = (
            update(User)
            .where(User.id == current_user.id)
            .values(
                access_token=api_key,
                timestamp_updated=datetime.utcnow(),
            )
        )
        await db.execute(stmt)
        await db.commit()
    else:
        raise HTTPException(status_code=404, detail="User not found.")
    return api_key


"""Beginning of OAuth methods

This section is enclosed with all OAuth-related methods
"""


async def oauth_get_current_user(
    token: str = Depends(oauth2_schema),
    db: AsyncSession = Depends(get_db_session)
) -> User:
    """Gets current user via OAuth token.

    This method gets the current user via OAuth token. The token is
    verified and the user object is returned.

    Args:
        token: The OAuth token.
        db: The database session object.

    Returns:
        User: The current user.

    Raises:
        HTTPException: If the token is invalid or expired.
    """
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
    """Creates OAuth token for front-end users.

    Args:
        user: The user object.

    Returns:
        The dictionary of access token and refresh token.

    Raises:
        HTTPException: If the user is not found.
    """
    user_obj = UserAuthenticationSchema.model_validate(user)
    refresh_token = jwt.encode(
        user_obj.model_dump(),
        settings.gryffen_security_key,
        settings.access_token_hash_algorithm
    )

    expire = datetime.utcnow() + timedelta(
        minutes=int(settings.oauth_token_duration_minute)
    )
    to_encode = user_obj.model_dump()
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
    refresh_token: str,
    db: AsyncSession
) -> Dict[str, str]:
    """Refreshes the access token via refresh token

    Args:
        refresh_token: The refresh token.
        db: The database session object.

    Returns:
        The dictionary of access token and refresh token.
    """
    payload = jwt.decode(refresh_token, settings.gryffen_security_key, algorithms=["HS256"])
    user: User = await db.scalar(
        select(User).where(User.email == payload.get("email"))
    )
    return await oauth_create_token(user)


"""End of OAuth methods"""
