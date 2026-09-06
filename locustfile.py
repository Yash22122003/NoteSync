from locust import HttpUser, task, between
import random


USERS = [
    ("loadtest1", "LoadTest@12345"),
    ("loadtest2", "LoadTest@12345"),
]


class NoteSyncUser(HttpUser):

    wait_time = between(1, 3)

    def on_start(self):
        username, password = random.choice(USERS)

        self.client.get(
            "/notes/login/",
            name="Login Page"
        )

        self.client.post(
            "/notes/login/",
            data={
                "username": username,
                "password": password,
            },
            name="Login"
        )

    @task
    def view_notes(self):
        self.client.get(
            "/notes/",
            name="View Notes"
        )