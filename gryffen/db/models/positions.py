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
This script is used to create the date model for position.

Author: Thomas Lin (ithomaslin@gmail.com | thomas@neat.tw)
Date: 22/04/2023
"""
from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from gryffen.db.base import Base
from gryffen.db.models.users import User


class Position(Base):

    __tablename__ = "position"

    id: Mapped[int] = Column(Integer, primary_key=True, index=True)
    symbol: Mapped[str] = Column(String(50), nullable=False)
    entry_price: Mapped[int] = Column(Integer, nullable=False)
    volume: Mapped[int] = Column(Integer, nullable=False)
    realized_profit: Mapped[int] = Column(Integer, default=0, nullable=False)
    is_finalized: Mapped[bool] = Column(Boolean(), default=False)
    timestamp_created: Mapped[datetime] = Column(DateTime)
    timestamp_updated: Mapped[datetime] = Column(DateTime)

    owner_id: Mapped[int] = mapped_column(ForeignKey("user.id"))
    owner: Mapped["User"] = relationship("User", back_populates="positions")
