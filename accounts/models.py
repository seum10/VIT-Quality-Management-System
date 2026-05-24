from django.contrib.auth.models import User
from django.db import models


class Profile(models.Model):
    ROLE_STUDENT = 'student'
    ROLE_FACULTY = 'faculty'
    ROLE_QA_OFFICER = 'qa_officer'
    ROLE_DEVELOPER = 'developer'
    ROLE_PROJECT_MANAGER = 'project_manager'
    ROLE_ADMIN = 'admin'

    ROLE_CHOICES = [
        (ROLE_STUDENT, 'Student'),
        (ROLE_FACULTY, 'Faculty'),
        (ROLE_QA_OFFICER, 'QA Officer'),
        (ROLE_DEVELOPER, 'Developer'),
        (ROLE_PROJECT_MANAGER, 'Project Manager'),
        (ROLE_ADMIN, 'Admin'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(
        max_length=30,
        choices=ROLE_CHOICES,
        default=ROLE_STUDENT
    )
    department = models.CharField(max_length=100, blank=True)
    phone = models.CharField(max_length=20, blank=True)

    def __str__(self):
        return f"{self.user.username} - {self.get_role_display()}"