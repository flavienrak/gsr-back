from django.db import models

# Create your models here.


class Users(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=25, null=False, blank=False, default="")
    email = models.CharField(max_length=100, null=False, blank=False, default="")
    username = models.CharField(max_length=25, null=False, blank=False, default="")
    password = models.CharField(max_length=250, null=False, blank=False, default="")
    biographie = models.CharField(max_length=250, null=False, blank=False, default="")
    createdAt = models.DateTimeField(auto_now_add=True, null=True)
    updatedAt = models.DateTimeField(auto_now=True, null=True)


class UserPhoneNumber(models.Model):
    id = models.AutoField(primary_key=True)
    userId = models.ForeignKey(Users, on_delete=models.CASCADE)
    value = models.CharField(
        max_length=15, unique=True, null=False, blank=False, default=""
    )
    username = models.CharField(max_length=25, null=False, blank=False, default="")
    createdAt = models.DateTimeField(auto_now_add=True, null=True)
    updatedAt = models.DateTimeField(auto_now=True, null=True)
