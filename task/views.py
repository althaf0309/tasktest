"""
task/views.py
"""
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action, api_view
from rest_framework_simplejwt.views import TokenObtainPairView

from .models import User, Task
from .serializers import (
    MyTokenObtainPairSerializer,
    UserSerializer,
    TaskSerializer
)

# 1) Custom JWT (POST /api/token/custom/)
class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer


# 2) Registration Endpoint
@api_view(['POST'])
def register_view(request):
    """
    Create a new user. 
    If you want to require superadmin for all user creation, uncomment the lines checking for role.
    """
    # if not request.user.is_authenticated or request.user.role != 'superadmin':
    #     return Response({'detail': 'Not authorized'}, status=status.HTTP_403_FORBIDDEN)
    serializer = UserSerializer(data=request.data)
    if serializer.is_valid():
        role = request.data.get('role', 'user')
        serializer.save(role=role)
        return Response({
            'message': 'Registration successful!',
            'user': serializer.data
        }, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# 3) For HTML login page
def login_view(request):
    return render(request, 'login.html')

# 4) For HTML tasks (or dashboard)
@login_required
def dashboard_view(request):
    return render(request, 'dashboard.html')

# 5) Users
class UserViewSet(viewsets.ModelViewSet):
    """
    superadmin can create, update, delete any user. 
    normal user sees only themselves (GET /users/ => [themselves]).
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    
    def get_queryset(self):
        user = self.request.user
        if user.role == 'superadmin':
            return User.objects.all()
        return User.objects.filter(id=user.id)
    
    def create(self, request, *args, **kwargs):
        # Only superadmin can create from this endpoint
        if request.user.role != 'superadmin':
            return Response({'detail': 'Not authorized'}, status=status.HTTP_403_FORBIDDEN)
        return super().create(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        # Only superadmin can update user roles, etc.
        if request.user.role != 'superadmin':
            return Response({'detail': 'Not authorized'}, status=status.HTTP_403_FORBIDDEN)
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        # Only superadmin can delete a user
        if request.user.role != 'superadmin':
            return Response({'detail': 'Not authorized'}, status=status.HTTP_403_FORBIDDEN)
        return super().destroy(request, *args, **kwargs)


# 6) Tasks
class TaskViewSet(viewsets.ModelViewSet):
    """
    Admin/superadmin can create tasks. 
    Normal user sees only tasks assigned to them and can only mark them completed if assigned to them.
    """
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role == 'superadmin':
            return Task.objects.all()
        elif user.role == 'admin':
            return Task.objects.all()
        else:
            return Task.objects.filter(assigned_to=user)

    def create(self, request, *args, **kwargs):
        if request.user.role not in ['admin', 'superadmin']:
            return Response({'detail': 'Not authorized'}, status=status.HTTP_403_FORBIDDEN)
        return super().create(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        data = request.data
        # If marking completed => user must be assigned and provide report/hours
        if 'status' in data and data['status'] == 'completed':
            if request.user.role == 'user':
                if instance.assigned_to != request.user:
                    return Response({'detail': 'Not your task'}, status=status.HTTP_403_FORBIDDEN)
                if 'completion_report' not in data or 'worked_hours' not in data:
                    return Response({
                        'detail': 'Must provide completion_report and worked_hours when completing a task.'
                    }, status=status.HTTP_400_BAD_REQUEST)
        return super().update(request, *args, **kwargs)

    @action(detail=True, methods=['get'])
    def report(self, request, pk=None):
        task = get_object_or_404(Task, pk=pk)
        if task.status != 'completed':
            return Response({'detail': 'Task not completed yet'}, status=status.HTTP_400_BAD_REQUEST)
        if request.user.role in ['admin', 'superadmin']:
            return Response({
                'completion_report': task.completion_report,
                'worked_hours': task.worked_hours
            })
        return Response({'detail': 'Not authorized'}, status=status.HTTP_403_FORBIDDEN)
