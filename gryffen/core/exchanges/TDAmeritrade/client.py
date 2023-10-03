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

"""TD Ameritrade API Authentication Module"""

import requests
from datetime import datetime, timedelta
from typing import Dict, Any
from sqlalchemy import select
from urllib import parse
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from gryffen.settings import settings
from gryffen.db.models.users import User
from gryffen.db.models.credentials import Credential
from gryffen.core.exchanges.TDAmeritrade.enums import GrantType, TokenType


class TDAmeritrade:

    def __init__(self):
        self.access_token = None
        self.refresh_token = None

    async def validate_token(self, user_id, db: AsyncSession) -> None:
        now = datetime.now()
        cred = await db.execute(
            select(Credential)
            .where(
                Credential.owner_id == user_id,
                Credential.type == TokenType.ACCESS_TOKEN
            )
        )
        assert cred.scalar_one(), "No access token found."
        if cred.scalar_one().expires_at < now:
            await self.refresh_token(user_id, db)

    async def refresh_token(self, user_id, db: AsyncSession) -> Dict[str, Any]:
        """
        Refreshes the access token.
        """
        cred = await db.execute(
            select(Credential)
            .where(
                Credential.owner_id == user_id,
                Credential.type == TokenType.REFRESH_TOKEN
            )
        )
        assert cred.scalar_one(), "No refresh token found."
        response = await self.get_token(GrantType.REFRESH_TOKEN, cred.scalar_one().value)
        assert response.status_code == 200, "Failed to refresh token."
        data = response.json()
        cred.scalar_one().value = data["access_token"]
        cred.scalar_one().expires_at = datetime.now() + timedelta(seconds=data["expires_in"])
        await db.commit()
        return data

    @staticmethod
    async def get_token(grant_type: GrantType, auth_code: str):
        if grant_type == GrantType.AUTH_CODE:
            data = {
                "grant_type": GrantType.AUTH_CODE,
                "access_type": "offline",
                "code": auth_code,
                "client_id": settings.td_ameritrade_api_key,
                "redirect_uri": settings.td_ameritrade_redirect_uri
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
