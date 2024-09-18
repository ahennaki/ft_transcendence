from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ChatsView

urlpatterns = [
    path('chats/', ChatsView.as_view()),
]