from log_service.config import LogServiceConfig
from log_service.data.event_dto import EventQueueDTO, EventRequestDTO, EventResponseDTO

from log_service.db_accessors.event_db_accessor import EventDatabaseAccessor
from log_service.processors.queue_producer import QueueProducer
from fastapi import HTTPException


class EventController:
    """
    EventController handles event-related operations within the log service, including creating and retrieving events.

    This class integrates components for event queue processing, configuration management, and database access to
    facilitate the processing and querying of events. It provides methods to enqueue new events and fetch events based
    on specified criteria.

    Attributes:
        queue_processor (QueueProducer): An instance of QueueProducer for event queuing operations.
        config (LogServiceConfig): Configuration instance for accessing global settings.
        database_accessor (EventDatabaseAccessor): Database accessor for event data retrieval and manipulation.

    Methods:
        __init__(): Initializes the EventController with necessary components.
        create_event(event_type, timestamp, customer_id, event_data): Enqueues a new event for processing.
        get_event(request_dto: EventRequestDTO): Retrieves events based on criteria defined in an EventRequestDTO.

    """

    def __init__(self) -> None:
        """
        Initializes the EventController with instances of the queue processor, configuration settings, and database accessor.
        """
        self.queue_processor = QueueProducer.get_instance()
        self.config = LogServiceConfig.get_instance()
        self.database_accessor = EventDatabaseAccessor()

    def create_event(
        self,
        event_type: str,
        timestamp_utc: int | None,
        customer_id: int,
        event_data: dict,
    ) -> str:
        """
        Creates and enqueues an event for processing.

        Parameters:
            event_type (str): The type of the event.
            timestamp_utc (int): The Unix timestamp (in UTC) when the event occurred
            customer_id (int): Identifier of the customer associated with the event.
            event_data (dict): Additional data related to the event.

        Returns:
            str: A message indicating successful receipt and queuing of the event.

        Raises:
            HTTPException: An exception with status code 500 if the event fails to be enqueued.
        """
        event = EventQueueDTO(event_type, timestamp_utc, customer_id, event_data)
        is_queued = self.queue_processor.enqueue_event(event)
        if not is_queued:
            raise HTTPException(
                status_code=500,
                detail="Failed to process event, Something went wrong. Please try again",
            )
        return "Event received and queued successfully"

    def get_event(self, request_dto: EventRequestDTO) -> dict:
        """
        Retrieves events based on criteria specified in the EventRequestDTO.

        Parameters:
            request_dto (EventRequestDTO): Data transfer object containing query criteria.

        Returns:
            dict: A dictionary representing the response, including the events, total count, and pagination details.
        """
        events, count = self.database_accessor.get_events(request_dto)
        events_response_dto = EventResponseDTO(
            events=events,
            total_count=count,
            offset=request_dto.offset,
            count=len(events),
        )
        return events_response_dto.to_dict()
