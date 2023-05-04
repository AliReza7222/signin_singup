from django.db import models
from django.contrib.auth.models import AbstractUser


# custom model user .
class User(AbstractUser):
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=11)

