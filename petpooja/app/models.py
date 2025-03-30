from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.utils.timezone import now
from django.dispatch import receiver


# Create your models here.
class UserData(models.Model) :
    user = models.OneToOneField(User , on_delete=models.CASCADE , name='user')
    restaurant_name = models.CharField(max_length=50)
    restaurant_location = models.CharField(max_length=100)
    
    
    def __str__(self):
        return str(self.restaurant_name)
    
    
    
from django.utils.timezone import now
class Inventory(models.Model):
    name = models.CharField(max_length=100)
    quantity = models.IntegerField(default=0)
    status = models.CharField(max_length=10,default="fresh")  # fresh/expired
    date_added = models.DateField(default=now)
    
    def __str__(self):
        return str(self.name)

    
class Waste(models.Model) :
    name = models.CharField(max_length=50)
    quantity = models.IntegerField(default=0)
    date = models.DateField(auto_now_add=True)

