"""
task/urls.py
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    MyTokenObtainPairView,
    register_view,
    login_view,  # optional
    dashboard_view,  # optional
    UserViewSet,
    TaskViewSet
)

router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')
router.register(r'tasks', TaskViewSet, basename='task')

urlpatterns = [
    # /api/users/, /api/tasks/
    path('', include(router.urls)),

    # Registration endpoint => POST /api/register/
    path('register/', register_view, name='register'),

    # Custom token => POST /api/token/custom/ with {email, password}
    path('token/custom/', MyTokenObtainPairView.as_view(), name='custom_token_obtain_pair'),

    # (Optional) If you want to serve these HTML pages under /api/ as well:
    path('login-html/', login_view, name='login_html'),
    path('dashboard-html/', dashboard_view, name='dashboard_html'),
]
