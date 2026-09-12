from django.http import response
from locust import HttpUser, task, between
import random
import re
import threading


USERS = [
    ("loadtest1", "LoadTest@12345"),
    ("loadtest2", "LoadTest@12345"),
]


class NoteSyncUser(HttpUser):
    wait_time = between(1, 3)

    user_counter = 0
    counter_lock = threading.Lock()

    def on_start(self):
        with self.counter_lock:
            user_index = NoteSyncUser.user_counter
            NoteSyncUser.user_counter += 1

        username, password = USERS[user_index % len(USERS)]

        print("TRYING LOGIN:", username)

        login_page = self.client.get(
            "/notes/login/",
            name="Login Page"
        )

        csrf_token = re.search(
            r'name="csrfmiddlewaretoken" value="([^"]+)"',
            login_page.text
        ).group(1)

        response = self.client.post(
            "/notes/login/",
            data={
                "username": username,
                "password": password,
                "csrfmiddlewaretoken": csrf_token,
            },
            name="Login",
            allow_redirects=False
        )

        print("LOGIN STATUS:", response.status_code)
    
    @task
    def view_notes(self):
        self.client.get(
            "/api/notes/",
            name="API - View Notes"
        )