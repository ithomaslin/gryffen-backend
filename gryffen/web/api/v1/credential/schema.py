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

from pydantic import BaseModel
from pydantic import ConfigDict
from datetime import datetime
from typing import Optional


class CredentialCreationSchema(BaseModel):

    """The CredentialCreationSchema is used to define the data object

    Attributes:
        exchange_id (int): The exchange id
        credential (str): The credential string
        type (str): The type of the credential
        scope (str): The scope of the credential
        expires_at (datetime): The expiration date
    """

    model_config = ConfigDict(from_attributes=True)

    exchange_id: int
    credential: str
    type: str
    scope: str
    expires_at: Optional[datetime] = None
