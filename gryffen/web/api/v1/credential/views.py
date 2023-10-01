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
This script is used to create API routers for credential-related actions.

Author: Thomas Lin (ithomaslin@gmail.com | thomas@neat.tw)
Date: 22/04/2023
"""

from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession

from gryffen.db.dependencies import get_db_session
from gryffen.db.models.users import User
from gryffen.db.models.credentials import Credential
from gryffen.security import TokenBase, destruct_token
from gryffen.db.handlers.user import get_user_by_token
from gryffen.web.api.v1.credential.schema import CredentialCreationSchema
from gryffen.db.handlers.credential import (
    create_credential, get_credentials_by_token
)


router = APIRouter(prefix="/credential")


@router.get("/")
async def get(
    user_info: TokenBase = Depends(destruct_token),
    db: AsyncSession = Depends(get_db_session),
    status_code: int = status.HTTP_200_OK,
) -> JSONResponse:
    """Gets all the credentials associated with a user.

    Args:
        user_info: The decoded access token as the TokenBase object.
        db: The database session object, which will be populated by the dependency injection
            method `get_db_session` automatically.
        status_code: The default status_code to be returned when the request is successful.

    Returns:
        The JSONResponse of the credential objects
    """
    credentials: List[Credential] = await get_credentials_by_token(user_info, db)
    return JSONResponse(
        status_code=status_code,
        content={
            "status": "success",
            "message": "Credentials retrieved successfully.",
            "data": {
                "credentials": jsonable_encoder(credentials)
            }
        }
    )


@router.post("/")
async def create(
    request: CredentialCreationSchema,
    user_info: TokenBase = Depends(destruct_token),
    db: AsyncSession = Depends(get_db_session),
    status_code: int = status.HTTP_201_CREATED,
) -> JSONResponse:
    """Creates a new credential entry and link to an existing exchange.

    Args:
        request: The Credential creation schema.
        user_info: The decoded access token as the TokenBase object.
        db: The database session object, which will be populated by the dependency injection
            method `get_db_session` automatically.
        status_code: The default status_code to be returned when the request is successful.

    Returns:
        The JSONResponse of the credential object that's just created.
    """
    usr: User = await get_user_by_token(user_info, db)
    credential = await create_credential(
        user_id=usr.id,
        submission=request,
        db=db
    )
    return JSONResponse(
        status_code=status_code,
        content={
            "status": "success",
            "message": "Credential created successfully.",
            "data": {
                "credential": jsonable_encoder(credential)
            }
        }
    )
