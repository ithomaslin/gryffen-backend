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

from datetime import datetime
from decimal import Decimal
from sqlalchemy import Boolean
from sqlalchemy import DateTime
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import Numeric
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship
from gryffen.db.base import Base


class Position(Base):

    """
    Position model

    Attributes:
        id (int): ID of the position
        symbol (str): Symbol of the position
        is_finalized (bool): Whether the position is finalized
        timestamp_created (datetime): Timestamp of the position creation
        timestamp_updated (datetime): Timestamp of the position update
        entry_price (Decimal): Entry price of the position
        volume (Decimal): Volume of the position
        realized_profit (Decimal): Realized profit of the position
        owner_id (int): ID of the owner
        owner (User): Owner of the position
    """

    __tablename__ = "position"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    symbol: Mapped[str] = mapped_column(String(50), nullable=False)
    is_finalized: Mapped[bool] = mapped_column(Boolean(), default=False)
    entry_price: Mapped[Decimal] = mapped_column(Numeric(precision=10, scale=4), nullable=False)
    volume: Mapped[Decimal] = mapped_column(Numeric(precision=10, scale=4), nullable=False)
    realized_profit: Mapped[Decimal] = mapped_column(Numeric(precision=10, scale=4), default=0, nullable=False)
    timestamp_created: Mapped[datetime] = mapped_column(DateTime)
    timestamp_updated: Mapped[datetime] = mapped_column(DateTime)

    # Relationships:
    # - Many-to-one: User
    #   Multiple positions belong to a single user
    owner_id: Mapped[int] = mapped_column(ForeignKey("user.id"))
    owner: Mapped["User"] = relationship(
        "User",
        back_populates="positions"
    )

    # Relationships:
    # - Many-to-one: Strategy
    #   Multiple positions belong to a single strategy
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
