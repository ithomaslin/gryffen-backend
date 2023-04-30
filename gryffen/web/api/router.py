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

from gryffen.web.api import docs, echo, monitoring
from gryffen.web.api.v1 import auth, strategy, user, exchange, credential

api_router = APIRouter()
api_router.include_router(monitoring.router)
api_router.include_router(docs.router)
api_router.include_router(echo.router, prefix="/echo", tags=["echo"])
api_router.include_router(auth.router, prefix="/v1", tags=["auth", "v1"])
api_router.include_router(user.router, prefix="/v1", tags=["user", "v1"])
api_router.include_router(strategy.router, prefix="/v1", tags=["strategy", "v1"])
api_router.include_router(exchange.router, prefix="/v1", tags=["exchange", "v1"])
api_router.include_router(credential.router, prefix="/v1", tags=["credential", "v1"])
