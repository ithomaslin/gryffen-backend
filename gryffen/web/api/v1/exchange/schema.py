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
This script is used to define exchange data object schema.

Author: Thomas Lin (ithomaslin@gmail.com | thomas@neat.tw)
Date: 22/04/2023
"""

from pydantic import BaseModel, ConfigDict


class ExchangeCreationSchema(BaseModel):

    """Schema for creating exchange.

    Attributes:
        name (str): Exchange name.
        type (str): Exchange type.
        account_id (str): Account id of the exchange.
    """

    model_config = ConfigDict(from_attributes=True)

    name: str
    type: str
    account_id: str
