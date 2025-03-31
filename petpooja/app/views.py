import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from statsmodels.tsa.statespace.sarimax import SARIMAX
from django.http import JsonResponse
import os
from django.shortcuts import render , redirect , get_object_or_404
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login , logout
from .models import UserData,Sale
import os
from django.conf import settings

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from statsmodels.tsa.statespace.sarimax import SARIMAX
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
    # Get last 7 unique dates from database
    last_7_dates = Sale.objects.dates('date', 'day', order='DESC')[:7]
    
    # Get sales data for these dates
    sales_data = Sale.objects.filter(date__in=last_7_dates)
    
    # Create DataFrame from ORM data
    df = pd.DataFrame.from_records(sales_data.values(
        'date', 'item_name', 'quantity'
    ))
    
    # Group and calculate sales
    item_sales = df.groupby('item_name')['quantity'].sum()
    
    most_sold = item_sales.nlargest(2).to_dict()
    least_sold = item_sales.nsmallest(2).to_dict()
    
    return [most_sold, least_sold]
from django.http import JsonResponse
import json

def analysis(request):
    try:
        inventory_data = list(Inventory.objects.values())
        waste_data = list(Waste.objects.values())
        forecast_data = get_ingredient_data()
        
        print(forecast_data)
        return JsonResponse({
            "inventory": inventory_data,
            "waste": waste_data,
            "forecast": forecast_data
        })
    
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
   
    

import os
import pandas as pd
import numpy as np
from django.http import JsonResponse
from statsmodels.tsa.statespace.sarimax import SARIMAX

def get_ingredient_data():
    try:
        # Get sales data from database
        sales_data = Sale.objects.all().values('date', 'quantity', 'ingredients')
        df = pd.DataFrame.from_records(sales_data)

        # Check if sales data exists
        if df.empty:
            return {"error": "No sales data found in database."}

        # Convert date to datetime format
        df['date'] = pd.to_datetime(df['date'], errors='coerce')
        df = df.dropna(subset=['date'])  # Remove rows with invalid dates

        # Process ingredients
        df['Ingredients'] = df['ingredients'].apply(
            lambda x: x.split(", ") if x and isinstance(x, str) else []
        )

        # Create ingredient usage list
        ingredient_usage = []
        for _, row in df.iterrows():
            for ingredient in row['Ingredients']:
                ingredient = ingredient.strip()
                if ingredient.lower() != 'seasoning' and ingredient != '':
                    ingredient_usage.append({
                        'date': row['date'],
                        'ingredient': ingredient,
                        'consumption': row['quantity']
                    })

        # Check if any ingredients were processed
        if not ingredient_usage:  # Proper list emptiness check
            return {"error": "No valid ingredients found in sales data."}

        # Create DataFrame and process
        ingredient_df = pd.DataFrame(ingredient_usage)
        if ingredient_df.empty:  # Proper DataFrame emptiness check
            return {"error": "Failed to create ingredient usage DataFrame."}

        # Pivot the data
        try:
            ingredient_df = ingredient_df.groupby(['date', 'ingredient'])['consumption'] \
                                        .sum().unstack().fillna(0)
        except Exception as e:
            return {"error": f"Data processing failed: {str(e)}"}

        # Forecasting function
        def forecast_all_ingredients(steps=7):
            forecast_data = {}
            required_history = 14

            for ingredient in ingredient_df.columns:
                data = ingredient_df[ingredient]
                
                if len(data) < required_history:
                    continue

                try:
                    train = data[:-steps]
                    last_date = data.index[-1]

                    model = SARIMAX(train,
                                  order=(1, 1, 1),
                                  seasonal_order=(1, 1, 1, 7),
                                  enforce_stationarity=False)
                    model_fit = model.fit(disp=False)
                    forecast = model_fit.get_forecast(steps=steps)
                    
                    forecast_data[ingredient] = {
                        'predicted_total': round(forecast.predicted_mean.sum(), 2),
                        'last_date': last_date.strftime('%Y-%m-%d')
                    }

                except Exception as e:
                    print(f"Skipped {ingredient}: {str(e)}")
                    continue

            return forecast_data or {"error": "No forecasts generated. Check data requirements."}

        # Generate forecast
        forecast_dict = forecast_all_ingredients(steps=7)

        if 'error' in forecast_dict:
            return forecast_dict

        # Return top 10 ingredients
        sorted_forecast = sorted(
            forecast_dict.items(),
            key=lambda x: x[1]['predicted_total'],
            reverse=True
        )[:10]

        return {item[0]: item[1] for item in sorted_forecast}

    except Exception as e:
        return {"error": f"System error: {str(e)}"}
def render_analysis(request) :
    return render(request ,'analytics.html')
