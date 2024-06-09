from django.urls import path
from . import views

urlpatterns = [
    # path("get-users/", views.getUsers, name="get-users"),
    path("auth/register", views.register, name="register"),
    path("auth/login", views.login, name="login"),
    # path("user/<str:id>/delete", views.deleteUser, name="delete-user"),
]
