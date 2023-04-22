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

from typing import List

from pydantic import BaseModel

from gryffen.web.api.utils import is_valid_email


class UserRegisterMessage(BaseModel):

    username: str
    password: str
    email: str
    errors: List = []

    async def is_valid(self):
        if not self.username or not len(self.username) > 3:
            self.errors.append("Username should have at least 4 characters.")
        if not self.email or not is_valid_email(self.email):
            self.errors.append("Please enter a valid email address.")
        if not self.password or not len(self.password) >= 4:
            self.errors.append("Password must be > 4 chars")

        if not self.errors:
            return True
        return False
