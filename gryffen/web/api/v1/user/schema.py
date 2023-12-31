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

from typing import List
from pydantic import BaseModel
from pydantic import EmailStr
from pydantic import ConfigDict
from gryffen.web.api.utils import is_valid_email


class UserCreationSchema(BaseModel):

    model_config = ConfigDict(from_attributes=True)

    email: EmailStr
    password: str
    register_via: str
    external_uid: bool
    # In-class list to capture validation errors
    __errors: List = []

    async def is_valid(self):
        if not self.email or not is_valid_email(self.email):
            self.__errors.append("Please enter a valid email address.")

        if not self.__errors:
            return True
        return False


class UserAuthenticationSchema(BaseModel):

    model_config = ConfigDict(from_attributes=True)

    email: str
    password: str
    external_uid: bool
