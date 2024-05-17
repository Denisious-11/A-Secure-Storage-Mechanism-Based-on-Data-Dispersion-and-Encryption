from django.db import models

# Create your models here.

class Users(models.Model):
    u_id=models.IntegerField(primary_key=True)
    username=models.CharField(max_length=255)
    password=models.CharField(max_length=255)
    phone=models.CharField(max_length=255)
    email=models.CharField(max_length=255)


class Files(models.Model):
    f_id=models.IntegerField(primary_key=True)
    filename=models.CharField(max_length=255)
    username=models.CharField(max_length=255)
    date=models.CharField(max_length=255)
    time=models.CharField(max_length=255)
    chunks=models.CharField(max_length=255)

class Keys(models.Model):
    k_id=models.IntegerField(primary_key=True)
    f_id=models.CharField(max_length=255)
    key=models.BinaryField()#CharField(max_length=255)
    nonce=models.BinaryField()#CharField(max_length=255)


