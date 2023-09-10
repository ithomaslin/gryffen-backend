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
This script is used to define the DB model for user.

Author: Thomas Lin (ithomaslin@gmail.com | thomas@neat.tw)
Date: 22/04/2023
"""

from datetime import datetime
from typing import List

from sqlalchemy import Boolean, DateTime, Integer, String, LargeBinary
from sqlalchemy.orm import Mapped, mapped_column, relationship

from gryffen.db.base import Base
from gryffen.db.models.positions import Position
from gryffen.db.models.strategies import Strategy
from gryffen.db.models.exchanges import Exchange
from gryffen.db.models.credentials import Credential
from gryffen.db.models.activations import Activation
from gryffen.security import hashing


class User(Base):

    __tablename__ = "user"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    public_id: Mapped[str] = mapped_column(String(50), unique=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=True)
    email: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(LargeBinary, nullable=False)
    first_name: Mapped[str] = mapped_column(String(50), nullable=True)
    last_name: Mapped[str] = mapped_column(String(50), nullable=True)
    register_via: Mapped[str] = mapped_column(String(50), nullable=True)
    external_uid: Mapped[str] = mapped_column(LargeBinary, nullable=True)
    access_token: Mapped[str] = mapped_column(String(1024), nullable=True, default=None)
    is_active: Mapped[bool] = mapped_column(Boolean(), default=False)
    is_superuser: Mapped[bool] = mapped_column(Boolean(), default=False)
    timestamp_created: Mapped[datetime] = mapped_column(DateTime)
    timestamp_updated: Mapped[datetime] = mapped_column(DateTime)

    positions: Mapped[List["Position"]] = relationship(
        "Position",
        back_populates="owner",
        cascade="all, delete-orphan",
    )

    strategies: Mapped[List["Strategy"]] = relationship(
        "Strategy",
        back_populates="owner",
        cascade="all, delete-orphan",
    )

    exchanges: Mapped[List["Exchange"]] = relationship(
        "Exchange",
        back_populates="owner",
        cascade="all, delete-orphan",
    )

    credentials: Mapped[List["Credential"]] = relationship(
        "Credential",
        back_populates="owner",
        cascade="all, delete-orphan",
    )

    activations: Mapped[List["Activation"]] = relationship(
        "Activation",
        back_populates="owner",
        cascade="all, delete-orphan",
    )

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        for key, value in kwargs.items():
            if hasattr(value, "__iter__") and not isinstance(value, str):
                value = value[0]
            if key == "password" or key == "external_uid":
                value = hashing(value)
            setattr(self, key, value)

    def __repr__(self):
        return f"User <{self.username} ({self.email})> - is_active: {self.is_active}"
