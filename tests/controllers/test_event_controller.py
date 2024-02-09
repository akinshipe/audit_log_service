import pytest
from fastapi import HTTPException
from log_service.controllers.event_controller import EventController
from log_service.data.event_dto import EventRequestDTO


@pytest.fixture
def event_controller(mocker):
    mocker.patch(
        "log_service.controllers.event_controller.EventDatabaseAccessor",
        return_value=mocker.Mock(),
    )
    mocker.patch(
        "log_service.controllers.event_controller.LogServiceConfig.get_instance",
        return_value=mocker.Mock(),
    )
    mocker.patch(
        "log_service.controllers.event_controller.QueueProducer.get_instance",
        return_value=mocker.Mock(),
    )
    return EventController()


def test_create_event_success(event_controller):
    # mock_queue_producer.enqueue_event.return_value = True
    response = event_controller.create_event("type", 1234567890, 1, {})
    assert response == "Event received and queued successfully"


def test_create_event_failure(mocker, event_controller):
    mocker.patch.object(
        event_controller.queue_processor, "enqueue_event", return_value=False
    )
    with pytest.raises(HTTPException) as excinfo:
        event_controller.create_event("type", 1234567890, 1, {})
    assert excinfo.value.status_code == 500


def test_get_event_success(mocker, event_controller):
    return_value = (
        [
            {
                "event_type": "type",
                "timestamp_utc": 1234567890,
                "customer_id": 1,
                "event_data": {},
            }
        ],
        1,
    )
    mocker.patch.object(
        event_controller.database_accessor, "get_events", return_value=return_value
    )

    request_dto = EventRequestDTO()
    response = event_controller.get_event(request_dto)
    assert "events" in response
    assert response["total_count"] == 1
