import pytest
from pydantic import ValidationError

from app.core.models import Worker


def test_worker_validators():
    # validators passed
    worker = Worker(**{"name": "w1", "interval": 1, "source": "http://test.com"})
    assert worker.name == "w1"

    # source must be a valid url
    with pytest.raises(ValidationError):
        Worker(**{"name": "w1", "interval": 1, "source": "http2://test.com"})
