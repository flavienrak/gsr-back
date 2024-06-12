from django.urls import path
from . import views

urlpatterns = [
    path("get-users/", views.getUsers, name="get-users"),
    path("auth/register", views.register, name="register"),
    path("auth/login", views.login, name="login"),
    path("token/<str:token>/verify-token", views.verifyToken, name="verify-token"),
    path("user/<str:id>/get-user", views.getUser, name="get-user"),
    path("user/<str:email>/verify-user", views.verifyUser, name="verify-user"),
    path("user/<str:id>/edit-user", views.editUser, name="edit-user"),
    path("user/<str:id>/mvola-payement", views.mvola_payement, name="mvola-payement"),
    # path("user/<str:id>/delete", views.deleteUser, name="delete-user"),
]
