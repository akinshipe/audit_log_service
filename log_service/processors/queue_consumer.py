import sqlite3
import time
from sqlite3 import Connection
from threading import RLock
from collections import deque

import orjson

from log_service.config import LogServiceConfig
from log_service.data.event_dto import EventQueueDTO
from log_service.db_accessors.event_db_accessor import EventDatabaseAccessor
from log_service.processors.queue_producer import QueueProducer
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

CHUNK_SIZE = 30


class QueueConsumer:
    """
    Implements a thread-safe singleton queue consumer for processing and storing events from an event queue.

    This class is responsible for consuming events from a shared event queue managed by a QueueProducer instance,
    processing them in chunks, and saving them to a database using an EventDatabaseAccessor. It maintains performance
    statistics such as the maximum queue length observed. The QueueConsumer is designed to run in a separate thread
    or as part of a scheduled job to regularly consume and process events.

    Attributes:
        _instance (QueueConsumer, optional): Class variable to hold the singleton instance.
        _lock (RLock): A reentrant lock to ensure thread-safe operations on the singleton instance and event consumption.
        event_queue (deque[EventQueueDTO | None]): Reference to the shared event queue from QueueProducer.
        config (LogServiceConfig | None): Configuration instance for accessing database settings.
        max_queue_length (int): Tracks the maximum length the event queue has reached.
        conn (Connection): Database connection used to save events.
        database_accessor (EventDatabaseAccessor): Accessor for interacting with the event database.

    Raises:
        Exception: If an attempt is made to directly instantiate the class instead of using the `get_instance` method.
    """

    _instance = None
    _lock: RLock = RLock()
    event_queue: deque[EventQueueDTO]
    config: LogServiceConfig
    max_queue_length: int = 0
    conn: Connection
    database_accessor: EventDatabaseAccessor
    last_log_time: int
    last_consumed_time: datetime

    def __init__(self) -> None:

        """
        Private constructor to enforce the singleton pattern. Initializes the event queue reference,
        configuration, database accessor, and establishes a database connection.

        Raises:
            Exception: If an attempt is made to instantiate the class directly.
        """

        if QueueConsumer._instance:
            raise Exception("This class is a singleton!")
        self.event_queue = QueueProducer.get_instance().event_queue
        self.config = LogServiceConfig.get_instance()
        self.database_accessor = EventDatabaseAccessor()
        self.conn = sqlite3.connect(self.config.get_db_url())
        self.last_log_time = int(datetime.now().timestamp())
        self.last_consumed_time = datetime.now()
        QueueConsumer._instance = self
        logger.info("QueueConsumer initialized successfully")

    @classmethod
    def get_instance(cls) -> "QueueConsumer":

        """
        Retrieves the singleton instance of the QueueConsumer class, creating it if it does not already exist.

        Returns:
            QueueConsumer: The singleton instance of the class.
        """

        if not cls._instance:
            with cls._lock:
                if not cls._instance:
                    cls._instance = QueueConsumer()
        return cls._instance

    def consume_events(self) -> None:

        """
        Consumes events from the queue in chunks, processes them, and saves them to the database.
        If the queue is empty, it briefly sleeps before checking again. Performance stats are logged.
        """

        queue_length = len(self.event_queue)

        if queue_length == 0:
            self._log_event_performance_stats(
                f" ####### No events in queue ------------> Queue Consumer currently sleeping. Last event consumed at {self.last_consumed_time}"
            )

            time.sleep(0.1)
            return

        if queue_length > self.max_queue_length:
            self.max_queue_length = queue_length

        self._log_event_performance_stats()

        with self._lock:

            queue_length = len(self.event_queue)
            if not queue_length:
                return

            chunk_size = CHUNK_SIZE if queue_length > CHUNK_SIZE else queue_length

            events = []

            for i in range(chunk_size):
                events.append(self.event_queue.popleft())

        self._save_event(events)

    def _save_event(self, events: list[EventQueueDTO]) -> None:

        """
        Saves a list of events to the database. If saving fails, events are returned to the queue for retrying.

        Parameters:
            events (list[EventQueueDTO]): The list of events to be saved.

        Note:
            - Connection recycling and retry logic should be implemented for robustness.
        """

        insert_data = [
            (
                event.customer_id,
                event.event_type,
                event.timestamp_utc,
                orjson.dumps(event.event_data),
            )
            for event in events
            if event is not None
        ]

        if (
            not self.conn
        ):  # todo recycle connection after x amount usage to avoid it being stale
            self.conn = sqlite3.connect(self.config.get_db_url())

        is_successful = self.database_accessor.save_events_to_db(
            insert_data, conn=self.conn
        )

        #  return failed events back to the queue to be retried
        #  todo there should be some logic surrounding events that have been retried a couple of times and still fails
        if not is_successful:
            with self._lock:
                for event in events:
                    self.event_queue.append(event)
        else:
            self.last_consumed_time = datetime.now()

    def _log_event_performance_stats(self, message: str | None = None) -> None:
        """
        Logs the current queue length and the maximum queue length observed for performance monitoring.
        """
        performance_message = f" current queue lag: {len(self.event_queue)}, max queue lag: {self.max_queue_length} "

        if int(datetime.now().timestamp()) > self.last_log_time + 5:
            if message:
                logger.error(message + performance_message)
            else:
                logger.error(performance_message)

            self.last_log_time = int(datetime.now().timestamp())
