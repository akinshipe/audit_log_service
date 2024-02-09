import threading

from fastapi import FastAPI, Query, Request

from log_service.controllers.auth_controller import AuthController

from log_service.config import LogServiceConfig

from log_service.controllers.event_controller import EventController
from log_service.data.event_dto import EventRequestDTO
from log_service.processors.queue_consumer import QueueConsumer
from log_service.data.request_models import CreateEventModel

app = FastAPI()

consume_queue = True

event_controller = EventController()

config = LogServiceConfig.get_instance()
queue_consumer_thread: threading.Thread | None = None


########################### ENDPOINTS START ##########################################
@app.get("/access-token")
def generate_access_token(valid_minutes: int = Query(default=1800, gt=0)) -> dict:
    return AuthController.generate_access_token(valid_minutes=valid_minutes)


@app.get("/event")
async def get_events(
    request: Request,
    event_id: int | None = None,
    event_type: str | None = None,
    customer_id: int | None = None,
    timestamp_start_utc: int | None = None,
    timestamp_end_utc: int | None = None,
    offset: int | None = None,
    limit: int | None = None,
) -> dict:
    # validate authentication
    AuthController.validate_access_token(request=request)
    request_dto = EventRequestDTO(
        event_id=event_id,
        event_type=event_type,
        customer_id=customer_id,
        timestamp_start_utc=timestamp_start_utc,
        timestamp_end_utc=timestamp_end_utc,
        offset=offset or 0,
        limit=limit or 100,
    )

    return event_controller.get_event(request_dto=request_dto)


@app.post("/event")
async def post_event(request: Request, event: CreateEventModel) -> str:
    AuthController.validate_access_token(request=request)
    return event_controller.create_event(
        event_type=event.event_type,
        timestamp_utc=event.timestamp_utc,
        customer_id=event.customer_id,
        event_data=event.event_data,
    )


# ##################################################### ENDPOINTS  END ##########################################


# ################################# BACKGROUND TASK ##########################################
@app.on_event("startup")
def start_background_thread() -> None:
    """Start background thread to run queue consumer task.

    This function starts a background thread that runs the
    background_task() function at startup.

    background_task() handles continuously consuming events
    from the queue. Starting it in a background thread allows
    the queue consumption to run asynchronously in parallel.

    The background thread is stored globally so it remains alive.

    No return value as it just starts the background thread.
    """

    global queue_consumer_thread
    queue_consumer_thread = threading.Thread(target=background_task)
    queue_consumer_thread.start()


@app.on_event("shutdown")
def stop_background_thread() -> None:
    """Stop the background thread that runs the queue consumer task.

    This function handles shutting down the background thread that was
    started at application startup to run the queue consumer task.

    It sets a flag to signal the consumer to stop fetching new events,
    and then joins the background thread to stop it from running.

    remaining events in the queue will be consumed once this
    shutdown event is triggered.

    No return value as it just stops the background thread.
    """

    global consume_queue
    global queue_consumer_thread

    consume_queue = False

    if queue_consumer_thread is not None:
        queue_consumer_thread.join()


def background_task() -> None:  # todo move into its own module

    """Run continuous background task to consume events from queue.

    This function initializes a QueueConsumer instance and starts an
    infinite loop to continuously monitor and consume events from the
    event queue. Uses the consume queue flag to stop the loop when the
    application is shutting down.

    Any exceptions during consuming events will be caught and printed.

    This allows events to be asynchronously consumed from the queue
    by a background thread.

    Returns:
        None
    """

    queue_consumer = QueueConsumer.get_instance()
    while True:
        # monitor and consume events
        try:
            if not consume_queue and len(queue_consumer.event_queue) == 0:
                break
            queue_consumer.consume_events()
        except Exception as e:
            print("consuming events failed", e)


# ################################# END BACKGROUND TASK ##########################################
