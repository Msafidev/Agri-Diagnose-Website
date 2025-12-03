from django.shortcuts import render,redirect
from django_daraja.mpesa.core import MpesaClient
from django.contrib import messages
from .models import ContactMessage

def research(request):
    return render(request, 'research.html')


def technology(request):
    return render(request, 'technology.html')


def index(request):
    return render(request, 'index.html')

def coming_soon(request):
    return render(request, 'coming_soon.html')

def payment_form(request):
    if request.method == 'POST':
        phone = request.POST.get('phone')
        amount = int(request.POST.get('amount'))

        client = MpesaClient()

        account_ref = 'Msafi Tech'
        desc = 'school fees payment'

        callback_url = 'http://emobilies.co.ke/mpesa/paycallback'

        response =client.stk_push(phone, amount, account_ref, desc,callback_url)
        return render(request, 'payment_form.html', {'message': 'STK push sent'})
    return render(request, 'payment_form.html')

from django.shortcuts import render, redirect
from .models import Subscriber
from django.contrib import messages

def coming_soon(request):
    if request.method == 'POST':
        email = request.POST.get('email')

        if email:
            # Avoid duplicate emails
            Subscriber.objects.get_or_create(email=email)
            messages.success(request, "You will be notified!")
            return redirect('coming_soon')  # reload page

    return render(request, 'coming_soon.html')




def contact(request):
    if request.method == "POST":
        name = request.POST.get("name")
        phone = request.POST.get("phone")
        email = request.POST.get("email")
        message = request.POST.get("message")

        ContactMessage.objects.create(
            name=name,
            phone=phone,
            email=email,
            message=message
        )

        messages.success(request, "Your message has been sent successfully!")
        return redirect("contact")

    return render(request, "contact.html")



# Create your views here.
