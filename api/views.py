from rest_framework.response import Response
from rest_framework.decorators import api_view
from .models import Users
from .serializers import UserSerializer


@api_view(["GET"])
def getUsers(request):
    users = Users.objects.all()
    serializer = UserSerializer(users, many=True)
    return Response(serializer.data)
