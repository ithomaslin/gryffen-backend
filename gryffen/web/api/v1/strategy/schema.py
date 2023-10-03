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

from pydantic import BaseModel
from pydantic import ConfigDict
from typing import Optional


class StrategyCreationSchema(BaseModel):

    """
    Schema for creating a strategy.

    Attributes:
        name (str): The name of the strategy.
        description (str): The description of the strategy.
        symbol (str): The symbol of the strategy.
        risk_level (int): The risk level of the strategy.
        risk_tolerance (int): The risk tolerance of the strategy.
        strategy_type (int): The type of the strategy.
        principal_balance (float): The principal balance of the strategy.
        max_drawdown (float): The maximum drawdown of the strategy.
        is_active (bool): Whether the strategy is active.
    """

    model_config = ConfigDict(from_attributes=True)

    name: str
    description: str
    symbol: str
    risk_level: int
    risk_tolerance: int
    strategy_type: int
    principal_balance: float
    max_drawdown: Optional[float] = None
    is_active: bool
