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

import json
import math
import decimal
from datetime import datetime
from decimal import Decimal
from decimal import Context
from decimal import setcontext
from gryffen.core.strategies.enum import GridType


ctx = Context(prec=2, rounding=decimal.ROUND_DOWN)
setcontext(ctx)


class GridStrategy:

    """This is a grid strategy class."""

    def __init__(
        self, symbol, upper_bound, lower_bound, grid_size,
        grid_type, max_drawdown, principal_balance, owner_id
    ) -> None:
        """
        This is the constructor of the grid strategy class.

        @param symbol: symbol of the strategy
        @param upper_bound: upper bound of the grid
        @param lower_bound: lower bound of the grid
        @param grid_size: size of the grid
        @param grid_type: type of the grid
        @param max_drawdown: max drawdown accepted by the strategy
        @param principal_balance: trade amount of the strategy
        @param owner_id: owner id of the strategy
        """
        assert upper_bound > lower_bound, \
            f"Upper bound {upper_bound} must be " \
            f"greater than lower bound {lower_bound}."

        self.symbol = symbol
        self.upper_bound = upper_bound
        self.lower_bound = lower_bound
        self.grid_size = grid_size
        self.grid_type = grid_type
        self.max_drawdown = max_drawdown
        self.principal_balance = principal_balance
        self.owner_id = owner_id
        self.created = datetime.utcnow()

        # Initialize grids for the strategy based on grid type
        # Arithmetic: [1, 2, 3, 4, 5]
        # Geometric: [1, 2, 4, 8, 16]
        if self.grid_type == GridType.ARITHMETIC.value:
            step = (self.upper_bound - self.lower_bound) / (self.grid_size - 1)
            grids = [
                Decimal(str(math.floor((self.lower_bound + step * i) * 100) / 100))
                for i in range(int(self.grid_size))
            ]
        elif self.grid_type == GridType.GEOMETRIC.value:
            ratio = (self.upper_bound / self.lower_bound) ** (1 / self.grid_size - 1)
            grids = [
                Decimal(str(math.floor((self.lower_bound * ratio ** i) * 100) / 100))
                for i in range(int(self.grid_size))
            ]
        else:
            raise ValueError("Invalid grid type.")

        self.grids = grids

    def __str__(self):
        return json.dumps(self.grids, default=str)

    def __repr__(self):
        return self.__str__()
