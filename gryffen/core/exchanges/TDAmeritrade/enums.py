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
TD Ameritrade API Authentication Module - Enums

@Author: Thomas Lin (ithomaslin@gmail.com | thomas@neat.tw)
@Date: 22/04/2023
"""

from enum import Enum


class GrantType(str, Enum):
    AUTH_CODE = "authorization_code"
    REFRESH_TOKEN = "refresh_token"

    def __repr__(self) -> str:
        return str.__str__(self)


class TokenType(str, Enum):
    REFRESH_TOKEN = "refresh_token"
    ACCESS_TOKEN = "access_token"

    def __repr__(self) -> str:
        return str.__str__(self)
