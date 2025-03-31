from django.contrib import admin
from .models import UserData , Inventory,Waste , Sale

# Register your models here.
admin.site.register(UserData)
admin.site.register(Inventory)
admin.site.register(Waste)
admin.site.register(Sale)
