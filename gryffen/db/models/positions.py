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
This script is used to define the DB model for position.

Author: Thomas Lin (ithomaslin@gmail.com | thomas@neat.tw)
Date: 22/04/2023
"""

from datetime import datetime
from decimal import Decimal
from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship

from gryffen.db.base import Base


class Position(Base):

    __tablename__ = "position"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    symbol: Mapped[str] = mapped_column(String(50), nullable=False)
    is_finalized: Mapped[bool] = mapped_column(Boolean(), default=False)
    timestamp_created: Mapped[datetime] = mapped_column(DateTime)
    timestamp_updated: Mapped[datetime] = mapped_column(DateTime)
    entry_price: Mapped[Decimal] = mapped_column(
        Numeric(precision=10, scale=4), nullable=False
    )
    volume: Mapped[Decimal] = mapped_column(Numeric(
        precision=10, scale=4), nullable=False
    )
    realized_profit: Mapped[Decimal] = mapped_column(
        Numeric(precision=10, scale=4), default=0, nullable=False
    )

    owner_id: Mapped[int] = mapped_column(ForeignKey("user.id"))
    owner: Mapped["User"] = relationship(
        "User",
        back_populates="positions"
    )

    strategy_id: Mapped[int] = mapped_column(ForeignKey("strategy.id"))
    strategy: Mapped["Strategy"] = relationship(
        "Strategy",
        back_populates="positions"
    )

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def __repr__(self):
        if self.is_finalized:
            return f'Finalized position ID: {self.id} - ' \
                   f'{self.symbol} : entered @ {self.entry_price}'
        else:
            return f'On-going position ID: {self.id} - ' \
                   f'{self.symbol} : entered @ {self.entry_price}'
