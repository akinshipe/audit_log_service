from dataclasses import dataclass
from datetime import datetime
from fastapi import HTTPException


class EventQueueDTO:
    """
    Represents an event to be queued for processing, encapsulating all necessary
    information about the event.

    Attributes:
        event_type (str): The type of event, e.g., 'login', 'purchase'.
        timestamp_utc (int): The Unix timestamp (in UTC) when the event occurred.
        customer_id (int): The identifier for the customer associated with the event.
        event_data (dict): A dictionary containing additional data about the event.

    Methods:
        __init__(event_type, timestamp_utc, customer_id, event_data): Initializes a new instance of EventQueueDTO.

    TODO:
        - Consider adding fields like event_source, event_version, and event_id(uuid4 generated).
        - Generate event_id using uuid4 to provide a unique identifier for referencing the event.
    """

    def __init__(
        self,
        event_type: str,
        timestamp_utc: int | None,
        customer_id: int,
        event_data: dict,
    ):
        self.event_type = event_type
        self.customer_id = customer_id
        self.event_data = event_data
        if timestamp_utc is None:
            self.timestamp_utc = int(datetime.utcnow().timestamp())
        else:
            self.timestamp_utc = int(timestamp_utc)


@dataclass
class EventRequestDTO:
    """
    Data transfer object for requesting events, supporting filtering by various criteria.

    """

    event_id: int | None = None
    event_type: str | None = None
    customer_id: int | None = None
    timestamp_start_utc: int | None = None
    timestamp_end_utc: int | None = None
    offset: int = 0
    limit: int = 100

    def __post_init__(self) -> None:
        """
        Post-initialization to validate timestamps and set default values for offset and limit.
        Raises ValueError if the start timestamp is greater than the end timestamp.
        """

        self.validate_timestamps()

        if self.limit > 100:
            self.limit = 100

    def validate_timestamps(self) -> None:
        if self.timestamp_start_utc and self.timestamp_end_utc:
            if self.timestamp_start_utc > self.timestamp_end_utc:
                raise HTTPException(
                    status_code=401, detail="Start time must be before End time."
                )


class EventResponseDTO:
    """
    Data transfer object for responding to event queries, encapsulating the results and metadata for pagination.

    Attributes:
        total_count (int): The total number of events matching the query.
        count (int): The number of events returned in this response.
        offset (int): The offset from the start of the result set.
        events (list[dict]): The list of events, each represented as a dictionary.

    Methods:
        __init__(events, count, offset, total_count): Initializes a new instance of EventResponseDTO.
        to_dict(): Converts the instance to a dictionary for easy serialization.
    """

    total_count: int
    count: int
    offset: int
    events: list[dict]

    def __init__(self, events: list[dict], count: int, offset: int, total_count: int):
        self.count = count
        self.current_offset = offset
        self.events = events
        self.total_count = total_count

    def to_dict(self) -> dict:
        return {
            "total_count": self.total_count,
            "returned_item_count": self.count,
            "offset": self.current_offset,
            "events": self.events,
        }
