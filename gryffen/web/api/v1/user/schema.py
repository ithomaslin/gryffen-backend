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
This script is used to define user data object schema.

Author: Thomas Lin (ithomaslin@gmail.com | thomas@neat.tw)
Date: 22/04/2023
"""

from typing import List

from pydantic import BaseModel, EmailStr

from gryffen.web.api.utils import is_valid_email


class UserCreationSchema(BaseModel):

    email: EmailStr
    password: str | None
    register_via: str | None
    external_uid: str | None
    first_name: str | None
    last_name: str | None
    # In-class list to capture validation errors
    __errors: List = []

    class Config:
        orm_mode = True

    async def is_valid(self):
        if not self.email or not is_valid_email(self.email):
            self.__errors.append("Please enter a valid email address.")

        if not self.__errors:
            return True
        return False


class UserAuthenticationSchema(BaseModel):

    email: str
    password: str | None
    external_uid: str | None

    class Config:
        orm_mode = True
