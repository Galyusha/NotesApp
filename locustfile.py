import random
from locust import HttpUser, task, between


class NotesAppUser(HttpUser):
    wait_time = between(1, 3)

    token = None
    username = None
    created_note_ids = []

    def on_start(self):
        self.username = f"testuser_{random.randint(1, 100000)}"

        self.register()

        self.login()

    def register(self):
        response = self.client.post(
            "/users/register",
            json={"username": self.username, "password": "password123"},
            name="/users/register"
        )

        if response.status_code not in [200, 400]:
            response.failure(
                f"Registration failed with status code: {response.status_code}")

    def login(self):
        response = self.client.post(
            "/users/login",
            json={"username": self.username, "password": "password123"},
            name="/users/login"
        )

        if response.status_code == 200:
            self.token = response.json()["access_token"]
        else:
            response.failure(
                f"Login failed with status code: {response.status_code}")

    @task(3)
    def get_notes(self):
        if not self.token:
            return

        headers = {"Authorization": f"Bearer {self.token}"}
        self.client.get(
            "/notes/",
            headers=headers,
            name="/notes/ (GET)"
        )

    @task(2)
    def create_note(self):
        if not self.token:
            return

        headers = {"Authorization": f"Bearer {self.token}"}
        note_data = {
            "title": f"Test Note {random.randint(1, 1000)}",
            "content": f"This is a test note created at {self.username}"
        }

        response = self.client.post(
            "/notes/",
            json=note_data,
            headers=headers,
            name="/notes/ (POST)"
        )

        if response.status_code == 200:
            note_id = response.json()["id"]
            self.created_note_ids.append(note_id)

    @task(1)
    def update_note(self):
        if not self.token or not self.created_note_ids:
            return

        headers = {"Authorization": f"Bearer {self.token}"}
        note_id = random.choice(self.created_note_ids)
        updated_data = {
            "title": f"Updated Note {random.randint(1, 1000)}",
            "content": f"This note was updated by {self.username}"
        }

        self.client.put(
            f"/notes/{note_id}",
            json=updated_data,
            headers=headers,
            name="/notes/{note_id} (PUT)"
        )

    @task(1)
    def delete_note(self):
        if not self.token or not self.created_note_ids:
            return

        headers = {"Authorization": f"Bearer {self.token}"}
        note_id = self.created_note_ids.pop() if self.created_note_ids else None

        if note_id:
            self.client.delete(
                f"/notes/{note_id}",
                headers=headers,
                name="/notes/{note_id} (DELETE)"
            )


class NotesAppReadOnlyUser(HttpUser):
    wait_time = between(1, 5)

    token = None
    username = None

    def on_start(self):
        self.username = f"readonly_{random.randint(1, 100000)}"

        response = self.client.post(
            "/users/register",
            json={"username": self.username, "password": "password123"},
            name="/users/register (readonly)"
        )

        response = self.client.post(
            "/users/login",
            json={"username": self.username, "password": "password123"},
            name="/users/login (readonly)"
        )

        if response.status_code == 200:
            self.token = response.json()["access_token"]

    @task
    def get_notes_repeatedly(self):
        if not self.token:
            return

        headers = {"Authorization": f"Bearer {self.token}"}
        self.client.get(
            "/notes/",
            headers=headers,
            name="/notes/ (GET readonly)"
        )
