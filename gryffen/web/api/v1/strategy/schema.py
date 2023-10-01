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
This script is used to define strategy data object schema.

Author: Thomas Lin (ithomaslin@gmail.com | thomas@neat.tw)
Date: 22/04/2023
"""

from pydantic import BaseModel, ConfigDict
from typing import Optional


class StrategyCreationSchema(BaseModel):

    """
    Schema for creating a strategy.

    Attributes:
        symbol (str): The symbol of the strategy associated to.
        strategy_type (int): The type of the strategy.
        grid_type (int): The type of the grid.
        upper_bound (float): The upper bound of the grid.
        lower_bound (float): The lower bound of the grid.
        grid_size (int): The size of the grid.
        principal_balance (float): The principal balance of the strategy.
        max_drawdown (float): The max drawdown of the strategy.
    """

    model_config = ConfigDict(from_attributes=True)

    symbol: str
    strategy_type: int
    grid_type: int
    upper_bound: float
    lower_bound: float
    grid_size: int
    principal_balance: float
    max_drawdown: Optional[float] = None
