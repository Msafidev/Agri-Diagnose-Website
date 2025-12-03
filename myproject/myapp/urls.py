from django.urls import path
from . import views

urlpatterns = [
    path('index/', views.index, name='index'),
    path('technology/', views.technology, name='technology'),
    path('research/', views.research, name='research'),
    path('payment/', views.payment_form, name='payment_form'),
    path('coming/', views.coming_soon, name='coming_soon'),
    path('coming-soon/', views.coming_soon, name='coming_soon'),
    path('contact/', views.contact, name='contact'),
]

