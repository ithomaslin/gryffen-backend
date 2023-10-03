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

from fastapi.routing import APIRouter
from gryffen.web.api.v1 import user
from gryffen.web.api.v1 import strategy
from gryffen.web.api.v1 import exchange
from gryffen.web.api.v1 import credential


router = APIRouter()
router.include_router(user.router, prefix="/v1", tags=["user"])
router.include_router(strategy.router, prefix="/v1", tags=["strategy"])
router.include_router(exchange.router, prefix="/v1", tags=["exchange"])
router.include_router(credential.router, prefix="/v1", tags=["credential"])
