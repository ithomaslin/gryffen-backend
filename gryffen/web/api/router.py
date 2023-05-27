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
This script is used as the root router of the Gryffen API.

Author: Thomas Lin (ithomaslin@gmail.com | thomas@neat.tw)
Date: 22/04/2023
"""

import jwt
from fastapi.routing import APIRouter
from fastapi import (
    HTTPException, Depends, Form, security, status
)
from typing import Annotated
from sqlalchemy.ext.asyncio import AsyncSession

from gryffen.web.api import docs, echo
from gryffen.web.api.v1 import strategy, user, exchange, credential
from gryffen.db.dependencies import get_db_session
from gryffen.db.models.users import User
from gryffen.db.handlers.user import (
    authenticate_user,
    oauth_create_token,
    oauth_get_current_user,
    oauth_refresh_token,
    check_user_exist,
    create_user,
)
from gryffen.db.handlers.activation import create_activation_code
from gryffen.web.api.v1.user.schema import UserAuthenticationSchema
from gryffen.settings import settings


router = APIRouter()

router.include_router(docs.router)
router.include_router(echo.router, prefix="/echo", tags=["echo"])
router.include_router(user.router, prefix="/v1", tags=["user", "v1"])
router.include_router(strategy.router, prefix="/v1", tags=["strategy", "v1"])
router.include_router(exchange.router, prefix="/v1", tags=["exchange", "v1"])
router.include_router(credential.router, prefix="/v1", tags=["credential", "v1"])


@router.post("/register")
async def register(
    email: Annotated[str, Form()],
    password: Annotated[str, Form()],
    register_via: Annotated[str, Form()],
    db: AsyncSession = Depends(get_db_session)
):
    """

    @param email:
    @param password:
    @param register_via:
    @param db:
    @return:
    """
    submission = {"email": email, "password": password}
    user_exists = await check_user_exist(submission, db)
    if user_exists:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"User email {email} has already been registered."
        )

    usr = await create_user(submission, register_via, db)
    activation_code = await create_activation_code(
        usr.id, usr.username, usr.email, db
    )
    return {
        "status": "success",
        "message": "User created.",
        "data": {
            "user": usr,
            "activation_code": activation_code,
            "info": "Please activate your account within 15 minutes."
        }
    }


@router.post("/token")
async def generate_oauth_token(
    form_data: security.OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db_session)
):
    """

    @param form_data:
    @param db:
    @return:
    """
    usr = await authenticate_user(
        form_data.username, form_data.password, db
    )
    if not usr:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with email {form_data.username} is not found."
        )

    return await oauth_create_token(usr)


@router.get("/me")
async def oauth_get_user(
    usr: UserAuthenticationSchema = Depends(oauth_get_current_user)
):
    """

    @param usr:
    @return:
    """
    return usr


@router.get("/refresh")
async def oauth_refresh(
    refresh_token: str,
    db: AsyncSession = Depends(get_db_session)
):
    """

    @param refresh_token:
    @param db:
    @return:
    """
    return await oauth_refresh_token(refresh_token, db)


@router.get("/logout")
async def logout():
    return {
        "status": "success",
        "message": "You've logged out successfully."
    }
