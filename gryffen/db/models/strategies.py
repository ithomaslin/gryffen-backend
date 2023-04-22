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
This script is used to create data model for strategy.

Author: Thomas Lin (ithomaslin@gmail.com | thomas@neat.tw)
Date: 22/04/2023
"""
from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import mapped_column, relationship

from gryffen.db.base import Base
from gryffen.db.models.users import User


class Strategy(Base):

    __tablename__ = "strategy"

    id: int = Column(Integer, primary_key=True, index=True)
    upper_bound: int = mapped_column(Integer)
    lower_bound: int = mapped_column(Integer)
    grid_size: int = mapped_column(Integer)
    grid_type: str = mapped_column(String(50))
    is_active: bool = Column(Boolean(), default=True)
    timestamp_created: datetime = Column(DateTime)
    timestamp_updated: datetime = Column(DateTime)

    owner_id: int = mapped_column(ForeignKey("user.id"))
    owner: User = relationship(back_populates="strategies")
