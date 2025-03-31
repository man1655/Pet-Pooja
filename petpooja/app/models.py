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

class Sale(models.Model):
    order_id = models.CharField(max_length=100, unique=True)
    date = models.DateField(db_index=True)
    item_name = models.CharField(max_length=200, db_index=True)
    item_type = models.CharField(max_length=100)
    item_price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.IntegerField()
    transaction_amount = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_type = models.CharField(max_length=50)
    received_by = models.CharField(max_length=100)
    time_of_sale = models.CharField(max_length=50)  # Changed from TimeField
    ingredients = models.TextField()

    def __str__(self):
        return f"Order {self.order_id} - {self.item_name}"