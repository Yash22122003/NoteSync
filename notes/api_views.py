from rest_framework import viewsets
from rest_framework.authentication import SessionAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework import status
from django.core.cache import cache
from django.contrib.auth.models import User
from .models import Note
from .serializers import NoteSerializer
from rest_framework.decorators import action
from rest_framework import status

class NoteViewSet(viewsets.ModelViewSet):
    """
    DRF API for Notes.

    - Users can access only their own notes.
    - User is assigned automatically during creation.
    - Note list is cached in Redis.
    - Cache is invalidated whenever a note is created,
      updated, or deleted.
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
    @action(detail=True, methods=["post"])
    def share(self, request, pk=None):
        note = self.get_object()

        if note.user != request.user:
            return Response(
                {"error": "Only the note owner can share this note."},
                status=status.HTTP_403_FORBIDDEN,
            )

        username = request.data.get("username")

        if not username:
            return Response(
                {"error": "Username is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            return Response(
                {"error": "User not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        if user == request.user:
            return Response(
                {"error": "You already own this note."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        note.collaborators.add(user)

        return Response({
            "message": f"Note shared with {username}."
        })