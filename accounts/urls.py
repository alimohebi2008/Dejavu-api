from rest_framework.routers import DefaultRouter
from .views import UserViewSet, RoleViewSet
from django.urls import path, include

router = DefaultRouter()
router.register(r'users', UserViewSet, basename='users')
router.register(r'roles', RoleViewSet, basename='roles')

urlpatterns = [
    path('', include(router.urls)),
]
