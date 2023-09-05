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

from fastapi.routing import APIRouter

from gryffen.web.api import docs, echo
from gryffen.web.api.v1 import (
    user,
    strategy,
    exchange,
    credential
)


router = APIRouter()

router.include_router(docs.router)
router.include_router(echo.router, prefix="/echo", tags=["echo"])
router.include_router(user.router, prefix="/v1", tags=["user", "v1"])
router.include_router(strategy.router, prefix="/v1", tags=["strategy", "v1"])
router.include_router(exchange.router, prefix="/v1", tags=["exchange", "v1"])
router.include_router(credential.router, prefix="/v1", tags=["credential", "v1"])


# @router.get("/refresh")
# async def oauth_refresh(
#     refresh_token: str,
#     db: AsyncSession = Depends(get_db_session)
# ):
#     """
#
#     @param refresh_token:
#     @param db:
#     @return:
#     """
#     return await oauth_refresh_token(refresh_token, db)


@router.get("/logout")
async def logout():
    return {
        "status": "success",
        "message": "You've logged out successfully."
    }
