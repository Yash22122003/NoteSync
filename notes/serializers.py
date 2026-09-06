from rest_framework import serializers

from .models import Note


class NoteSerializer(serializers.ModelSerializer):
    """
    Minimal serializer for the existing Note model.

    `user` is deliberately NOT included here. That means a client can
    never read, set, or override it via the API — ownership is assigned
    server-side in NoteViewSet.perform_create(), the same way
    notes/views.py already does it (note.user = request.user).
    """

    class Meta:
        model = Note
        fields = ["id", "title", "content", "created_at", "updated_at"]
        read_only_fields = ["id", "created_at", "updated_at"]
