from django.urls import path

from . import views

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("history/", views.history, name="history"),
    path("classification/<int:classification_id>/action/", views.take_action, name="take_action"),
]
