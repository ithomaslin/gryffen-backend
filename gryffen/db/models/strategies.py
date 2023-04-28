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
This script is used to define the DB model for strategy.

Author: Thomas Lin (ithomaslin@gmail.com | thomas@neat.tw)
Date: 22/04/2023
"""

from datetime import datetime
from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from gryffen.db.base import Base


class Strategy(Base):

    __tablename__ = "strategy"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    strategy_type: Mapped[int] = mapped_column(Integer)
    symbol: Mapped[str] = mapped_column(String(50))
    upper_bound: Mapped[int] = mapped_column(Integer)
    lower_bound: Mapped[int] = mapped_column(Integer)
    grid_count: Mapped[int] = mapped_column(Integer)
    grid_size: Mapped[int] = mapped_column(Integer)
    grid_type: Mapped[str] = mapped_column(String(50))
    principal_balance: Mapped[int] = mapped_column(Integer)
    max_drawdown: Mapped[int] = mapped_column(Integer)
    is_active: Mapped[bool] = mapped_column(Boolean(), default=True)
    timestamp_created: Mapped[datetime] = mapped_column(DateTime)
    timestamp_updated: Mapped[datetime] = mapped_column(DateTime)

    owner_id: Mapped[int] = mapped_column(ForeignKey("user.id"))
    owner: Mapped["User"] = relationship(
        "User",
        back_populates="strategies"
    )

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def __repr__(self):
        return f'Strategy {self.id} - {self.symbol}'
