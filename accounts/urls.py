from rest_framework.routers import DefaultRouter
from .views import UserViewSet, RoleViewSet,DashboardView
from django.urls import path, include

router = DefaultRouter()
router.register(r'users', UserViewSet, basename='users')
router.register(r'roles', RoleViewSet, basename='roles')
router.register("dashboard", DashboardView, basename="dashboard")

urlpatterns = [
    path('', include(router.urls)),
]
