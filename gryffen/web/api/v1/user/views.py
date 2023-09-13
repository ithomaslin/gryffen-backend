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
from fastapi import APIRouter, Depends, HTTPException, Form, status, security
from sqlalchemy.ext.asyncio import AsyncSession
from deprecated import deprecated

from gryffen.security import decode_access_token
from gryffen.db.dependencies import get_db_session
from gryffen.web.api.utils import GriffinMailService
from gryffen.web.api.utils import private_method
from gryffen.web.api.v1.user.schema import (
    UserCreationSchema,
    UserAuthenticationSchema
)
from gryffen.db.handlers.activation import (
    create_activation_code,
    reissue_activation_code,
)
from gryffen.db.handlers.user import (
    authenticate_user,
    activate_user,
    check_user_exist,
    create_user,
    get_user_by_token,
    promote_user,
    create_new_api_key,
    social_authenticate_user,
    oauth_get_current_user,
    oauth_create_token,
    oauth_refresh_token,
)


router = APIRouter(prefix="/user")


@router.get("/")
async def user_root_route():
    """
    This route is used to test if the API is working.
    """
    return {"message": "User API is working."}


@private_method
@router.post("/api-registration")
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
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"User email {request.email} has already been registered."
        )
    if not valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid input."
        )

    user = await create_user(request, db)
    activation_code_obj = await create_activation_code(
        user.id, user.username, user.email, db
    )

    service = GriffinMailService()
    service.send(
        to=user.email,
        code=activation_code_obj.activation_code
    )

    return {
        "status": "success",
        "message": "User created.",
        "data": {
            "user": user,
            "activation_code": activation_code_obj,
            "info": "Please activate your account within 15 minutes."
        }
    }


@private_method
@router.post("/form-registration")
async def register(
    email: str = Form(...),
    password: str = Form(...),
    register_via: str = Form(...),
    db: AsyncSession = Depends(get_db_session)
):
    """

    @param email:
    @param password:
    @param register_via:
    @param db:
    @return:
    """
    submission = UserCreationSchema(
        email=email, password=password, register_via=register_via
    )
    user_exists = await check_user_exist(submission, db)
    if user_exists:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Your email {email} has already been registered."
        )

    usr = await create_user(submission, db)
    activation_code = await create_activation_code(
        usr.id, usr.username, usr.email, db
    )

    mail_service = GriffinMailService()
    mail_service.send("test message", activation_code)

    return {
        "status": "success",
        "message": "User created.",
        "data": {
            "user": usr,
            "activation_code": activation_code,
            "info": "Please activate your account within 15 minutes."
        }
    }


@private_method
@router.post("/token-login")
async def login_for_oauth_token(
    form_data: security.OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db_session)
):
    """
    Loging user via oauth token

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

    if usr.register_via == 'google.com':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"User is authenticated via Google Login."
        )

    if not usr.is_active:
        raise HTTPException(
            status_code=status.HTTP_418_IM_A_TEAPOT,
            detail="User is not activated yet, so here's a teapot."
        )

    return await oauth_create_token(usr)


@private_method
@router.post("/social-login")
async def social_login(
    request: UserAuthenticationSchema,
    db: AsyncSession = Depends(get_db_session),
):
    """

    @param request:
    @param db:
    @return:
    """
    user = await social_authenticate_user(request.email, request.external_uid, db)
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_418_IM_A_TEAPOT,
            detail="User is not activated yet, so here's a teapot."
        )
    return await oauth_create_token(user)


@private_method
@router.get("/oauth-refresh-token")
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


@router.get("/me")
async def get_user(
    current_user: Dict[str, Any] = Depends(decode_access_token),
    db: AsyncSession = Depends(get_db_session),
) -> Dict[str, Any]:
    """
    API endpoint: fetch user info.

    @param current_user:
    @param db:
    @return:
    """
    user: Dict[str, Any] = await get_user_by_token(current_user, db)
    return {
        "status": "success",
        "message": "User info fetched.",
        "data": {"user": user}
    }


@private_method
@router.get("/oauth/me")
async def oauth_get_user(
    usr: UserAuthenticationSchema = Depends(oauth_get_current_user)
):
    """

    @param usr:
    @return:
    """
    return usr


@private_method
@router.get("/reissue-activation-code/{email}")
async def reissue_activation(
    email: str,
    db: AsyncSession = Depends(get_db_session)
) -> Dict[str, Any]:
    """
    API endpoint: reissue activation code.

    @param email: of the user
    @param db: DB AsyncSession
    @return:
    """
    access_token = await reissue_activation_code(email, db)
    return {
        "status": "success",
        "message": "Activation code reissued.",
        "data": {"access_token": access_token}
    }


@private_method
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
    return await activate_user(activation_code, db)


@private_method
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
    return await promote_user(current_user, public_id, db)


@private_method
@router.get("/new-api-key/{email}")
async def get_new_api_key(
    email: str,
    db: AsyncSession = Depends(get_db_session)
) -> Dict[str, Any]:
    """
    API endpoint: create a new access token.

    @param email: of the user
    @param db:
    @return:
    """
    return await create_new_api_key(email, db)


@private_method
@router.get("/has-account/{email}")
async def has_registered(
    email: str,
    db: AsyncSession = Depends(get_db_session),
):
    request = UserCreationSchema(email=email, password='')
    return await check_user_exist(request, db)
