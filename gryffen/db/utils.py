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
This script is used to host all the DB-related utility functions.

Author: Thomas Lin (ithomaslin@gmail.com | thomas@neat.tw)
Date: 22/04/2023
"""

from datetime import date, datetime
from enum import Enum
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

from gryffen.settings import settings


async def create_database() -> None:
    """Create a database."""

    engine = create_async_engine(str(settings.db_url.with_path("/mysql")))

    async with engine.connect() as conn:
        database_existance = await conn.execute(
            text(
                "SELECT 1 FROM INFORMATION_SCHEMA.SCHEMATA"  # noqa: S608
                f" WHERE SCHEMA_NAME='{settings.db_base}';",
            ),
        )
        database_exists = database_existance.scalar() == 1

    if database_exists:
        await drop_database()

    async with engine.connect() as conn:  # noqa: WPS440
        await conn.execute(
            text(
                f"CREATE DATABASE {settings.db_base};",
            ),
        )


async def drop_database() -> None:
    """Drop current database."""
    engine = create_async_engine(str(settings.db_url.with_path("/mysql")))
    async with engine.connect() as conn:
        await conn.execute(text(f"DROP DATABASE {settings.db_base};"))


async def serializer(obj):
    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    raise TypeError(f"Type {type(obj)} is not serializable")
