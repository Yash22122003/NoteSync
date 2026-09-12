from rest_framework import viewsets
from rest_framework.authentication import SessionAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from django.core.cache import cache

from .models import Note
from .serializers import NoteSerializer


class NoteViewSet(viewsets.ModelViewSet):
    """
    DRF API for Notes: list/create/retrieve/update/partial_update/destroy.

    Ownership rules mirror the existing template views in notes/views.py:
      - get_queryset() restricts every read/write to the caller's own
        notes.
      - perform_create() assigns request.user server-side.
    """

    serializer_class = NoteSerializer
    authentication_classes = [SessionAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Note.objects.filter(
            user=self.request.user
        ).order_by("-updated_at")

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

        cache_key = f"notes:user:{self.request.user.id}"
        cache.delete(cache_key)

    def perform_update(self, serializer):
        serializer.save()

        cache_key = f"notes:user:{self.request.user.id}"
        cache.delete(cache_key)


    def perform_destroy(self, instance):
        cache_key = f"notes:user:{self.request.user.id}"

        instance.delete()

        cache.delete(cache_key)

    def list(self, request, *args, **kwargs):
        cache_key = f"notes:user:{request.user.id}"

        cached_notes = cache.get(cache_key)

        if cached_notes is not None:
            return Response(cached_notes)

        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)

        cache.set(cache_key, serializer.data, 60)

        return Response(serializer.data)