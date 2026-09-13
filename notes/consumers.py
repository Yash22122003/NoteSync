import json

from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from django.db.models import Q
from .models import Note


class NoteConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        self.note_id = self.scope["url_route"]["kwargs"]["note_id"]
        self.user = self.scope["user"]

        if self.user.is_anonymous:
            await self.close()
            return

        note_exists = await self.user_can_access_note()

        if not note_exists:
            await self.close()
            return

        self.room_group_name = f"note_{self.note_id}"

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name,
        )

        await self.accept()

    async def disconnect(self, close_code):
        if hasattr(self, "room_group_name"):
            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name,
            )

    async def receive(self, text_data):
        data = json.loads(text_data)

        content = data.get("content")

        if content is None:
            return

        await self.save_note(content)

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "note_update",
                "content": content,
            },
        )

    async def note_update(self, event):
        await self.send(
            text_data=json.dumps({
                "content": event["content"],
            })
        )

    @database_sync_to_async
    def user_owns_note(self):
        return Note.objects.filter(
            id=self.note_id,
            user=self.user,
        ).exists()

    @database_sync_to_async
    def save_note(self, content):
        Note.objects.filter(
            id=self.note_id
        ).filter(
            Q(user=self.user) |
            Q(collaborators=self.user)
        ).update(content=content)

    @database_sync_to_async
    def user_can_access_note(self):
        return Note.objects.filter(
            id=self.note_id
        ).filter(
            Q(user=self.user) |
            Q(collaborators=self.user)
        ).exists()