from rest_framework import viewsets
from rest_framework.authentication import SessionAuthentication
from rest_framework.permissions import IsAuthenticated

from .models import Note
from .serializers import NoteSerializer


class NoteViewSet(viewsets.ModelViewSet):
    """
    DRF API for Notes: list/create/retrieve/update/partial_update/destroy.

    Ownership rules mirror the existing template views in notes/views.py:
      - get_queryset() restricts every read/write to the caller's own
        notes (same idea as Note.objects.filter(user=request.user)).
        A note belonging to another user is outside this queryset, so
        DRF's generic view machinery returns 404 for it (not 403) --
        this avoids revealing that another user's note even exists.
      - perform_create() assigns request.user server-side; the client
        cannot supply or override the owner (see serializers.py).
    """

    serializer_class = NoteSerializer
    authentication_classes = [SessionAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Note.objects.filter(user=self.request.user).order_by("-updated_at")

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
