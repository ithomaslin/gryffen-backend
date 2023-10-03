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

"""
This script is for all Gryffen security methods.

Author: Thomas Lin (ithomaslin@gmail.com | thomas@neat.tw)
Date: 22/04/2023
"""

import os
import jwt
import hashlib
import binascii
from jwt import PyJWTError
from datetime import datetime, timedelta
from fastapi import HTTPException, status
from pydantic import BaseModel, ConfigDict
from fastapi.security import OAuth2PasswordBearer

from gryffen.settings import settings
from gryffen.logging import logger

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def hashing(password: str) -> hashlib.sha256:
    """Hashes the password.

    Encrypts the password from a plain string to a byte string.
    The byte string is then hashed using the SHA-256 algorithm.
    The byte string is then encoded to a hex string.
    The hex string is then returned.

    Args:
        password: The password to be hashed.

    Returns:
        hashlib.sha256: The hashed password.
    """
    if password is None:
        return None
    salt = hashlib.sha256(os.urandom(60)).hexdigest().encode("ascii")
    password_hash = binascii.hexlify(
        hashlib.pbkdf2_hmac("sha512", password.encode("utf-8"), salt, 100000),
    )
    return salt + password_hash


def verify_password(provided_password: str, stored_password: hashlib.sha256()) -> bool:
    """Verifies if the user provided password matches the stored password.

    Args:
        provided_password: The password provided by the user when logging in.
        stored_password: The password stored in the database.

    Returns:
        bool: True if passwords match, False otherwise.
    """
    stored_password = stored_password.decode('ascii')
    salt = stored_password[:64]
    stored_password = stored_password[64:]
    password_hash = hashlib.pbkdf2_hmac(
        'sha512', provided_password.encode('utf-8'), salt.encode('ascii'), 100000
    )
    password_hash = binascii.hexlify(password_hash).decode('ascii')
    return password_hash == stored_password


class TokenBase(BaseModel):

    """The TokenBase class to be used as the base object for all token objects.

    Attributes:
        email: The email of the user.
        public_id: The public_id of the user.
        token: The token of the user.
        expiration: The expiration of the token.
    """

    model_config = ConfigDict(from_attributes=True)

    email: str | None = None
    public_id: str | None = None
    token: str | None = None
    expiration: datetime | None = None

    def tokenize(self, expiration_delta: timedelta | None = None) -> str:
        """Creates token

        Args:
            expiration_delta: The time delta of which the token to be expired.

        Returns:
            str: The tokenized string.
        """
        to_encode: dict = self.model_dump(exclude={'token', 'expiration'})
        if expiration_delta:
            expire = datetime.utcnow() + expiration_delta
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

    def detokenize(self) -> None:
        """Decodes token string into TokenBase class object.

        Returns:
            TokenBase: The TokenBase class object, which contains user's info:
                - email
                - public_id
        """
        credential_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credential invalid, make sure you have the valid credential.",
            headers={"WWW-Authenticate": "Bearer"},
        )
        try:
            payload = jwt.decode(
                self.token,
                settings.gryffen_security_key,
                algorithms=settings.access_token_hash_algorithm,
            )
            self.email: str = payload.get("email")
            self.public_id: str = payload.get("public_id")
            self.expiration: datetime = datetime.fromtimestamp(payload.get("expires"))

            if self.email is None or self.public_id is None:
                logger.error("Invalid credential - User not found.")
                raise credential_exception
            elif self.expiration < datetime.utcnow():
                logger.error("Invalid credential - Token expired.")
                raise credential_exception

        except PyJWTError:
            logger.error("Invalid credential.")
            raise credential_exception


def destruct_token(token: str) -> TokenBase:
    """Decodes token string into TokenBase class object.

    Notes:
        This is a helper function for the `TokenBase.detokenize()` class method to
        be used as the dependency injection.

    Returns:
        TokenBase: The TokenBase class object, which contains user's info:
            - email
            - public_id
    """
    token_base = TokenBase()
    token_base.token = token
    token_base.detokenize()
    return token_base
