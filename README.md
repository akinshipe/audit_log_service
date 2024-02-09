# Audit Log Service

Audit Log Service is a mock robust and scalable python-based logging system designed for efficient capturing, storage, and retrieval of audit logs. This service is equipped with JWT-based authentication, making it suitable for a wide range of applications from internal to external system monitoring.

## Why I Chose FastAPI and SQLite3

#### FastAPI Rationale

The decision to utilize FastAPI for the mock Audit Log Service was motivated by my desire to explore the capabilities of it. Fastapi is a new kid on the block that I have not tried out. It has that has recently gained significant attention from the python community . While FastAPI is well-known for its performance in I/O-bound operations and its support for asynchronous request handling, it is important to note that for the specific use case of this service, an asynchronous framework is not a strict requirement.

The architecture of the Audit Log Service is designed to decouple event reception from event processing. This separation allows the system to queue events in memory and process them independently at lazy stable rate. Consequently, even a synchronous framework would suffice, as the non-blocking nature of the event reception would not be a bottleneck in this context.

The choice of FastAPI, in this case, represents a proactive approach to adopting modern frameworks that offer rapid development features, type safety, and the possibility to scale to asynchronous I/O operations should the need arise in the future.


#### Database Selection Rationale

The use of SQLite3 as the database for the mock Audit Log Service was a deliberate choice driven by the context of this project as a mock implementation. The primary considerations were ease of portability and the desire for a straightforward setup process. SQLite3's lightweight nature and file-based approach make it an excellent candidate for applications like this mock project where quick setup and minimal configuration is wanted

Additionally, the decision to use SQLite3 was influenced by me deciding that I do not want to mock database calls in the unit test. By directly utilizing a test database in tests, i eliminated the need for mocked responses as database response.

Furthermore, the choice provided me an opportunity to evaluate SQLite's claims on their website regarding its suitability for medium-sized companies. SQLite's website suggests that it is capable of handling databases for medium sized businesses. Through load testing, the database has indeed proven to be remarkably performant and reliable, exceeding expectations I had for it. That being said, I am yet to be convinced it should be used in production.


#### Architecture Selection Rationale
In the majority of scenarios, the adoption of a decoupled architecture for systems, as exemplified by the Audit Log Service's method of separating event reception from event processing, may not be necessary. This approach, while beneficial for managing high loads by queuing events to be processed at a more controlled rate, often comes with complexities and potential drawbacks that may outweigh its advantages for systems that do not face significant load challenges. For many applications, the operational demands do not justify the need for such an architecture, as they are unlikely to encounter the level of traffic or processing loads where the benefits of decoupling—such as enhanced scalability and resilience under heavy load—would come into play. In these cases, a simpler, synchronous framework could adequately meet the system's needs without the additional complexity, making the decoupled architecture an unnecessary solution for the majority of use cases.

## Service Features

- **Event Logging**: Capture and store detailed event logs with custom data.
- **Secure Access**: JWT authentication to secure endpoints.
- **Asynchronous Processing**: Utilizes a producer-consumer pattern for efficient and load log processing.
- **Flexible Querying**: Retrieve logs based on event type, customer ID, timestamps, and more.
- **Scalable Architecture**: Designed for easy scalability and high performance.

## Getting Started

### Prerequisites

### Installation

You can deploy the Audit Log Service using the provided shell scripts for either a standard deployment or a Docker-based deployment. if you have docker installed, the Docker-Based deployment is probably prefered as you do not need to install anything on your machine directly.

#### Standard Deployment

Requirements for standard deployment

 -- Python (Tested on python 3.10  && 3.11, But I do not see a reason why it should not on python 3.9 and above)

1. Clone the repository or use the downloaded tar.gz archive:

    ```bash
    git clone https://github.com/yourgithubusername/audit-log-service.git


    ```
2. Change directory into the project directory:
   ```bazaar
    cd audit-log-service
   ```

3. Run the deployment script to set up a virtual environment, install dependencies, and start the service:

    ```bash
    ./scripts/deploy.sh
    ```

#### Docker-based Deployment

Ensure Docker is installed on your system and running. Then run the Docker deployment script. This builds the docker image and deploy it to
a docker container with all dependencies installed. it also starts the application and exposes necessary port:
1. Clone the repository or use the downloaded tar.gz archive:

    ```bash
    git clone https://github.com/yourgithubusername/audit-log-service.git


    ```
2. Change directory into the project directory:
   ```bazaar
    cd audit-log-service
   ```
3. Run the docker deployment script
   ```bash
   ./scripts/deploy-docker.sh

   ```

## Usage

### Authentication

Generate an access token to interact with the service:
This endpoint accepts a query parameter:

   1. valid_minutes: Optional [int] : The validity of the access token in minutes. Defaults to 1800 if not specified.

```bash
curl -X 'GET' \
  'http://127.0.0.1:8000/access-token?valid_minutes=1800' \
  -H 'accept: application/json'
```

### Creating Events
With the token, create an event::

Body parameters for creating an event:

1. event_type: string : Type of the event (e.g., "login_attempt" ).

2. timestamp_utc: optional[integer] : Unix timestamp when the event occurred. This uses the current utc time of when the even was received if not provided

3. customer_id: integer : Identifier for the customer id associated with the event.

4. event_data: dict : Additional data about the event. A dictionary of key value pairs. it can be as deep as needed. as this is stored as json in the db. the root dictionary cannot be empty.


```bazaar
curl -X 'POST' \
  'http://127.0.0.1:8000/event' \
  -H 'accept: application/json' \
  -H 'Authorization: Bearer YOUR_ACCESS_TOKEN' \
  -H 'Content-Type: application/json' \
  -d '{
  "event_type": "login_attempt",
  "timestamp_utc": 1609459200,
  "customer_id": 123,
  "event_data": {"success": true, "is_admin": true, "admin_data": {"username": "admin", "permission_level": 3}}
}'

```

### Retrieving Events
With the token Retrieve events using filters:

Query parameters for retrieving events:

1. event_type: optional[string] : Filter events by type.
2. customer_id: optional[integer] : Filter events by customer ID.
3. timestamp_start_utc: optional[integer] : Filter events by timestamp Start
4. timestamp_end_utc: optional[integer] : Filter events by timestamp End
5. offset: optional[integer] : Offset for pagination. defaults to 0 if not specified.
6. limit: optional[integer] : Limit for pagination. defaults to 100 if not specified or a value > 100 is provided.


```bazaar
curl -X 'GET' \
  'http://127.0.0.1:8000/event?event_type=login_attempt&customer_id=123' \
  -H 'accept: application/json' \
  -H 'Authorization: Bearer YOUR_ACCESS_TOKEN'

```


#### API Documentation
For a detailed overview of all API endpoints and their specifications, refer to the Swagger UI documentation hosted at http://127.0.0.1:8000/docs after starting the service.

## Future Enhnacements

#### Distributed Queue System

For production deployments, it is highly recommended to use established distributed systems such as RabbitMQ or Kafka for queue management. These systems offer enhanced reliability and resilience, ensuring that your service can maintain robust performance and handle consumer thread failures effectively.
If you want to use this custom implementation, atleast implement automatic thread recovery for the consumer, this will make the system more resilient. This not only improves fault tolerance but also allows the service to scale more effectively in response to varying loads. Also make sure
you implement proper shut down for the application, so that it processes events in the queue before shutting down to avoid event loss.

#### Use Production Grade Database

In a production environment, given that the service does not require relational database features, transitioning to a key-value store or document-oriented database may offer significant benefits. MongoDB, with its automatic sharding capabilities, presents a robust solution for handling large datasets while also providing scalability and resilience.

For those who prefer to continue using relational databases, PostgreSQL or MySQL are recommended for their production-grade capabilities. Both offer support for indexing JSON fields, which could substantially improve read performance when filtering by various keys. Ensure to leverage their advanced features like connection pooling and JSONB data types for optimized performance and efficient data retrieval.

#### Enhanced Security
For the production version of the Audit Log Service, it is essential to finalize the implementation of the Authentication Controller. This includes setting up a dedicated datastore for managing user credentials and access control. Such a datastore will enable the service to authenticate users reliably before issuing tokens, rather than the current open token generation, which is not secure for production.



All sensitive configuration details and data should be securely managed. This involves:

- Storing all secret keys, access tokens, and sensitive configuration variables in environment variables or a secure vault solution, never hard-coded within the application.
- Implementing proper encryption for sensitive data both at rest and in transit.
- Ensuring that data backups, audit logs, and other sensitive data are securely stored and managed with restricted access, following the principle of least privilege.

#### Production Dependency Management

For the production deployment of the Audit Log Service, it is important to manage dependencies effectively. To this end, the project will separate production and development dependencies into two distinct files:

- `requirements.txt`: This will contain only the essential packages necessary for running the service in a production environment, thus ensuring a lean and secure deployment.

- `dev-requirements.txt`: This will list all packages required for the development process, including testing and linting tools.

Furthermore, to address potential dependency conflicts and ensure consistent, reproducible environments, the project will incorporate a dependency manager such as `pipenv` or `poetry`. These tools are designed to handle package versions and dependencies with greater precision, allowing for:


#### Monitoring, Alerts and Logs

To ensure optimal performance and reliability of the Audit Log Service in a production environment, comprehensive monitoring and alerting mechanisms will be established. These mechanisms will focus on two critical areas: the service endpoints and the queue consumer.


Monitoring will encompass:

- **Endpoint Performance**: Tracking response times, error rates, and throughput of the API endpoints to identify and address potential bottlenecks or failures promptly.

- **Queue Health**: Monitoring the length of the event queue, processing times, and any errors encountered during event consumption. This includes setting thresholds for queue length to identify backlogs before they impact performance.

- **System Resources**: Observing CPU, memory, and disk usage to ensure the service operates within its resource allocation and to prevent resource exhaustion.

#### Alerts

Alerting policies will be configured to notify the development and operations teams of any issues that could affect the service's availability or performance, such as:

- Unexpected spikes in endpoint response times or error rates.
- Queue length exceeding predefined thresholds, indicating a potential slowdown in event processing.
- Resource usage nearing capacity limits.

These monitoring and alerting systems will be instrumental in maintaining the health of the Audit Log Service, enabling proactive management of the infrastructure and quick responses to any issues that arise.

#### Please Note that this is a work in progress and is not yet production-ready and this is not an exhaustive list of todos.

## Development Tools

#### Load test

There is a load testing script in the scripts directory that can be used to simulate a load on the service.
Please confirm that
the application is deployed before running the load test.
You can set the number of requests you want to send to the service and how many threads you want to use in
the python script load_test.py located under tests/load_test directory
This script can be run using the following command:

```bazaar
    scripts/load-test.py
```

#### Unit Test

I wrote some unit tests for the service, it curently sits at 80% coverage. In future I plan to add more tests to 100% coverage.
You can see the tests in the tests directory.
You can view the coverage report by opening the report/index.html file in your browser after running the tests.

You can run the tests using the following command:

```bazaar
   scripts/unit-tests.sh
```

### Development Cleanup

The service has pre-commit, mypy, flake8, and isort installed and setted up. You need to have git installed though.
You can run dev-cleanup by running the script

```bazaar
scripts/dev-cleanup.sh
```
