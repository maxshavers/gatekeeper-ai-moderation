from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticatedOrReadOnly

from .models import ChatMessage, Classification, ModeratorAction
from .serializers import ChatMessageSerializer, ClassificationSerializer, ModeratorActionSerializer


class ChatMessageViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = ChatMessage.objects.all().prefetch_related("classifications")
    serializer_class = ChatMessageSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]


class ClassificationViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Classification.objects.select_related("message").all()
    serializer_class = ClassificationSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        qs = super().get_queryset()
        status_param = self.request.query_params.get("status")
        if status_param:
            qs = qs.filter(status=status_param)
        return qs


class ModeratorActionViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = ModeratorAction.objects.select_related("classification", "moderator").all()
    serializer_class = ModeratorActionSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
