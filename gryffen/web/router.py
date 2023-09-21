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
This script is used to create the base router for the API.

Author: Thomas Lin (ithomaslin@gmail.com | thomas@neat.tw)
Date: 19/09/2023
"""

from fastapi import Request
from fastapi.routing import APIRouter

from .lifetime import template

root_router = APIRouter()


@root_router.get("/")
async def root(request: Request):
    return template.TemplateResponse("home.html", {"request": request})