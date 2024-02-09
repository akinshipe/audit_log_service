import pytest

from log_service.data.event_dto import EventQueueDTO
from log_service.processors.queue_consumer import QueueConsumer


@pytest.fixture
def setup_queue_consumer():
    QueueConsumer._instance = None
    consumer = QueueConsumer.get_instance()

    return consumer


def test_singleton_pattern(setup_queue_consumer):
    consumer1 = setup_queue_consumer
    consumer2 = QueueConsumer.get_instance()
    assert consumer1 is consumer2


def test_consume_events_empty_queue(mocker, setup_queue_consumer):
    consumer = setup_queue_consumer
    mock_sleep = mocker.patch("time.sleep")
    consumer.consume_events()
    mock_sleep.assert_called_once()


def test_consume_events_with_data(setup_queue_consumer, mocker):
    consumer = setup_queue_consumer
    mock_event = EventQueueDTO(
        event_type="test",
        timestamp_utc=123456789,
        customer_id=1,
        event_data={"key": "value"},
    )
    consumer.event_queue.append(mock_event)

    spy = mocker.spy(consumer, "_save_event")
    consumer.consume_events()
    consumer._save_event.assert_called_once_with([mock_event])
    assert spy.call_args[0][0] == [mock_event]
    assert len(consumer.event_queue) == 0


def test_save_event_failure_and_retry(mocker, setup_queue_consumer):
    consumer = setup_queue_consumer
    mock_event = EventQueueDTO(
        event_type="test",
        timestamp_utc=123456789,
        customer_id=1,
        event_data={"key": "value"},
    )
    consumer.event_queue.append(mock_event)

    mocked_db_accessor = mocker.Mock()
    mocked_db_accessor.save_events_to_db.return_value = False

    consumer.database_accessor = mocked_db_accessor

    consumer.consume_events()
    # Verify that the event was re-queued due to failure
    assert mock_event in consumer.event_queue


def test_save_event_failure_and_retry_with_no_connection_object(
    mocker, setup_queue_consumer
):
    consumer = setup_queue_consumer
    mock_event = EventQueueDTO(
        event_type="test",
        timestamp_utc=123456789,
        customer_id=1,
        event_data={"key": "value"},
    )
    consumer.event_queue.append(mock_event)

    mocked_db_accessor = mocker.Mock()
    mocked_db_accessor.save_events_to_db.return_value = False

    consumer.database_accessor = mocked_db_accessor
    # disable the connection object
    consumer.conn = None

    consumer.consume_events()
    # Verify that the event was re-queued due to failure
    assert mock_event in consumer.event_queue


def test_multiple_consumers_instance_raise_exception(mocker):
    # This test is to verify that the singleton pattern is working as expected.
    QueueConsumer._instance = None
    _ = QueueConsumer()
    with pytest.raises(Exception):
        _ = QueueConsumer()
