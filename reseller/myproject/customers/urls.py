from django.urls import path
from .views import *

urlpatterns = [
    path('index/', index, name='index'),

     path('', signup2, name='signup2'),

     path('signup_page/', signup_page, name='signup_page'),
]
