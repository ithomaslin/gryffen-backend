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

from gryffen.core.strategies.enum import GridType


class GridStrategy:

    """This is a grid strategy class."""

    def __init__(
        self, upper_bound, lower_bound, grid_size,
        grid_type, stop_loss, trade_amount, owner_id
    ) -> None:
        """This is the constructor of the grid strategy class."""
        assert upper_bound > lower_bound

        self.upper_bound = upper_bound
        self.lower_bound = lower_bound
        self.grid_size = grid_size
        self.grid_type = grid_type
        self.stop_loss = stop_loss
        self.trade_amount = trade_amount
        self.owner_id = owner_id

        self.grids: List = []
        self.init_grid()

    async def init_grid(self):
        """This method is used to initialise the grid."""
        if self.grid_type == GridType.ARITHMETIC:
            step = (self.upper_bound - self.lower_bound) / (self.grid_size - 1)
            self.grids = [self.lower_bound + step * i for i in range(self.grid_size)]
        elif self.grid_type == GridType.GEOMETRIC:
            ratio = (self.upper_bound / self.lower_bound) ** (1 / self.grid_size - 1)
            self.grids = [self.lower_bound * ratio ** i for i in range(self.grid_size)]
        else:
            raise ValueError("Invalid grid type.")
