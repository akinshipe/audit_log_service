import sqlite3

from typing import Any

import orjson

from log_service.config import LogServiceConfig
from log_service.data.event_dto import EventRequestDTO
from sqlite3 import Connection
import logging

logger = logging.getLogger(__name__)


class EventDatabaseAccessor:

    """
    Provides access to the events database, enabling querying and storing of event records.

    This class encapsulates the logic for interacting with the database to perform operations such as retrieving events
    based on specified criteria and inserting new event records. It leverages the LogServiceConfig singleton for
    database configuration details.

    Attributes:
        config (LogServiceConfig): A configuration instance for accessing database settings.

    """

    def __init__(self) -> None:
        """
        Initializes a new instance of the EventDatabaseAccessor class, setting up the configuration instance.
        """
        self.config = LogServiceConfig.get_instance()

    def get_events(self, get_event_dto: EventRequestDTO) -> tuple[list[dict], int]:
        """
        Retrieves events from the database based on the criteria specified in the EventRequestDTO.

        Parameters:
            get_event_dto (EventRequestDTO): The DTO containing filter criteria for the events query.

        Returns:
            tuple[list[dict], int]: A tuple containing a list of event records as dictionaries and the total count of records matching the criteria.

        Raises:
            sqlite3.Error: If an error occurs during the database query execution.
        """
        filters = "WHERE true"

        if get_event_dto.event_id:
            filters += f" AND id = '{get_event_dto.event_id}'"

        if get_event_dto.event_type:
            filters += f" AND event_type = '{get_event_dto.event_type}'"

        if get_event_dto.customer_id:
            filters += f" AND customer_id = {get_event_dto.customer_id}"

        if get_event_dto.timestamp_start_utc:
            filters += f" AND timestamp_utc >= {get_event_dto.timestamp_start_utc}"

        if get_event_dto.timestamp_end_utc:
            filters += f" AND timestamp_utc <= {get_event_dto.timestamp_end_utc}"

        base_sql = f"SELECT * FROM EVENTS {filters}"

        base_sql += " ORDER BY timestamp_utc"
        count_sql = f'{base_sql.replace("*", "COUNT(1)")};'

        sql = (
            base_sql
            + f" LIMIT {get_event_dto.limit if get_event_dto.limit and get_event_dto.limit <= 100 else 100}"
        )
        sql += f" OFFSET {get_event_dto.offset or 0}"

        event_rows, total_count = self.get_events_from_db(sql=sql, count_sql=count_sql)
        events = []

        # parse the event_data from json to dict and populate response items
        for item in event_rows:
            item = dict(item)
            item["event_data"] = (
                orjson.loads(item["event_data"]) if item["event_data"] else {}
            )
            events.append(item)

        return events, total_count

    def get_events_from_db(
        self, sql: str, count_sql: str, conn: Connection | None = None
    ) -> tuple[list, int]:
        """
        Executes the provided SQL query and count query to fetch event records and their total count from the database.

        Parameters:
            sql (str): The SQL query to fetch event records.
            count_sql (str): The SQL query to count the total number of event records matching the criteria.
            conn (Connection | None): An optional existing database connection. If None, a new connection is established.

        Returns:
            tuple[list[Row | None], int]: A tuple containing a list of event rows (as sqlite3.Row) and the total count of records matching the criteria.

        Raises:
            sqlite3.Error: If an error occurs during database operation.
        """
        # todo: implement the code for connection pooling to enable re-using connections
        # todo connection pooling does not come with SQlite3 like other production grade databases

        if conn is None:
            conn = sqlite3.connect(self.config.get_db_url())

        try:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute(count_sql)
            total_count = list(cursor.fetchone())[0]
            cursor.execute(sql)
            event_rows = cursor.fetchall()
            conn.close()
            return event_rows, total_count

        except sqlite3.Error as e:
            logger.error(f"Error while getting events: {e}")
            raise

        finally:
            conn.close()

    def save_events_to_db(
        self,
        insert_data: list[tuple[int, str, int, Any]],
        conn: Connection | None = None,
    ) -> bool:
        """
        Inserts new event records into the database.

        Parameters:
            insert_data (list[tuple]): A list of tuples, each representing the data for one event record to be inserted.
            conn (Connection | None): An optional existing database connection. If None, a new connection is established.

        Returns:
            bool: True if the insert operation was successful, False otherwise.

        Raises:
            sqlite3.Error: If an error occurs during the insert operation.
        """
        if not conn:
            conn = sqlite3.connect(self.config.get_db_url())
        try:
            c = conn.cursor()
            sql = """INSERT INTO Events (customer_id, event_type, timestamp_utc, event_data)
                       VALUES (?, ?, ?, ?)"""

            c.executemany(sql, insert_data)
            conn.commit()
            return True

        except sqlite3.Error as error:  # todo catch specific errors and handle as appropriate
            # roll back transaction if any error occurs and return the events back to the queue for retry
            logger.error("Error while inserting data into sqlite", str(error))
            conn.rollback()
            # return false so as to return failed events back to the queue to be retried
            return False
