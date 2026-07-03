from uuid import UUID

from sovereignai.shared.types import new_correlation_id
from sovereignai.shared.types_base import CorrelationId


def test_new_correlation_id_returns_uuid():
    cid = new_correlation_id()
    assert isinstance(cid, UUID)
    assert cid.version == 4


def test_correlation_id_wraps_uuid():
    uuid_val = UUID("12345678-1234-5678-1234-567812345678")
    cid = CorrelationId(uuid_val)
    assert isinstance(cid, UUID)
    assert str(cid) == "12345678-1234-5678-1234-567812345678"


def test_correlation_id_generation():
    cid1 = new_correlation_id()
    cid2 = new_correlation_id()
    assert isinstance(cid1, UUID)
    assert isinstance(cid2, UUID)
    assert cid1 != cid2


def test_correlation_id_type_annotation():
    from typing import get_type_hints

    hints = get_type_hints(new_correlation_id)
    assert hints.get("return") == CorrelationId
