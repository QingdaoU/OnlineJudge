from django.urls import path
from .views import DashboardAdminAPI

urlpatterns = [
    path("dashboard/", DashboardAdminAPI.as_view(), name="dashboard_admin_api"),
]
