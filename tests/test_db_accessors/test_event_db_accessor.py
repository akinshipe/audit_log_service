import os
import random
import sqlite3
from datetime import datetime, timedelta

import orjson
import pytest
from log_service.config import DB_DIRECTORY_PATH

from log_service.data.event_dto import EventRequestDTO
from log_service.db_accessors.event_db_accessor import EventDatabaseAccessor

TEST_DB_PATH = os.path.join(os.getcwd(), DB_DIRECTORY_PATH, "SQLite-test.db")
CONN = sqlite3.connect(TEST_DB_PATH)


@pytest.fixture
def mock_config(mocker):
    mock_config = mocker.Mock()
    mock_config.get_db_url.return_value = os.path.join(os.getcwd(), TEST_DB_PATH)
    return mocker.patch(
        "log_service.config.LogServiceConfig.get_instance", return_value=mock_config
    )


# @pytest.fixture
# def mock_db(mocker):
#     mocker.patch('sqlite3.connect')
#     cursor = mocker.MagicMock()
#     cursor.fetchone.return_value = [0]  # Mock for COUNT(1)
#     cursor.fetchall.return_value = []  # Default empty list for rows
#     mocker.patch('sqlite3.Connection.cursor', return_value=cursor)
#     return cursor


def test_init(mock_config):
    accessor = EventDatabaseAccessor()
    assert accessor.config.get_db_url() == TEST_DB_PATH
    mock_config.assert_called()


def seed_db_with_events(events=None, count=10):
    if not events:
        events = [
            (
                100000 + random.choice([x for x in range(5)]),
                f"event_type_{random.choice([x for x in range(5)])}",
                datetime.utcnow().timestamp(),
                orjson.dumps({"key1": "value1", "key2": "value2"}),
            )
            for x in range(count)
        ]

        # empty the db

    delete_sql = "DELETE FROM EVENTS"
    CONN.execute(delete_sql)
    print("//////////////////////////deleted")

    # insert the events
    event_db_accessor = EventDatabaseAccessor()
    event_db_accessor.save_events_to_db(insert_data=events, conn=CONN)

    return events, len(events)


def test_get_events_no_filters(mock_config):
    expected_events, expected_events_count = seed_db_with_events()
    accessor = EventDatabaseAccessor()
    event_request_dto = EventRequestDTO()
    events, count = accessor.get_events(event_request_dto)
    assert count == expected_events_count
    assert len(events) == expected_events_count


def test_get_events_with_customer_id_filters(mock_config):
    customer_id = 100
    events = [
        (
            customer_id,
            "event_type_1",
            datetime.utcnow().timestamp(),
            orjson.dumps({"key1": "value1", "key2": "value"}),
        ),
        (
            200,
            "event_type_1",
            (datetime.utcnow() + timedelta(minutes=10)).timestamp(),
            orjson.dumps({"key1": "value1", "key2": "value"}),
        ),
        (
            300,
            "event_type_1",
            (datetime.utcnow() + timedelta(minutes=10)).timestamp(),
            orjson.dumps({"key1": "value1", "key2": "value"}),
        ),
    ]
    seed_db_with_events(events=events)
    accessor = EventDatabaseAccessor()
    event_request_dto = EventRequestDTO(customer_id=customer_id)
    events, count = accessor.get_events(event_request_dto)
    assert count == 1
    assert len(events) == 1
    assert events[0]["customer_id"] == customer_id


def test_get_events_with_event_type_filter(mock_config):
    event_type = "event_type_2"
    events = [
        (
            100,
            "event_type_1",
            datetime.utcnow().timestamp(),
            orjson.dumps({"key1": "value1", "key2": "value"}),
        ),
        (
            100,
            "event_type_3",
            datetime.utcnow().timestamp(),
            orjson.dumps({"key1": "value1", "key2": "value"}),
        ),
        (
            200,
            event_type,
            (datetime.utcnow() + timedelta(minutes=10)).timestamp(),
            orjson.dumps({"key1": "value1", "key2": "value"}),
        ),
    ]

    seed_db_with_events(events=events)
    accessor = EventDatabaseAccessor()
    event_request_dto = EventRequestDTO(event_type=event_type)
    events, count = accessor.get_events(event_request_dto)
    assert count == 1
    assert len(events) == 1
    assert events[0]["event_type"] == event_type
