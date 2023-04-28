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
This script is used to create API routers for credential-related actions.

Author: Thomas Lin (ithomaslin@gmail.com | thomas@neat.tw)
Date: 22/04/2023
"""

from fastapi import APIRouter, Depends
from typing import Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession

from gryffen.db.dependencies import get_db_session
from gryffen.security import decode_access_token
from gryffen.db.models.credentials import Credential


router = APIRouter(prefix="/credential")


@router.get("/")
async def get(
    current_user: Dict[str, Any] = Depends(decode_access_token),
    db: AsyncSession = Depends(get_db_session),
):
    """
    API endpoint: fetch all credentials of a given user by access token.

    @param current_user:
    @param db:
    @return:
    """
    credentials: Credential = await get_credentials_by_token(current_user, db)
    return {"credentials": credentials}
