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
from .models import UserData
import os
from django.conf import settings

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from statsmodels.tsa.statespace.sarimax import SARIMAX
import matplotlib.pyplot as plt
from statsmodels.tsa.statespace.sarimax import SARIMAX
from sklearn.metrics import mean_absolute_percentage_error



# Create your views here.
def index(request) :
    return render(request , 'index.html')

def inventory_view(request):
    return render(request, "inventory.html")

def render_login(request):
    return render(request, 'login.html')  # Ensure this exists in 'templates/'

def user_login(request):
    return render(request, 'login.html')


def render_signup(request):
    return render(request,'signup.html')



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
            return redirect('login_page')

        except Exception as e:
            messages.error(request, f"An error occurred: {str(e)}")
            return redirect('signupPage')

    # If the request method is not POST
    return HttpResponse('404 - Not Found', status=404)


from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, logout, login as auth_login

def login(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        

        user = authenticate(request, username=username, password=password)
        if user is not None:
            auth_login(request, user)  
            messages.success(request, "Successfully Logged In")
            return redirect('home')
        else:
            messages.error(request, "Invalid Credentials, Please try again")
            return redirect('login_page')

    return render(request, "login.html")


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
    print(inventory_items)

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
def analysis(request):
    try:
        # Fetch Inventory Data
        inventory_data = list(Inventory.objects.values())

        # Fetch Waste Data
        waste_data = list(Waste.objects.values())

        # Get Ingredient Forecast Data
        forecast_response = get_ingredient_data()

        # If forecast_response is a JsonResponse, extract JSON content
        if isinstance(forecast_response, JsonResponse):
            forecast_data = forecast_response.content.decode('utf-8')
        else:
            forecast_data = {}

        # Combine All Data
        response_data = {
            "inventory": inventory_data,
            "waste": waste_data,
            "forecast": forecast_data,
        }

        return JsonResponse(response_data, safe=False)

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
    

import os
import pandas as pd
import numpy as np
from django.http import JsonResponse
from statsmodels.tsa.statespace.sarimax import SARIMAX
def get_ingredient_data():
    try:
        # Load Data
        file_path = os.path.join(os.path.dirname(__file__), "Balaji_Fast_Food_Sales_Final_Complete.csv")
        df = pd.read_csv(file_path)
        df.columns = df.columns.str.strip()
        df["date"] = pd.to_datetime(df["date"], errors="coerce")
        df.dropna(subset=["date"], inplace=True)  # Remove invalid dates

        # Remove duplicate dates to avoid reindexing issues
        df = df.drop_duplicates(subset=["date"])

        # Set date as index and ensure frequency
        df = df.set_index("date")
        df = df.asfreq("D")  # Setting frequency to daily

        # Fill missing values with 0 (optional, if needed)
        df = df.fillna(0)

        # Extract Time Features
        df["weekday"] = df.index.day_name()
        df["month"] = df.index.month
        df["season"] = df["month"].map(lambda x: "Winter" if x in [12,1,2] else 
                                                 "Spring" if x in [3,4,5] else 
                                                 "Summer" if x in [6,7,8] else "Fall")

        # Process Ingredients
        df["Ingredients"] = df["Ingredients"].apply(lambda x: x.split(", ") if isinstance(x, str) else [])

        # Aggregate Ingredient Consumption
        ingredient_usage = []
        for _, row in df.iterrows():
            for ingredient in row["Ingredients"]:
                if ingredient.lower() != "seasoning":  # Exclude "seasoning"
                    ingredient_usage.append({"date": row.name, "ingredient": ingredient, "consumption": row["quantity"]})

        # Convert to DataFrame
        ingredient_df = pd.DataFrame(ingredient_usage)
        if ingredient_df.empty:
            return JsonResponse({"error": "No ingredient data found."}, status=400)

        # Group and reshape the data
        ingredient_df = ingredient_df.groupby(["date", "ingredient"])["consumption"].sum().unstack().fillna(0)

        # Forecast Function
        def forecast_all_ingredients(steps=7):
            forecast_data = {}

            for ingredient in ingredient_df.columns:
                data = ingredient_df[ingredient]
                train = data[:-steps]

                # Check if sufficient data exists for SARIMAX
                if len(train) < 10:  
                    continue  

                try:
                    model = SARIMAX(train, order=(1,1,1), seasonal_order=(1,1,1,7))
                    model_fit = model.fit(disp=False)  # Suppress warnings
                    forecast = model_fit.forecast(steps=steps)

                    forecast_data[ingredient] = forecast.sum()  # Sum for total consumption

                except Exception as e:
                    print(f"Error forecasting {ingredient}: {e}")
                    continue

            # Convert forecast to DataFrame & Get Top 10 Ingredients
            if not forecast_data:
                return {"error": "No forecast could be generated."}

            forecast_df = pd.DataFrame.from_dict(forecast_data, orient='index', columns=['Predicted Consumption'])
            forecast_df = forecast_df.nlargest(10, 'Predicted Consumption')
            return forecast_df.to_dict(orient="index")  # Convert to JSON-friendly format

        # Run Forecast
        forecast_dict = forecast_all_ingredients(steps=7)

        return JsonResponse(forecast_dict, safe=False)
    
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
    

def render_analysis(request) :
    return render(request ,'analytics.html')
