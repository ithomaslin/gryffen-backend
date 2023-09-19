import uuid
import os
import pytest
from fastapi import FastAPI
from httpx import AsyncClient
from starlette import status

from gryffen.web.api.utils import GriffinMailService


@pytest.mark.anyio
def test_mail_service() -> None:

    service = GriffinMailService()
    assert service.send(os.getenv("TEST_EMAIL"), "test-activation-code")
