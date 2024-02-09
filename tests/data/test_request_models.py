import pytest
from pydantic import ValidationError

from log_service.data.request_models import CreateEventModel


def test_create_event_model_with_valid_data():
    # Test creating an instance with all fields provided and valid
    event_data = {"key": "value"}
    model = CreateEventModel(
        event_type="test_event",
        timestamp_utc=123456789,
        customer_id=1,
        event_data=event_data,
    )
    assert model.event_type == "test_event"
    assert model.timestamp_utc == 123456789
    assert model.customer_id == 1
    assert model.event_data == event_data


def test_create_event_model_without_timestamp():
    # Test creating an instance without providing `timestamp_utc`
    event_data = {"key": "value"}
    model = CreateEventModel(
        event_type="test_event", customer_id=1, event_data=event_data
    )
    assert model.event_type == "test_event"
    assert model.customer_id == 1
    assert model.event_data == event_data
    assert model.timestamp_utc is None


def test_create_event_model_with_empty_event_data():
    # Test that creating an instance with empty `event_data` raises a ValidationError
    with pytest.raises(ValidationError) as exc_info:
        CreateEventModel(
            event_type="test_event",
            timestamp_utc=123456789,
            customer_id=1,
            event_data={},
        )
    assert "event_data must contain at least one field" in str(exc_info.value)
