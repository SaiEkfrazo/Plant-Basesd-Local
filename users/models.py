from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.

class User(AbstractUser):
    class Meta:
        db_table = 'User'
    first_name = models.CharField(max_length=100,blank=False,null=False)
    last_name = models.CharField(max_length=100,blank=False,null=False)
    password = models.CharField(max_length=100,blank=True,null=True)
    email = models.EmailField(blank=False,null=False,unique=True)
    phone_number = models.BigIntegerField(blank=True,null=True,unique=True)
    def __str__(self):
        return self.first_name if self.first_name else self.email

