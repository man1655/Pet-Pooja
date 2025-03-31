from django.urls import path
from . import views

urlpatterns = [
     path('', views.render_login, name="login_page"),  # Ensure this is correct
    path("inventory", views.inventory_view, name="inventory"),
    path('signup', views.signup, name='signup'),
    path('login', views.login, name='login'),  # Changed from `views.login`
    path('test/', views.test, name='test'),
    path('home', views.index, name='home'),  # Ensure trailing slash
    path('signup-page',views.render_signup,name='signup-page'),
    path('analysis',views.analysis,name='analysis'),
    path('render_analysis' ,views.render_analysis , name = 'ren_an')
]
