import pytest
from gryffen.web.api.utils import GriffinMailService


@pytest.mark.anyio
def test_mail_service() -> None:
    service = GriffinMailService()
    assert service.send('ithomaslin@gmail.com', "test-activation-code")
