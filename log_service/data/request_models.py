from pydantic import BaseModel, field_validator


class CreateEventModel(BaseModel):
    """
    A Pydantic model representing the structure and validation for creating new event data.

    This model is used to ensure that incoming data for event creation meets the expected
    format and contains all the necessary information. It includes basic validation to ensure
    that 'event_data' is not empty.

    Attributes:
        event_type (str): Specifies the type of the event (e.g., 'login', 'purchase').
        timestamp_utc (int | None, optional): Represents the Unix timestamp in UTC when the event occurred.
            Defaults to None, which signifies that the timestamp is to be determined at the time of processing.
        customer_id (int): The identifier of the customer associated with the event.
        event_data (dict): A dictionary containing additional details about the event. Must not be empty.

    Methods:
        event_data_not_empty(cls, event_data): A class method used as a validator to ensure 'event_data' is not empty.

    """

    event_type: str
    timestamp_utc: int | None = None
    customer_id: int
    event_data: dict

    @field_validator("event_data")
    def event_data_not_empty(cls, event_data: dict) -> dict:
        """
        Validates that the 'event_data' dictionary is not empty.

        Parameters:
            event_data (dict): The event data to validate.

        Returns:
            dict: The validated event data.

        Raises:
            ValueError: If 'event_data' is empty.
        """
        if len(event_data) == 0:
            raise ValueError("event_data must contain at least one field")
        return event_data
