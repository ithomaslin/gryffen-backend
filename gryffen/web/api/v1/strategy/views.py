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
This script is used to create API routers for strategy-related actions.

Author: Thomas Lin (ithomaslin@gmail.com | thomas@neat.tw)
Date: 22/04/2023
"""

from fastapi import APIRouter, Depends
from typing import Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession

from gryffen.db.dependencies import get_db_session
from gryffen.db.models.strategies import Strategy
from gryffen.db.handlers.strategy import (
    get_strategies_by_token,
    create_strategy,
    deactivate_strategy,
)
from gryffen.web.api.v1.strategy.schema import StrategyCreationSchema
from gryffen.security import destruct_token

router = APIRouter(prefix="/strategy")


@router.get("/")
async def get(
    current_user: Dict[str, Any] = Depends(destruct_token),
    db: AsyncSession = Depends(get_db_session),
):
    """
    API endpoint: fetch all strategies of a given user by access token.

    @param current_user:
    @param db:
    @return:
    """
    strategies: Strategy = await get_strategies_by_token(current_user, db)
    return {
        "status": "success",
        "message": "Strategy fetched successfully.",
        "data": {"strategy": strategies},
    }


@router.post("/create")
async def create(
    request: StrategyCreationSchema,
    current_user: Dict[str, Any] = Depends(destruct_token),
    db: AsyncSession = Depends(get_db_session),
):
    """
    API endpoint: create a new strategy for a given user by access token.

    @param request:
    @param current_user:
    @param db:
    @return:
    """
    strategy = await create_strategy(
        user_id=current_user.get("id"),
        submission=request,
        db=db,
    )
    return {
        "status": "success",
        "message": "Strategy created successfully.",
        "data": {"strategy": strategy},
    }


@router.put("/deactivate/{strategy_id}")
async def deactivate(
    strategy_id: int,
    current_user: Dict[str, Any] = Depends(destruct_token),
    db: AsyncSession = Depends(get_db_session),
):
    """
    API endpoint: deactivate a strategy for a given user by access token.

    @param strategy_id:
    @param current_user:
    @param db:
    @return:
    """
    return await deactivate_strategy(current_user, strategy_id, db)
