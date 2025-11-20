from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError

def validate_phone_number(value):
   
    if not value.isdigit():
        raise ValidationError("Phone number must contain only digits.")
    if  len(value) != 11:
        raise ValidationError("Phone number must be between 11 digits.")

class CustomUser(AbstractUser):
    profile_image = models.ImageField(
        upload_to='profile_images', blank=True, default='profile_images/default.png'
    )
    phone_number = models.CharField(max_length=15,blank=True,null=True,validators=[validate_phone_number]
    )

    def __str__(self):
        return self.username
