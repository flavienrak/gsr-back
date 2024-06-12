from rest_framework import status
from rest_framework.response import Response
from .models import *
from .serializers import *
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from rest_framework.decorators import api_view
from django.forms.models import model_to_dict
from django.contrib.auth.hashers import make_password, check_password
from mvola import Mvola
from mvola.tools import Transaction
from os import environ as env
from dotenv import load_dotenv
from rest_framework_simplejwt.tokens import RefreshToken
from django.middleware import csrf
from rest_framework_simplejwt.exceptions import TokenError


load_dotenv()
api = Mvola(
    env.get("CONSUMER_KEY"),
    env.get("SECRET_KEY"),
    status="SANDBOX",
)


@api_view(["GET"])
def getUsers(request):
    users = Users.objects.all()
    serializer = UserSerializer(users, many=True)
    response = Response(serializer.data)
    return response


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

        auth_token = RefreshToken()
        auth_token["id"] = user.id

        return Response(
            {"authToken": str(auth_token)},
            status=status.HTTP_200_OK,
        )
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(["GET"])
def verifyUser(request, email):
    try:
        if not email:
            return Response({"emailRequired": True})

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

        auth_token = RefreshToken()
        auth_token["id"] = user.id

        return Response(
            {"authToken": str(auth_token)},
            status=status.HTTP_200_OK,
        )
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(["GET"])
def getUser(request, id):
    try:
        if not id:
            return Response({"idRequired": True})

        user = Users.objects.filter(id=id).first()

        if not user:
            return Response({"userNotFound": True})

        user_data = model_to_dict(user, exclude=["password"])

        phone_numbers = UserPhoneNumber.objects.filter(userId=id).values(
            "value", "username"
        )
        user_data["telephones"] = list(phone_numbers)
        return Response(
            {"user": user_data},
            status=status.HTTP_200_OK,
        )

    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(["POST"])
def editUser(request, id):
    try:
        data = request.data

        name = data.get("name")
        username = data.get("username")
        biographie = data.get("biographie")
        phones = data.get("phones")

        if not id:
            return Response({"idRequired": True})

        user = Users.objects.filter(id=id).first()
        if not user:
            return Response({"userNotFound": True})

        if phones:
            allItems = UserPhoneNumber.objects.filter(userId=id)
            newItemsSet = set(phones)

            if allItems.exists():
                allValues = {item.value: item for item in allItems}
                allValuesSet = set(allValues.keys())

                itemsToDelete = allValuesSet - newItemsSet
                itemsToAdd = newItemsSet - allValuesSet

                if itemsToDelete:
                    UserPhoneNumber.objects.filter(
                        userId=id, value__in=itemsToDelete
                    ).delete()

                for item in itemsToAdd:
                    UserPhoneNumber.objects.create(userId=user, value=item)

            else:
                for item in newItemsSet:
                    UserPhoneNumber.objects.create(userId=user, value=item)

        if name:
            user.name = name
        if username:
            user.username = username
        if biographie:
            user.biographie = biographie

        user.save()
        user_data = model_to_dict(user)

        user_data["phones"] = list(
            UserPhoneNumber.objects.filter(userId=id).values_list("value", flat=True)
        )

        return Response(
            {"user": user_data},
            status=status.HTTP_200_OK,
        )
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


@api_view(["POST"])
def mvola_payement(request, id):
    try:
        if not id:
            return Response({"idRequired": True})

        user = Users.objects.filter(id=id).first()
        if not user:
            return Response({"userNotFound": True})

        data = request.data

        debit_phone = data.get("debit_phone", "").strip()
        credit_id = data.get("credit_id", "").strip()
        credit_phone = data.get("credit_phone", "").strip()

        if not debit_phone:
            return Response({"debitPhoneRequired": True})
        elif not credit_id:
            return Response({"creditIdRequired": True})
        elif not credit_phone:
            return Response({"creditPhoneRequired": True})

        # res = api.generate_token()
        # if res.success:
        #     api.token = res.response
        # else:
        #     return Response({"tokenFailed": True}, status=status.HTTP_400_BAD_REQUEST)

        credit_user = Users.objects.filter(id=credit_id).first()
        if not credit_user:
            return Response({"creditUserNotFound": True})

        debit_phones = list(
            UserPhoneNumber.objects.filter(userId=id).values_list("value", flat=True),
        )
        if not debit_phones:
            return Response({"noDebitPhones": True})
        elif debit_phone not in debit_phones:
            return Response({"debitPhoneNotFound": True})

        credit_phones = list(
            UserPhoneNumber.objects.filter(userId=id).values_list("value", flat=True),
        )
        if not credit_phones:
            return Response({"noCreditPhones": True})
        elif credit_phone not in credit_phones:
            return Response({"creditPhoneNotFound": True})

        # INITIATE TRANSACTION
        # transaction = Transaction(
        #     transid=f"{phone}-{datetime.now().strftime('%Y%m%d%H%M%S')}",
        #     token=api.token,
        #     user_language="FR",
        #     user_account_identifier=phone,
        #     partner_name="MyAsa",
        #     x_callback_url="",
        #     amount=f"{amount}",
        #     currency="Ar",
        #     original_transaction_reference="orgina",
        #     requesting_organisation_transaction_reference="ozcbajq",
        #     description_text=settings.description_text,
        #     request_date=datetime.now().strftime("%Y-%m-%dT%H:%M:%S.999Z"),
        #     debit=phone,
        #     credit=settings.phone_credit,
        # )

        return Response({"phones": credit_phone}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(["GET"])
def verifyToken(request, token):
    try:
        if not token:
            return Response({"tokenRequired": True})

        decoded_token = RefreshToken(token)
        infos = {
            "id": decoded_token.payload["id"],
            "iat": decoded_token.payload["iat"],
            "exp": decoded_token.payload["exp"],
        }

        return Response({"infos": infos}, status=status.HTTP_200_OK)
    except TokenError:
        return Response({"invalidToken": True}, status=status.HTTP_401_UNAUTHORIZED)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
