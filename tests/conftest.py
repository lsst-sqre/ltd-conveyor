from __future__ import annotations

from typing import Iterator

import pytest
import respx

from tests.support.keepermock import MockKeeper, patch_factory_keeper


@pytest.fixture
def mock_keeper(respx_mock: respx.Router) -> Iterator[MockKeeper]:
    yield from patch_factory_keeper(respx_mock=respx_mock)
