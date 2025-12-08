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
    path('start/', views.start, name='start'),

    path("start", views.start_diagnosis, name="start_diagnosis"),
    path("save", views.save_diagnosis, name="save_diagnosis"),
    path("result/<int:pk>", views.result, name="result_page"),

    path("diagnosis/save", views.save_diagnosis, name="save_diagnosis"),

    path('diagnose/start/', views.start_diagnosis, name='start_diagnosis'),
    path('api/predict/', views.predict_disease, name='predict_disease'),

]

