import datetime
import random

import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
import orjson
from requests.adapters import HTTPAdapter

# Updating the connection pool size
connection_session = requests.Session()
adapter = HTTPAdapter(pool_connections=10, pool_maxsize=20)
connection_session.mount("http://", adapter)

NUMBER_OF_REQUESTS = 100_000
NUMBER_OF_THREADS = 16


def send_http_request(session, token):
    url = "http://127.0.0.1:8000/event"
    timeout = 5
    payload = {
        "event_type": f"event{random.choice([x for x in range(10)])}",
        "customer_id": random.choice([x for x in range(10)]),
        "event_data": {
            "custom_data1": f"custom {random.choice([x for x in range(10)])}"
        },
    }
    headers = {"Content-Type": "application/json", "AUTHORIZATION": f"Bearer {token}"}

    # Use the session to send the request
    response = session.post(
        url, data=orjson.dumps(payload), headers=headers, timeout=timeout
    )
    return response.status_code == 200


def get_access_token(session):
    url = "http://127.0.0.1:8000/access-token?valid_minutes=1800"
    timeout = 5

    headers = {"Content-Type": "application/json"}

    # Use the session to send the request
    try:
        response = session.get(url, headers=headers, timeout=timeout)
        if response.status_code != 200:
            raise Exception(
                f"Failed to get access token. code :{response.status_code}, Reason: {response.text}"
            )
        print(response.json())
        return response.json()["token"]
    except Exception as e:
        print(f" ERORR-----------------> Failed to get access token: {str(e)}")
        print(
            " ----------------------------------------->    ARE YOU SURE YOU HAVE STARTED THE APP?"
        )


if __name__ == "__main__":

    print(
        "################################################################ Running LOAD TEST"
    )
    token = get_access_token(connection_session)
    if not token:
        exit()
    start_time = datetime.datetime.now()

    with ThreadPoolExecutor(max_workers=NUMBER_OF_THREADS) as executor:  #
        futures = [
            executor.submit(send_http_request, connection_session, token)
            for _ in range(NUMBER_OF_REQUESTS)
        ]

    success_count = 0
    for future in as_completed(futures):
        if future.result():
            success_count += 1

    total_seconds = (datetime.datetime.now() - start_time).total_seconds()

    print(
        "############################################################## --------------------- > LOAD TEST FINISHED"
    )

    print(
        f"Successful Requests: {success_count}, ----------------------> {int(success_count / total_seconds)} Requests/second"
    )
