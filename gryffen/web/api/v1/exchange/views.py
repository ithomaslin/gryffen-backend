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
This script is used to create API routers for exchange-related actions.

Author: Thomas Lin (ithomaslin@gmail.com | thomas@neat.tw)
Date: 22/04/2023
"""

from typing import List
from fastapi import APIRouter
from fastapi import Depends
from fastapi import status
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from sqlalchemy.ext.asyncio import AsyncSession

from gryffen.db.dependencies import get_db_session
from gryffen.db.handlers.exchange import create_exchange
from gryffen.db.handlers.exchange import get_exchanges_by_token
from gryffen.db.handlers.user import get_user_by_token
from gryffen.db.models.exchanges import Exchange
from gryffen.db.models.users import User
from gryffen.security import destruct_token
from gryffen.security import TokenBase
from gryffen.web.api.v1.exchange.schema import ExchangeCreationSchema


# Setting the API router prefix to `/exchange`
router = APIRouter(prefix="/exchange")


@router.get("/")
async def get(
    user_info: TokenBase = Depends(destruct_token),
    db: AsyncSession = Depends(get_db_session),
    status_code: int = status.HTTP_200_OK
) -> JSONResponse:
    """Fetches all exchange brokers.

    Retrieves all exchange brokers for a given user by access token.

    Args:
        user_info: The decoded access token as the TokenBase object.
        db: The database session object, which will be populated by the dependency injection
            method `get_db_session` automatically.
        status_code: The default status_code to be returned when the request is successful.

    Returns:
        JSONResponse: The json object with all the exchanges' info.
    """
    exchanges: List[Exchange] = await get_exchanges_by_token(user_info, db)
    return JSONResponse(
        status_code=status_code,
        content={
            "status": "success",
            "message": "Exchanges fetched successfully.",
            "data": {
                "exchanges": jsonable_encoder(exchanges)
            }
        }
    )


@router.post("/")
async def create(
    request: ExchangeCreationSchema,
    user_info: TokenBase = Depends(destruct_token),
    db: AsyncSession = Depends(get_db_session),
    status_code: int = status.HTTP_201_CREATED,
) -> JSONResponse:
    """Creates an exchange broker.

    Creates an exchange broker for a given user by access token.

    Args:
        request: The exchange creation schema.
        user_info: The decoded access token as the TokenBase object.
        db: The database session object, which will be populated by the dependency injection
            method `get_db_session` automatically.
        status_code: The default status_code to be returned when the request is successful.

    Returns:
        JSONResponse: The json object with the created exchange's info.
    """
    usr: User = await get_user_by_token(user_info, db)
    exchange: Exchange = await create_exchange(
        user_id=usr.id,
        submission=request,
        db=db
    )
    return JSONResponse(
        status_code=status_code,
        content={
            "status": "success",
            "message": "Exchange created successfully.",
            "data": {
                "exchange": jsonable_encoder(exchange)
            }
        }
    )
