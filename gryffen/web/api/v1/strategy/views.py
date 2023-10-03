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
This script is used to create API routers for strategy-related actions.

Author: Thomas Lin (ithomaslin@gmail.com | thomas@neat.tw)
Date: 22/04/2023
"""

from fastapi import APIRouter
from fastapi import Depends
from fastapi import status
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from gryffen.db.dependencies import get_db_session
from gryffen.db.models.users import User
from gryffen.db.models.strategies import Strategy
from gryffen.db.handlers.user import get_user_by_token
from gryffen.db.handlers.strategy import get_strategies_by_token
from gryffen.db.handlers.strategy import create_strategy
from gryffen.db.handlers.strategy import deactivate_strategy
from gryffen.web.api.v1.strategy.schema import StrategyCreationSchema
from gryffen.security import destruct_token
from gryffen.security import TokenBase


router = APIRouter(prefix="/strategy")


@router.get("/")
async def get(
    user_info: TokenBase = Depends(destruct_token),
    db: AsyncSession = Depends(get_db_session),
    status_code: int = status.HTTP_200_OK
) -> JSONResponse:
    """Gets all strategies of a user.

    Args:
        user_info: The decoded access token as the TokenBase object.
        db: The database session object, which will be populated by the dependency injection
            method `get_db_session` automatically.
        status_code: The default status_code to be returned when the request is successful.

    Returns:
        The JSOResponse of all strategies under a user.
    """
    strategies: List[Strategy] = await get_strategies_by_token(user_info, db)
    return JSONResponse(
        status_code=status_code,
        content={
            "status": "success",
            "message": "Fetches all strategies successfully.",
            "data": {
                "strategies": jsonable_encoder(strategies)
            }
        }
    )


@router.post("/create")
async def create(
    request: StrategyCreationSchema,
    user_info: TokenBase = Depends(destruct_token),
    db: AsyncSession = Depends(get_db_session),
    status_code: int = status.HTTP_200_OK
) -> JSONResponse:
    """Creates a new strategy for a user.

    Args:
        request: The strategy creation schema.
        user_info: The decoded access token as the TokenBase object.
        db: The database session object, which will be populated by the dependency injection
            method `get_db_session` automatically.
        status_code: The default status_code to be returned when the request is successful.

    Returns:
        JSONResponse of strategy object just created.
    """
    usr: User = await get_user_by_token(user_info=user_info, db=db)
    strategy = await create_strategy(
        user_id=usr.id,
        submission=request,
        db=db,
    )
    return JSONResponse(
        status_code=status_code,
        content={
            "status": "success",
            "message": "Strategy created.",
            "data": {
                "strategy": jsonable_encoder(strategy)
            }
        }
    )


@router.put("/deactivate/{strategy_id}")
async def deactivate(
    strategy_id: int,
    user_info: TokenBase = Depends(destruct_token),
    db: AsyncSession = Depends(get_db_session),
    status_code: int = status.HTTP_200_OK
) -> JSONResponse:
    """Deactivates a strategy by its ID.

    Args:
        strategy_id: The ID of the strategy of which to be disabled.
        user_info: The decoded access token as the TokenBase object.
        db: The database session object, which will be populated by the dependency injection
            method `get_db_session` automatically.
        status_code: The default status_code to be returned when the request is successful.

    Returns:
        JSONResponse of strategy object that's just disabled.
    """
    usr: User = await get_user_by_token(user_info=user_info, db=db)
    strategy = await deactivate_strategy(usr.id, strategy_id, db)
    return JSONResponse(
        status_code=status_code,
        content={
            "status": "success",
            "message": f"Successfully disabling strategy with ID: {strategy.id}",
            "data": {
                "strategy": strategy
            }
        }
    )
