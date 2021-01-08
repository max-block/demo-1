import pytest
from pydantic import ValidationError

from app.core.models import WorkerInDB


def test_worker_validators():
    # validators passed
    worker = WorkerInDB(**{"name": "w1", "interval": 1, "source": "http://test.com"})
    assert worker.name == "w1"

    # source must be a valid url
    with pytest.raises(ValidationError):
        WorkerInDB(**{"name": "w1", "interval": 1, "source": "http2://test.com"})
