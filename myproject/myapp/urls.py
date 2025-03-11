from django.urls import path
from .views import *

urlpatterns = [
    path('startreseller.com/login', index, name='index'),

     path('startreseller.com/signup', signup2, name='signup2'),

     path('signup_page/', signup_page, name='signup_page'),

       path('forgot-password/', forgot_password, name='forgot_password'),

       path('', coming_soon, name='coming_soon'),
]
