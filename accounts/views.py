from django.shortcuts import render
from rest_framework.viewsets import ModelViewSet
from .models import User, Role
from .serializers import UserSerializer, RoleSerializer

class RoleViewSet(ModelViewSet):
    queryset = Role.objects.all()
    serializer_class = RoleSerializer


class UserViewSet(ModelViewSet):
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer