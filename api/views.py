from rest_framework.response import Response
from rest_framework import status
from .models import Users
from .serializers import UserSerializer
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from rest_framework.decorators import api_view
from django.forms.models import model_to_dict
from django.contrib.auth.hashers import make_password, check_password


@api_view(["GET"])
def getUsers(request):
    users = Users.objects.all()
    serializer = UserSerializer(users, many=True)
    return Response(serializer.data)


@api_view(["POST"])
def register(request):
    try:
        data = request.data
        required_fields = [
            "name",
            "username",
            "email",
            "password",
        ]

        for field in required_fields:
            value = data.get(field, "")
            if field != "password":
                value = value.strip()
            if not value:
                return Response(
                    {"error": f"{field} is required"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        name = data.get("name").strip().upper()
        username = " ".join(
            word.capitalize() for word in data.get("username").strip().split()
        )
        email = data.get("email").strip()

        # Valider l'email
        try:
            validate_email(email)
        except ValidationError:
            return Response(
                {"error": "Invalid email format"}, status=status.HTTP_400_BAD_REQUEST
            )

        if Users.objects.filter(email=email).exists():
            return Response({"userAlreadyExist": True})

        user_data = {}
        hashed_password = make_password(data.get("password"))
        user_data["password"] = hashed_password

        user_data["name"] = name
        user_data["username"] = username
        user_data["email"] = email

        user = Users.objects.create(**user_data)
        user.save()

        serializedUser = UserSerializer(user)
        return Response({"user": serializedUser.data}, status=status.HTTP_201_CREATED)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(["POST"])
def login(request):
    try:
        email = request.data.get("email")
        password = request.data.get("password")

        if not email or not password:
            return Response({"dataRequired": True})

        email = email.strip()

        # Valider l'email
        try:
            validate_email(email)
        except ValidationError:
            return Response(
                {"error": "Invalid email format"}, status=status.HTTP_400_BAD_REQUEST
            )

        user = Users.objects.filter(email=email).first()
        if not user:
            return Response({"userNotFound": True})

        if not check_password(password, user.password):
            return Response({"incorrectPassword": True})

        serializer = UserSerializer(user)
        return Response({"user": serializer.data}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(["GET"])
def deleteUser(request, id):
    try:
        if not id:
            return Response({"idRequired": True})

        user = Users.objects.filter(id=id).first()
        if not user:
            return Response({"userNotFound": True})

        serializer = UserSerializer(user)
        user.delete()
        return Response({"user": serializer.data}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
