from django.shortcuts import render , redirect , get_object_or_404
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login , logout
from .models import UserData
import os
from django.conf import settings

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from statsmodels.tsa.statespace.sarimax import SARIMAX
from sklearn.metrics import mean_absolute_percentage_error
import json
from django.shortcuts import render
from django.http import JsonResponse
from ultralytics import YOLO
import re
import base64
import cv2
import numpy as np
import os
from django.conf import settings

# Load the YOLO model (move outside the function for better performance)
model = YOLO('D:/Pet-Pooja/yolo_fruits_and_vegetables_v3.pt')



# Create your views here.
def index(request) :
    return render(request , 'index.html')

def inventory_view(request):
    return render(request, "inventory.html")



def signup(request) :
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        restaurant_name = request.POST['restaurant_name']
        restaurant_location = request.POST['restaurant_location']
        pass1 = request.POST['pass1']
        pass2 = request.POST['pass2']

        if not username.isalnum():
            messages.error(request, "Username must be alphanumeric.")
            return redirect('signupPage')

        if pass1 != pass2:
            messages.error(request, "Passwords do not match.")
            return redirect('signupPage')

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already taken. Please choose another.")
            return redirect('signupPage')

        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already registered. Please use a different email.")
            return redirect('signupPage')

        # Create the user
        try:
            myuser = User.objects.create_user(username, email, pass1)
            myuser.save()
            UserData.objects.create(
                user = myuser ,
                restaurant_name = restaurant_name ,
                restaurant_location = restaurant_location
            )
            

            

            messages.success(request, "Your account has been successfully created.")
            return redirect('login-page')

        except Exception as e:
            messages.error(request, f"An error occurred: {str(e)}")
            return redirect('signupPage')

    # If the request method is not POST
    return HttpResponse('404 - Not Found', status=404)

@login_required
def login(request) :
    if request.method == "POST" :
        username = request.POST['username']
        password = request.POST['password']
        
        user = authenticate(username=username, password=password)

        if user is not None:
            login(request, user)
            messages.success(request, "Successfully Logged In")
            return redirect('Home')
        else:
            messages.error(request, "Invalid Credentials, Please try again")
            return redirect('login-page')

    # If the request method is not POST, redirect or handle accordingly
    return redirect('login-page')


from django.shortcuts import render
from django.utils.timezone import now
from django.db.models.functions import TruncDate
from django.db.models import Sum
from datetime import timedelta
from .models import Inventory, Waste
from django.utils.timezone import now
from django.db.models import Sum, F
from datetime import timedelta
from .models import Inventory, Waste
from django.http import JsonResponse
from datetime import timedelta, date

def move_expired_inventory():
    today = date.today()
    seven_days_ago = today - timedelta(days=7)

    grouped_inventory = (
        Inventory.objects
        .values('date_added', 'name')
        .annotate(total_quantity=Sum('quantity'))
        .order_by('date_added')
    )

    for item in grouped_inventory:
        item_date = item['date_added']
        item_name = item['name']
        item_quantity = item['total_quantity']

        if item_date and (today - item_date).days >= 7:
            Waste.objects.create(name=item_name, quantity=item_quantity)
            Inventory.objects.filter(name=item_name, date_added=item_date).delete()

def test(request):
    # Move expired inventory before returning data
    move_expired_inventory()

    # Group inventory by name, sum quantities, and include date_added
    inventory_items = list(
        Inventory.objects
        .values('name', 'date_added')  # Include date_added
        .annotate(total_quantity=Sum('quantity'))
        .order_by('name')
    )

    # Convert date format for JSON response
    for item in inventory_items:
        item['date_added'] = item['date_added'].strftime('%Y-%m-%d')  # Format date as YYYY-MM-DD

    waste_items = list(Waste.objects.values('name', 'quantity', 'date'))  # Include date

    # Convert waste date format
    for waste in waste_items:
        waste['date'] = waste['date'].strftime('%Y-%m-%d')

    data = menu_analysis()

    most_sold_cleaned = [{"item": key, "quantity": int(value)} for key, value in data[0].items()]
    least_sold_cleaned = [{"item": key, "quantity": int(value)} for key, value in data[1].items()]

    # Return JSON response
    return JsonResponse({
        'inventory_items': inventory_items,
        'waste_items': waste_items,
        'most_sold': most_sold_cleaned,
        'least_sold': least_sold_cleaned
    })
def menu_analysis():
   

    file_path = os.path.join(settings.BASE_DIR, "app", "Balaji_Fast_Food_Sales_Final_Complete.csv")
    df = pd.read_csv(file_path)

    # Convert 'date' column to datetime format
    df['date'] = pd.to_datetime(df['date'])

    # Sort dataset by date in descending order
    df = df.sort_values(by='date', ascending=False)

    # Get the last 7 unique dates
    last_7_dates = df['date'].drop_duplicates().head(7)

    # Filter data for the last 7 unique dates
    df_last_7_days = df[df['date'].isin(last_7_dates)]

    # Group by 'item_name' and sum the 'quantity' sold
    item_sales_last_7_days = df_last_7_days.groupby('item_name')['quantity'].sum()

    # Get the two most sold items
    most_sold_last_7 = item_sales_last_7_days.nlargest(2)

    # Get the two least sold items
    least_sold_last_7 = item_sales_last_7_days.nsmallest(2)
    mostsold=dict(most_sold_last_7)
    leastsold=dict(least_sold_last_7)
    
    return [mostsold , leastsold]



def detect(request):
    if request.method == "POST":
        try:
            # Parse JSON data
            data = json.loads(request.body)
            image_base64 = data.get("image")
            
            if not image_base64:
                return JsonResponse({'success': 'false', 'error': 'No image provided'}, status=400)
            
            # Decode Base64 image
            image_data = base64.b64decode(image_base64)
            
            # Ensure MEDIA_ROOT exists
            os.makedirs(settings.MEDIA_ROOT, exist_ok=True)
            
            # Define save path in MEDIA_ROOT
            save_path = os.path.join(settings.MEDIA_ROOT, 'uploaded_image.jpeg')
            
            # Save the image in JPEG format
            with open(save_path, 'wb') as f:
                f.write(image_data)
            
            # Load the saved image for YOLO prediction
            img = cv2.imread(save_path)
            if img is None:
                return JsonResponse({'success': 'false', 'error': 'Failed to read the uploaded image'}, status=400)

            conf = 0.6
            iou = 0.1
            results = model(save_path, conf=conf, iou=iou)
            
            detected_items = {}
            output_text = results[0].verbose()
            print(output_text)
            
            matches = re.findall(r"(\d+)\s([\w\s/-]+),", output_text)
            for count, item_name in matches:
                item_name = item_name.strip()
                detected_items[item_name] = detected_items.get(item_name, 0) + int(count)
            
            return JsonResponse({
                'success': 'true',
                'detected_items': detected_items,
                'count': len(detected_items),
                'image_path': save_path
            })
        
        except Exception as e:
            print(e)
            return JsonResponse({'success': 'false', 'error': str(e)}, status=500)

    return JsonResponse({'success': 'false', 'error': 'Invalid request method'}, status=405)
