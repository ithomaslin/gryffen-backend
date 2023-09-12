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
This script is used to define the base settings for Gryffen.

Author: Thomas Lin (ithomaslin@gmail.com | thomas@neat.tw)
Date: 22/04/2023
"""

import enum
import os
from pathlib import Path
from tempfile import gettempdir

from dotenv import load_dotenv
from pydantic import BaseSettings
from yarl import URL

TEMP_DIR = Path(gettempdir())
load_dotenv()


class LogLevel(str, enum.Enum):  # noqa: WPS600
    """Possible log levels."""

    NOTSET = "NOTSET"
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    FATAL = "FATAL"


class Settings(BaseSettings):
    """
    Application settings.

    These parameters can be configured
    with environment variables.
    """

    host: str = "127.0.0.1"
    port: int = 8000
    # quantity of workers for uvicorn
    workers_count: int = 1
    # Enable uvicorn reloading
    reload: bool = False

    # Current environment
    environment: str = "dev"

    log_level: LogLevel = LogLevel.INFO

    scaler = int(os.getenv("NUM_BENCHMARK"))

    gryffen_security_key = os.getenv("GRYFFEN_SECRET_KEY")
    hashing_iteration = os.getenv("HASH_ITERATION")
    unix_timestamp_never_expire = os.getenv("UNIX_TIMESTAMP_NEVER_EXPIRE")

    # Access token
    access_token_hash_algorithm = os.getenv("ACCESS_TOKEN_HASH_ALGO")
    access_token_duration_minute = os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES")
    oauth_token_duration_minute = os.getenv("OAUTH_TOKEN_EXPIRE_MINUTES")

    # Variables for the database
    db_host: str = os.getenv("PROD_DB_HOST")
    db_port: int = os.getenv("PROD_DB_PORT")
    db_user: str = os.getenv("PROD_DB_USER")
    db_pass: str = os.getenv("PROD_DB_PASS")
    db_base: str = os.getenv("PROD_DB_NAME")
    db_echo: bool = False

    # Finnhub
    finnhub_ws_endpoint = os.getenv("FINNHUB_WEBSOCKET_URI")
    finnhub_api_key = os.getenv("FINNHUB_API_KEY")

    # TD Ameritrade
    td_ameritrade_api_key = os.getenv("TD_API_CONSUMER_KEY")
    td_ameritrade_auth_url = os.getenv("TD_API_AUTH_URL")
    td_ameritrade_base_url = os.getenv("TD_API_BASE_URL")
    td_ameritrade_auth_endpoint = os.getenv("TD_API_AUTH_URL")
    td_ameritrade_orders_endpoint = os.getenv("TD_API_ORDERS_URL")
    td_ameritrade_redirect_uri = os.getenv("TD_API_REDIRECT_URL")

    front_end_ip_address = [
        os.getenv("FRONT_END_TEST_URL"),
        os.getenv("FRONT_END_IP_ADDRESS"),
    ]

    @property
    def db_url(self) -> URL:
        """
        Assemble database URL from settings.

        :return: database URL.
        """
        return URL.build(
            scheme="mysql+aiomysql",
            host=self.db_host,
            port=self.db_port,
            user=self.db_user,
            password=self.db_pass,
            path=f"/{self.db_base}",
        )

    class Config:
        env_file = ".env"
        env_prefix = "GRYFFEN_"
        env_file_encoding = "utf-8"


settings = Settings()
