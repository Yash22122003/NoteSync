import requests
import time
from concurrent.futures import ThreadPoolExecutor

LOGIN_URL = "http://127.0.0.1:8000/notes/login/"
NOTES_URL = "http://127.0.0.1:8000/notes/"

USERNAME = "loadtest"
PASSWORD = "LoadTest@12345"

TOTAL_REQUESTS = 10
CONCURRENT_USERS = 2


def send_request(i):
    try:
        session = requests.Session()

        # Login
        login_page = session.get(LOGIN_URL)

        # Get CSRF token
        csrf_token = session.cookies.get("csrftoken")

        login_data = {
            "username": USERNAME,
            "password": PASSWORD,
            "csrfmiddlewaretoken": csrf_token,
        }

        session.post(
            LOGIN_URL,
            data=login_data,
            headers={
                "Referer": LOGIN_URL
            }
        )

        # Access authenticated notes page
        start = time.perf_counter()

        response = session.get(NOTES_URL)

        end = time.perf_counter()

        return {
            "status": response.status_code,
            "time": end - start
        }

    except Exception as e:
        return {
            "status": "ERROR",
            "time": 0,
            "error": str(e)
        }


start_time = time.perf_counter()

with ThreadPoolExecutor(max_workers=CONCURRENT_USERS) as executor:
    results = list(
        executor.map(send_request, range(TOTAL_REQUESTS))
    )

end_time = time.perf_counter()

successful = sum(
    1 for result in results
    if result.get("status") == 200
)

failed = TOTAL_REQUESTS - successful

total_time = end_time - start_time

average_time = sum(
    result["time"] for result in results
) / TOTAL_REQUESTS

requests_per_second = TOTAL_REQUESTS / total_time


print()
print("========== AUTHENTICATED LOAD TEST ==========")
print("Concurrent users :", CONCURRENT_USERS)
print("Total requests   :", TOTAL_REQUESTS)
print("Successful       :", successful)
print("Failed           :", failed)
print("Total time       :", round(total_time, 2), "seconds")
print("Requests/second  :", round(requests_per_second, 2))
print("Average latency  :", round(average_time * 1000, 2), "ms")
print("==============================================")