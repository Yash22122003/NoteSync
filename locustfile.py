from locust import HttpUser, task, between
import random
import re

USERS = [
    ("loadtest1", "LoadTest@12345"),
    ("loadtest2", "LoadTest@12345"),
]


class ZyncUser(HttpUser):
    wait_time = between(1, 3)

    def on_start(self):
        username, password = random.choice(USERS)

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