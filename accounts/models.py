from django.db import models
from django.contrib.auth.models import AbstractUser

from .validators import check_phone_number, check_last_and_first_name


# custom model user .
class User(AbstractUser):
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=150, validators=[check_last_and_first_name])
    last_name = models.CharField(max_length=150, validators=[check_last_and_first_name])
    phone_number = models.CharField(max_length=11, unique=True, validators=[check_phone_number])

