from threading import RLock
from collections import deque

from log_service.data.event_dto import EventQueueDTO


class QueueProducer:
    """
    Implements a thread-safe singleton queue producer for managing event queuing operations.

    This class is designed to enqueue events in a thread-safe manner, ensuring that events are
    correctly appended to the queue even in a multi-threaded environment. It uses a deque (double-ended queue)
    from the collections module to store the events, providing efficient append operations.

    The QueueProducer class is implemented as a singleton to ensure that only one instance manages
    the event queue across the entire application.

    Attributes:
        _instance (QueueProducer, optional): Class variable to hold the singleton instance.
        _lock (RLock): A reentrant lock to ensure thread-safe operations on the singleton instance and the event queue.
        event_queue (deque[EventQueueDTO | None]): The event queue storing instances of EventQueueDTO.

    Methods:
        __init__(): Initializes a new QueueProducer instance, enforcing the singleton pattern.
        get_instance(): Returns the singleton instance of the QueueProducer class.
        enqueue_event(event: EventQueueDTO): Adds an event to the queue in a thread-safe manner.

    Usage:
        # Getting the singleton instance
        queue_producer = QueueProducer.get_instance()

        # Enqueuing an event
        event = EventQueueDTO(...)
        queue_producer.enqueue_event(event)

    Raises:
        Exception: If an attempt is made to directly instantiate the class instead of using the `get_instance` method.
    """

    _instance = None
    _lock: RLock = RLock()
    event_queue: deque[EventQueueDTO]

    def __init__(self) -> None:
        if QueueProducer._instance:
            raise Exception("This class is a singleton!")
        QueueProducer._instance = self
        self.event_queue = deque()

    @classmethod
    def get_instance(cls) -> "QueueProducer":
        """
        Retrieves the singleton instance of the QueueProducer class, creating it if it does not already exist.

        Returns:
            QueueProducer: The singleton instance of the class.
        """

        if not cls._instance:
            with cls._lock:
                if not cls._instance:
                    cls._instance = QueueProducer()
        return cls._instance

    def enqueue_event(self, event: EventQueueDTO) -> bool:
        """
        Adds an event to the queue in a thread-safe manner.

        Parameters:
            event (EventQueueDTO): The event data transfer object to enqueue.

        Returns:
            bool: Always returns True to indicate the event was successfully enqueued.
        """

        with self._lock:
            self.event_queue.append(event)
        return True
