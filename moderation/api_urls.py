from rest_framework.routers import DefaultRouter

from .api_views import ChatMessageViewSet, ClassificationViewSet, ModeratorActionViewSet

router = DefaultRouter()
router.register("messages", ChatMessageViewSet, basename="message")
router.register("classifications", ClassificationViewSet, basename="classification")
router.register("actions", ModeratorActionViewSet, basename="action")

urlpatterns = router.urls
