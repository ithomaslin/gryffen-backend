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

"""
This script is used to create API routers for user-related actions.

Author: Thomas Lin (ithomaslin@gmail.com | thomas@neat.tw)
Date: 22/04/2023
"""

from fastapi import APIRouter
from fastapi import Depends
from fastapi import Form
from fastapi import HTTPException
from fastapi import status
from fastapi import security
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from sqlalchemy.ext.asyncio import AsyncSession
from gryffen.db.dependencies import get_db_session
from gryffen.db.handlers.activation import create_activation_code
from gryffen.db.handlers.activation import reissue_activation_code
from gryffen.db.handlers.user import authenticate_user
from gryffen.db.handlers.user import activate_user
from gryffen.db.handlers.user import check_user_exist
from gryffen.db.handlers.user import create_user
from gryffen.db.handlers.user import get_user_by_token
from gryffen.db.handlers.user import promote_user
from gryffen.db.handlers.user import create_new_api_key
from gryffen.db.handlers.user import social_authenticate_user
from gryffen.db.handlers.user import oauth_get_current_user
from gryffen.db.handlers.user import oauth_create_token
from gryffen.db.handlers.user import oauth_refresh_token
from gryffen.db.models.users import User
from gryffen.web.api.v1.user.schema import UserCreationSchema
from gryffen.web.api.v1.user.schema import UserAuthenticationSchema
from gryffen.web.api.utils import GriffinMailService
from gryffen.web.api.utils import private_method
from gryffen.security import destruct_token
from gryffen.security import TokenBase


router = APIRouter(prefix="/user")


@private_method
@router.post("/create", include_in_schema=False)
async def create_user_via_json(
    request: UserCreationSchema,
    db: AsyncSession = Depends(get_db_session),
    status_code: int = status.HTTP_201_CREATED,
):
    """Creates user (via application/json)

    Creates a new user and sends an activation code to the user's email.

    Args:
        request: The request schema for creating a new user, request body should contain
            the following fields:
                - email
                - password
                - register_via
                - external_uid
                - first_name
                - last_name
        db: The database session object, which will be populated by the dependency injection
            method `get_db_session` automatically.
        status_code: The default status_code to be returned when the request is successful.

    Returns:
        A JSONResponse object with the following fields:
            - status: The status of the request.
            - message: The message of the request.
            - data: The data of the request.
    """
    valid = await request.is_valid()
    user_exists = await check_user_exist(request.email, db)
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

    user: User = await create_user(request, db)
    activation_code: str = await create_activation_code(
        user.public_id, user.id, user.email, db
    )

    service = GriffinMailService()
    service.send(
        to=user.email,
        code=activation_code
    )

    return JSONResponse(
        status_code=status_code,
        content={
            "status": "success",
            "message": "User created.",
            "data": {
                "user": jsonable_encoder(user),
                "activation_code": activation_code,
                "info": "Please activate your account within 15 minutes."
            }
        }
    )


@private_method
@router.post("/create/form", include_in_schema=False)
async def create_user_via_form(
    email: str = Form(...),
    password: str = Form(...),
    register_via: str = Form(...),
    db: AsyncSession = Depends(get_db_session),
    status_code: int = status.HTTP_201_CREATED,
):
    """Creates user (via Form)

    Creates a new user and sends an activation code to the user's email.

    Args:
        email: The email address of the user.
        password: The user defined password.
        register_via: The middleware used to register the user.
        db: The database session object, which will be populated by the dependency injection
            method `get_db_session` automatically.
        status_code: The default status_code to be returned when the request is successful.

    Returns:
        A JSONResponse object with the following fields:
            status: The status of the request.
            message: The message of the request.
            data: The data of the request.
    """
    submission = UserCreationSchema(
        email=email, password=password, register_via=register_via
    )
    user_exists = await check_user_exist(email, db)
    if user_exists:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Your email {email} has already been registered."
        )

    usr: User = await create_user(submission, db)
    activation_code: str = await create_activation_code(
        usr.id, usr.username, usr.email, db
    )

    mail_service = GriffinMailService()
    mail_service.send(
        to=usr.email,
        code=activation_code
    )

    return JSONResponse(
        status_code=status_code,
        content={
            "status": "success",
            "message": "User created.",
            "data": {
                "user": jsonable_encoder(usr),
                "activation_code": activation_code,
                "info": "Please activate your account within 15 minutes."
            }
        }
    )


@private_method
@router.post("/token-login", include_in_schema=False)
async def login_for_oauth_token(
    form_data: security.OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db_session),
    status_code: int = status.HTTP_200_OK,
) -> JSONResponse:
    """Logs user in (via OAuth2PasswordRequestForm)

    Authenticates user with email/password pair.

    Args:
        form_data: The HTML form data that contains user's email and password.
        db: The database session object, which will be populated by the dependency injection
            method `get_db_session` automatically.
        status_code: The default status_code to be returned when the request is successful.

    Returns:
        A JSONResponse object with the following fields:
            status: The status of the request.
            message: The message of the request.
            data: The data of the request.
                - user: The user object.
                - token: The access token object.
    """
    try:
        usr: User = await authenticate_user(
            form_data.username, form_data.password, db
        )
    except HTTPException:
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

    token = await oauth_create_token(usr)

    return JSONResponse(
        status_code=status_code,
        content={
            "status": "success",
            "message": "User logged in successfully.",
            "data": {
                "user": jsonable_encoder(usr),
                "token": token,
            }
        }
    )


@private_method
@router.post("/social-login", include_in_schema=False)
async def social_login(
    request: UserAuthenticationSchema,
    db: AsyncSession = Depends(get_db_session),
    status_code: int = status.HTTP_200_OK,
) -> JSONResponse:
    """Logs user in (via third-party OAuth)

    Authenticates the user via third-party OAuth provider. It will create a new access token for the user.
    Finally, it will return the user object and the access token object.

    Args:
        request: The request object that contains the user's email and external UID.
        db: The database session object, which will be populated by the dependency injection
            method `get_db_session` automatically.
        status_code: The default status_code to be returned when the request is successful.

    Returns:
        A JSONResponse object with the following fields:
            status: The status of the request.
            message: The message of the request.
            data: The data of the request.
                - user: The user object.
                - token: The access token object.
    """
    try:
        usr: User = await social_authenticate_user(request.email, request.external_uid, db)
    except HTTPException:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with email {request.email} is not found."
        )

    if not usr.is_active:
        raise HTTPException(
            status_code=status.HTTP_418_IM_A_TEAPOT,
            detail="User is not activated yet, so here's a teapot."
        )

    token = await oauth_create_token(usr)

    return JSONResponse(
        status_code=status_code,
        content={
            "status": "success",
            "message": "User logged in successfully.",
            "data": {
                "user": jsonable_encoder(usr),
                "token": token,
            }
        }
    )


@private_method
@router.get("/oauth-refresh-token", include_in_schema=False)
async def oauth_refresh(
    refresh_token: str,
    db: AsyncSession = Depends(get_db_session),
    status_code: int = status.HTTP_200_OK,
) -> JSONResponse:
    """Refreshes the access token.

    Args:
        refresh_token: The refresh token.
        db: The database session object, which will be populated by the dependency injection
            method `get_db_session` automatically.
        status_code: The default status_code to be returned when the request is successful.

    Returns:
        A JSONResponse object with the following fields:
            status: The status of the request.
            message: The message of the request.
            data: The data of the request.
                - token: The access token object.
    """
    token = await oauth_refresh_token(refresh_token, db)

    return JSONResponse(
        status_code=status_code,
        content={
            "status": "success",
            "message": "Token refreshed successfully.",
            "data": {
                "token": token,
            }
        }
    )


@router.get("/me")
async def get_user(
    user_info: TokenBase = Depends(destruct_token),
    db: AsyncSession = Depends(get_db_session),
    status_code: int = status.HTTP_200_OK,
) -> JSONResponse:
    """Gets user object

    Retrieves user's information.

    Args:
        user_info: The TokenBase object which contains user's info, is retrieved from decoding the access token.
        db: The database session object, which will be populated by the dependency injection
            method `get_db_session` automatically.
        status_code: The default status_code to be returned when the request is successful.

    Returns:
        A JSONResponse object with the following fields:
            status: The status of the request.
            message: The message of the request.
            data: The data of the request.
                - user: The user object.
    """
    usr: User = await get_user_by_token(user_info, db)
    return JSONResponse(
        status_code=status_code,
        content={
            "status": "success",
            "message": "User fetched successfully.",
            "data": {
                "user": jsonable_encoder(usr),
            }
        }
    )


@private_method
@router.get("/oauth/me", include_in_schema=False)
async def oauth_get_user(
    usr: UserAuthenticationSchema = Depends(oauth_get_current_user),
    status_code: int = status.HTTP_200_OK,
) -> JSONResponse:
    """Gets user object.

    Retrieves user's information via OAuth.

    Args:
        usr: The user object that is retrieved from decoding the access token.
        status_code: The default status_code to be returned when the request is successful.

    Returns:
        A JSONResponse object with the following fields:
            status: The status of the request.
            message: The message of the request.
            data: The data of the request.
                |- user: The user object.
    """
    return JSONResponse(
        status_code=status_code,
        content={
            "status": "success",
            "message": "User fetched successfully.",
            "data": {
                "user": jsonable_encoder(usr),
            }
        }
    )


@private_method
@router.get("/reissue-activation-code/{email}", include_in_schema=False)
async def reissue_activation(
    email: str,
    db: AsyncSession = Depends(get_db_session),
    status_code: int = status.HTTP_200_OK,
) -> JSONResponse:
    """Reissues a new activation code

    Generates a new activation code for the user and sends it to the user's email address.

    Args:
        email: The user's email address.
        db: The database session object, which will be populated by the dependency injection
            method `get_db_session` automatically.
        status_code: The default status_code to be returned when the request is successful.

    Returns:
        A JSONResponse object with the following fields:
            status: The status of the request.
            message: The message of the request.
    """
    activation_code = await reissue_activation_code(email, db)
    mail_service = GriffinMailService()
    mail_service.send(
        to=email,
        code=activation_code
    )

    return JSONResponse(
        status_code=status_code,
        content={
            "status": "success",
            "message": "Activation code reissued successfully.",
        }
    )


@private_method
@router.get("/activate/{activation_code}", include_in_schema=False)
async def activate(
    activation_code: str,
    db: AsyncSession = Depends(get_db_session),
    status_code: int = status.HTTP_200_OK,
) -> JSONResponse:
    """Activates user account

    Activates user's account via the activation code.

    Note:
        The activation code is generated by the `reissue_activation_code` method.

    Args:
        activation_code: The activation code.
        db: The database session object, which will be populated by the dependency injection
            method `get_db_session` automatically.
        status_code: The default status_code to be returned when the request is successful.

    Returns:
        A JSONResponse object with the following fields:
            status: The status of the request.
            message: The message of the request.
            data: The data of the request.
                - email: The email of the user.
                - public_id: The public ID of the user.
                - access_token: The access token of the user.
    """
    email, public_id, access_token = await activate_user(activation_code, db)

    return JSONResponse(
        status_code=status_code,
        content={
            "status": "success",
            "message": "User activated successfully.",
            "data": {
                "email": email,
                "public_id": public_id,
                "access_token": access_token,
            }
        }
    )


@private_method
@router.post("/promote/{public_id}", include_in_schema=False)
async def promote(
    public_id: str,
    user_info: TokenBase = Depends(destruct_token),
    db: AsyncSession = Depends(get_db_session),
    status_code: int = status.HTTP_200_OK,
) -> JSONResponse:
    """Promotes a user to superuser.

    Promotes a user to superuser with their public ID; only the users who
    already is a superuser can perform this action.

    Args:
        public_id: The public ID of the user whom to be promoted.
        user_info: The TokenBase object which contains user's info, is retrieved from decoding the access token.
            The current user must be a superuser.
        db: The database session object, which will be populated by the dependency injection
            method `get_db_session` automatically.
        status_code: The default status_code to be returned when the request is successful.

    Returns:
        A JSONResponse object with the following fields:
            status: The status of the request.
            message: The message of the request.
            data: The data of the request.
                - status: The status of the request.
                - message: The message of the request.
    """
    result = await promote_user(user_info, public_id, db)

    return JSONResponse(
        status_code=status_code,
        content={
            "status": "success" if result else "failed",
            "message": "User promoted successfully." if result else "User promotion failed.",
        }
    )


@private_method
@router.get("/new-api-key/{email}", include_in_schema=False)
async def generate_api_key(
    email: str,
    db: AsyncSession = Depends(get_db_session),
    status_code: int = status.HTTP_200_OK,
) -> JSONResponse:
    """Creates new API key.

    Args:
        email: The email of the user.
        db: The database session object, which will be populated by the dependency injection
            method `get_db_session` automatically.
        status_code: The default status_code to be returned when the request is successful.

    Returns:
        A JSONResponse object with the following fields:
            status: The status of the request.
            message: The message of the request.
            data: The data of the request.
                - status: The status of the request.
                - message: The message of the request.
                - data: the `api_key` enclosed in a json object.
    """
    api_key = await create_new_api_key(email, db)

    return JSONResponse(
        status_code=status_code,
        content={
            "status": "success",
            "message": "API key generated successfully.",
            "data": {
                "api_key": api_key
            }
        }
    )


@private_method
@router.get("/has-account/{email}", include_in_schema=False)
async def has_registered(
    email: str,
    db: AsyncSession = Depends(get_db_session),
    status_code: int = status.HTTP_200_OK,
) -> JSONResponse:
    """Checks if a user has registered

    Args:
        email: The user's email address.
        db: The database session object, which will be populated by the dependency injection
            method `get_db_session` automatically.
        status_code: The default status_code to be returned when the request is successful.

    Returns:
        A JSONResponse object with the following fields:
            status: The status of the request.
            message: The message of the request.
            data: The data of the request.
                - status: The status of the request.
                - message: The message of the request.
    """
    exists = await check_user_exist(email, db)
    return JSONResponse(
        status_code=status_code if exists else status.HTTP_404_NOT_FOUND,
        content={
            "status": "success" if exists else "failed",
            "message": "User exists." if exists else "User does not exist.",
        }
    )
