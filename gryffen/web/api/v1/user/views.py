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
This script is used to create API routers for user-related actions.

Author: Thomas Lin (ithomaslin@gmail.com | thomas@neat.tw)
Date: 22/04/2023
"""

from typing import Any, Dict
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from gryffen.db.dependencies import get_db_session
from gryffen.db.handlers.user import (
    activate_user,
    check_user_exist,
    create_user,
    get_user_by_token,
    promote_user,
)
from gryffen.db.handlers.activation import create_activation_code
from gryffen.db.models.users import User
from gryffen.security import decode_access_token
from gryffen.web.api.v1.user.schema import UserCreationSchema

router = APIRouter(prefix="/user")


@router.post("/register")
async def register(
    request: UserCreationSchema,
    db: AsyncSession = Depends(get_db_session),
):
    """
    API endpoint: user registration.

    @param request: UserCreationSchema
    @param db: DB AsyncSession
    @return:
    """
    valid = await request.is_valid()
    user_exists = await check_user_exist(request, db)
    if user_exists:
        return {"error": "Username or email has been registered."}
    if not valid:
        return {"error": "Input is invalid"}
    user = await create_user(request, db)
    activation_code = await create_activation_code(
        user.id, user.username, user.email, db
    )
    return {
        "user": user,
        "activation_code": activation_code,
        "info": "Please activate your account within 15 minutes."
    }


@router.get("/")
async def get_user(
    current_user: Dict[str, Any] = Depends(decode_access_token),
    db: AsyncSession = Depends(get_db_session),
):
    """
    API endpoint: fetch user info.

    @param current_user:
    @param db:
    @return:
    """
    user: User = await get_user_by_token(current_user, db)
    return {"user": user}


@router.get("/activate/{activation_code}")
async def activate(
    activation_code: str,
    db: AsyncSession = Depends(get_db_session),
):
    """
    API endpoint: activate a given user by access token.

    @param activation_code:
    @param db:
    @return:
    """
    result = await activate_user(activation_code, db)
    return {
        "success": result,
    }


@router.post("/promote/{public_id}")
async def promote(
    public_id: str,
    current_user: Dict[str, Any] = Depends(decode_access_token),
    db: AsyncSession = Depends(get_db_session),
):
    """
    API endpoint: promote a given user to superuser
    by access token.

    @param public_id:
    @param current_user:
    @param db:
    @return:
    """
    result = await promote_user(current_user, public_id, db)
    return {"success": result}
