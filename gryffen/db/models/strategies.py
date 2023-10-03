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
from typing import List
from decimal import Decimal
from sqlalchemy import Boolean
from sqlalchemy import DateTime
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import Numeric
from sqlalchemy import String
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship
from gryffen.db.base import Base


class Strategy(Base):

    """Strategy model

    Attributes:
        id (int): Strategy ID
        name (str): Strategy name
        description (str): Strategy description
        symbol (str): Strategy symbol
        risk_level (int): Strategy risk level
        risk_tolerance (int): Strategy risk tolerance
        principal_balance (Decimal): Strategy principal balance
        max_drawdown (Decimal): Strategy max drawdown
        is_active (bool): Strategy is active
        timestamp_created (datetime): Strategy timestamp created
        timestamp_updated (datetime): Strategy timestamp updated
        owner_id (int): Strategy owner ID
        owner (User): Strategy owner
        positions (List[Position]): Strategy positions
    """

    __tablename__ = "strategy"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str] = mapped_column(String(500), nullable=True)
    symbol: Mapped[str] = mapped_column(String(50))
    risk_level: Mapped[int] = mapped_column(Integer, default=0)
    risk_tolerance: Mapped[int] = mapped_column(Integer, default=0)
    principal_balance: Mapped[Decimal] = mapped_column(Numeric(precision=10, scale=4))
    max_drawdown: Mapped[Decimal] = mapped_column(Numeric(precision=10, scale=4))
    is_active: Mapped[bool] = mapped_column(Boolean(), default=True)
    timestamp_created: Mapped[datetime] = mapped_column(DateTime)
    timestamp_updated: Mapped[datetime] = mapped_column(DateTime)

    # Relationships:
    # - Many-to-one: User
    #   Multiple strategies belong to a single user
    owner_id: Mapped[int] = mapped_column(ForeignKey("user.id"))
    owner: Mapped["User"] = relationship(
        "User",
        back_populates="strategies"
    )

    # Relationships:
    # - One-to-many: Position
    #   Strategy can have many positions
    positions: Mapped[List["Position"]] = relationship(
        "Position",
        back_populates="strategy",
        cascade="all, delete, delete-orphan"
    )

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def __repr__(self):
        return f'Strategy {self.id} - {self.symbol}'
