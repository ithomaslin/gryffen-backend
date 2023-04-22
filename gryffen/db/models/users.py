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

from datetime import datetime
from typing import List

from sqlalchemy import Boolean, Column, DateTime, Integer, String
from sqlalchemy.orm import Mapped, relationship

from gryffen.db.base import Base
from gryffen.db.models.positions import Position
from gryffen.db.models.strategies import Strategy
from gryffen.security import hashing


class User(Base):

    __tablename__ = "user"

    id: Mapped[int] = Column(Integer, primary_key=True, index=True)
    public_id: Mapped[str] = Column(String(50), unique=True)
    username: Mapped[str] = Column(String(50), unique=True, nullable=False)
    email: Mapped[str] = Column(String(100), unique=True, nullable=False)
    password: Mapped[str] = Column(String(100), nullable=False)
    access_token: Mapped[str] = Column(String(1024), default=None)
    is_active: Mapped[bool] = Column(Boolean(), default=False)
    is_superuser: Mapped[bool] = Column(Boolean(), default=False)
    timestamp_created: Mapped[datetime] = Column(DateTime)
    timestamp_updated: Mapped[datetime] = Column(DateTime)

    positions: Mapped[List[Position]] = relationship(
        "Position",
        back_populates="owner",
        cascade="all, delete-orphan",
    )
    strategies: Mapped[List[Strategy]] = relationship(
        "Strategy",
        back_populates="owner",
        cascade="all, delete-orphan",
    )

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        for key, value in kwargs.items():
            if hasattr(value, "__iter__") and not isinstance(value, str):
                value = value[0]
            if key == "password":
                value = hashing(value)
            setattr(self, key, value)

    def __repr__(self):
        return f"User <{self.username} ({self.email})> - is_active: {self.is_active}"
