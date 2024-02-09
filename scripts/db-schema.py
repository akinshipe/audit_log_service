events_schema = """

CREATE TABLE Events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    event_type VARCHAR NOT NULL,
    timestamp_utc INT NOT NULL,
    customer_id INT NOT NULL,
    event_data JSON
);

CREATE INDEX idx_event_type ON Events(event_type);
CREATE INDEX idx_timestamp_utc ON Events(timestamp_utc);
CREATE INDEX idx_customer_id ON Events(customer_id);

"""
