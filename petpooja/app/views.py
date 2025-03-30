from django.shortcuts import render , redirect , get_object_or_404
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login , logout
from .models import UserData






# Create your views here.
@login_required(login_url='login-page')
def index(request) :
    return render(request , 'index.html')

def inventory_view(request):
    return render(request, "inventory.html")

def login_page(request) :
    return render(request , 'login.html')



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

def move_expired_inventory():
    today = now().date()
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
    # Move expired inventory before rendering the page
    move_expired_inventory()

    # Group inventory by name and sum the quantities
    inventory_items = (
        Inventory.objects
        .values('name')
        .annotate(total_quantity=Sum('quantity'))
        .order_by('name')
    )
    waste_items = Waste.objects.all()

    return render(request, 'test.html', {'inventory_items': inventory_items, 'waste_items': waste_items})
