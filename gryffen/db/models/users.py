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
from sqlalchemy import Boolean
from sqlalchemy import DateTime
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import LargeBinary
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship
from typing import List
from gryffen.db.base import Base
from gryffen.db.models.positions import Position
from gryffen.db.models.strategies import Strategy
from gryffen.db.models.exchanges import Exchange
from gryffen.db.models.credentials import Credential
from gryffen.db.models.activations import Activation


class User(Base):

    """
    User model

    Attributes:
        id (int): Primary key
        public_id (str): Unique id for the user, can be used for external facing.
        username (str): Username
        email (str): Email
        password (str): Password
        first_name (str): First name
        last_name (str): Last name
        register_via (str): Indicates the source of the registration
        external_uid (str): The external uid fetched from the third-party authentication provider
        api_key (str): Api key
        is_active (bool): Is active
        tier (int): Tier of the user, default as 0, is
        is_superuser (bool): Is superuser
        timestamp_created (datetime): Timestamp created
        timestamp_updated (datetime): Timestamp updated
        positions (List[Position]): Positions
        strategies (List[Strategy]): Strategies
        exchanges (List[Exchange]): Exchanges
        credentials (List[Credential]): Credentials
        activations (List[Activation]): Activations
    """

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
    api_key: Mapped[str] = mapped_column(String(1024), nullable=True, default=None)
    is_active: Mapped[bool] = mapped_column(Boolean(), default=False)
    tier: Mapped[int] = mapped_column(Integer, nullable=True, default=0)
    is_superuser: Mapped[bool] = mapped_column(Boolean(), default=False)
    timestamp_created: Mapped[datetime] = mapped_column(DateTime)
    timestamp_updated: Mapped[datetime] = mapped_column(DateTime)

    # Relationships:
    # - One-to-many: Position
    #   Users can have many positions
    positions: Mapped[List["Position"]] = relationship(
        "Position",
        back_populates="owner",
        cascade="all, delete-orphan",
    )

    # Relationships:
    # - One-to-many: Strategy
    #   Users can have many strategies
    strategies: Mapped[List["Strategy"]] = relationship(
        "Strategy",
        back_populates="owner",
        cascade="all, delete-orphan",
    )

    # Relationships:
    # - One-to-many: Exchange
    #   Users can have many exchange brokers
    exchanges: Mapped[List["Exchange"]] = relationship(
        "Exchange",
        back_populates="owner",
        cascade="all, delete-orphan",
    )

    # Relationships:
    # - One-to-many: Credential
    #   Users can have many credentials
    credentials: Mapped[List["Credential"]] = relationship(
        "Credential",
        back_populates="owner",
        cascade="all, delete-orphan",
    )

    # Relationships:
    # - One-to-many: Activation
    #   Users can have many activation codes
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
            setattr(self, key, value)

    def __repr__(self):
        return f"User <{self.username} ({self.email})> - is_active: {self.is_active}"
