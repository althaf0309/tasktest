from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    ROLE_CHOICES = (
        ('superadmin', 'Super Admin'),
        ('admin', 'Admin'),
        ('user', 'User'),
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='user')
    email = models.EmailField(unique=True, blank=False)

    # We treat email as the username field
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']  # because AbstractUser normally requires username

    def __str__(self):
        return f"{self.email} ({self.role})"


class Task(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
    )

    title = models.CharField(max_length=255, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    assigned_to = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tasks', blank=True, null=True)
    due_date = models.DateField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    completion_report = models.TextField(blank=True, null=True)
    worked_hours = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)

    def __str__(self):
        return f"{self.title} - {self.status}"
