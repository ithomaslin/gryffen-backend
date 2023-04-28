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

"""TD Ameritrade API Authentication Module"""

import requests
from datetime import datetime, timedelta
from typing import Dict, Any
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from gryffen.settings import settings
from gryffen.db.models.users import User
from gryffen.db.models.credentials import Credential
from gryffen.core.exchanges.TDAmeritrade.enums import GrantType, TokenType


def get_tokens(grant_type, auth_code) -> requests.Response:
    if grant_type == GrantType.AUTH_CODE:
        data = {
            "grant_type": GrantType.AUTH_CODE,
            "access_type": "offline",
            "code": auth_code,
            "client_id": settings.td_ameritrade_api_key,
            "redirect_uri": settings.td_ameritrade_redirect_url,
        }
    else:
        data = {
            "grant_type": GrantType.REFRESH_TOKEN,
            "refresh_token": auth_code,
            "client_id": settings.td_ameritrade_api_key,
        }
    return requests.post(
        url=settings.td_ameritrade_auth_url,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        data=data
    )


async def update_access_token(user_id: User.id, db: AsyncSession) -> Dict[str, Any]:
    stmt = (
        select(User)
        .where(
            User.id == user_id
            and User.credentials.any(Credential.type == TokenType.REFRESH_TOKEN)
        )
        .options(
            selectinload(User.credentials),
        )
    )
    user = await db.scalar(stmt)
    refresh_token = user.credentials[0].credential
    response = get_tokens(GrantType.REFRESH_TOKEN, refresh_token)
    now = datetime.now()
    new_date = None
    new_access_token = None

    if response.status_code == 200:
        new_access_token = response.json()
        access_token: Credential = await db.scalar(
            select(Credential)
            .where(
                Credential.owner_id == user_id
                and Credential.type == TokenType.ACCESS_TOKEN
            )
        )
        access_token.credential = new_access_token.get(TokenType.ACCESS_TOKEN)
        access_token.timestamp_created = now
        access_token.expires_at = now + timedelta(
            seconds=new_access_token.get("expires_in")
        )
        await db.commit()
        await db.refresh(access_token)
    return {
        "access_token": new_access_token.get(TokenType.ACCESS_TOKEN),
        "expires_at": new_date,
    }
