from django.urls import path
from . import views

urlpatterns = [
    path("get-users/", views.getUsers, name="get-users"),
]
