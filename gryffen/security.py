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
This script is for all Gryffen security methods.

Author: Thomas Lin (ithomaslin@gmail.com | thomas@neat.tw)
Date: 22/04/2023
"""

import binascii
import hashlib
import os
import time
from datetime import datetime, timedelta
from typing import Optional, Dict, Any

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jwt import PyJWTError

from gryffen.settings import settings
from gryffen.logging import logger

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def hashing(password: str) -> hashlib.sha256:
    """
    Generate a hashed password.
    @param: password: user password
    @return: byte
    """
    salt = hashlib.sha256(os.urandom(60)).hexdigest().encode("ascii")
    password_hash = binascii.hexlify(
        hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 100000),
    )
    return salt + password_hash


def create_access_token(data: Dict, expire_delta: Optional[timedelta] = None) -> str:
    """

    @param data: {"id": "<USER_ID>", "username": "<USERNAME>", "email":"<EMAIL>"}
    @param expire_delta:
    @return:
    """
    to_encode = data.copy()
    if expire_delta:
        expire = datetime.utcnow() + expire_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=int(settings.access_token_duration_minute),
        )
    to_encode.update({"expires": int(datetime.timestamp(expire))})
    encoded_jwt = jwt.encode(
        to_encode,
        settings.gryffen_security_key,
        algorithm=settings.access_token_hash_algorithm,
    )
    return encoded_jwt


def decode_access_token(token: str = Depends(oauth2_scheme)) -> Dict[str, Any]:
    credential_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Credential invalid, make sure you have the valid credential.",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(
            token,
            settings.gryffen_security_key,
            algorithms=settings.access_token_hash_algorithm,
        )
        username: str = payload.get("username")
        expires: datetime = datetime.utcfromtimestamp(payload.get("expires"))
        if username is None:
            logger.error("Invalid credential - User not found.")
            raise credential_exception
        elif expires <= datetime.utcnow():
            logger.error("Invalid credential - Credential expires.")
            raise credential_exception
    except PyJWTError:
        logger.error("Invalid credential.")
        raise credential_exception
    return payload
