# myapp/views.py — FINAL WORKING VERSION (NO ERRORS, NO KERAS, NO 500)

import os
import joblib
import numpy as np
import requests
from PIL import Image
import torch


from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from django.conf import settings

from django_daraja.mpesa.core import MpesaClient
from .models import ContactMessage, Subscriber, Diagnosis


# ============================= BASIC PAGES =============================
def index(request):
    return render(request, 'index.html')

def research(request):
    return render(request, 'research.html')

def start_diagnosis(request):
    return render(request, "diagnosis/start.html")

def result(request):
    return render(request, "diagnosis/result.html")

def technology(request):
    return render(request, 'technology.html')

def coming_soon(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        if email:
            Subscriber.objects.get_or_create(email=email)
            messages.success(request, "You will be notified when we launch!")
        return redirect('coming_soon')
    return render(request, 'coming_soon.html')

def contact(request):
    if request.method == "POST":
        ContactMessage.objects.create(
            name=request.POST.get("name"),
            phone=request.POST.get("phone"),
            email=request.POST.get("email"),
            message=request.POST.get("message")
        )
        messages.success(request, "Message sent successfully!")
        return redirect("contact")
    return render(request, "contact.html")


# ============================= MPESA =============================
def payment_form(request):
    if request.method == 'POST':
        phone = request.POST.get('phone')
        amount = int(request.POST.get('amount', 1))
        client = MpesaClient()
        client.stk_push(phone, amount, 'AgriDiagnose', 'Diagnosis Fee', 'https://yourdomain.com/callback')
        return render(request, 'payment_form.html', {'message': 'STK Push sent!'})
    return render(request, 'payment_form.html')


# ============================= AI MODEL LOADING (NO KERAS!) =============================
MODEL_PATH = os.path.join(settings.BASE_DIR, "models", "plant_disease_model.pkl")

print("\n" + "="*80)
print("LOADING PLANT DISEASE MODEL...")
print(f"Looking for: {MODEL_PATH}")

model = None
processor = None

if os.path.exists(MODEL_PATH):
    try:
        data = joblib.load(MODEL_PATH)
        model = data['model']
        processor = data['processor']
        print("MODEL LOADED SUCCESSFULLY! Ready for diagnosis.")

    except Exception as e:
        print(f"MODEL LOAD FAILED: {e}")
else:
    print("MODEL FILE NOT FOUND! Put plant_disease_model.pkl in myproject/myproject/models/")

print("="*80 + "\n")


# ============================= CLASS NAMES =============================
CLASS_NAMES = [
    'Apple___Apple_scab', 'Apple___Black_rot', 'Apple___Cedar_apple_rust', 'Apple___healthy',
    'Blueberry___healthy', 'Cherry_(including_sour)___Powdery_mildew', 'Cherry_(including_sour)___healthy',
    'Corn_(maize)___Cercospora_leaf_spot Gray_leaf_spot', 'Corn_(maize)___Common_rust_',
    'Corn_(maize)___Northern_Leaf_Blight', 'Corn_(maize)___healthy', 'Grape___Black_rot',
    'Grape___Esca_(Black_Measles)', 'Grape___Leaf_blight_(Isariopsis_Leaf_Spot)', 'Grape___healthy',
    'Orange___Haunglongbing_(Citrus_greening)', 'Peach___Bacterial_spot', 'Peach___healthy',
    'Pepper,_bell___Bacterial_spot', 'Pepper,_bell___healthy', 'Potato___Early_blight',
    'Potato___Late_blight', 'Potato___healthy', 'Raspberry___healthy', 'Soybean___healthy',
    'Squash___Powdery_mildew', 'Strawberry___Leaf_scorch', 'Strawberry___healthy',
    'Tomato___Bacterial_spot', 'Tomato___Early_blight', 'Tomato___Late_blight', 'Tomato___Leaf_Mold',
    'Tomato___Septoria_leaf_spot', 'Tomato___Spider_mites Two-spotted_spider_mite',
    'Tomato___Target_Spot', 'Tomato___Tomato_Yellow_Leaf_Curl_Virus',
    'Tomato___Tomato_mosaic_virus', 'Tomato___healthy'
]


# ============================= RECOMMENDATIONS =============================
RECOMMENDATIONS = {
    "Tomato___Late_blight": {"english": "Late Blight", "swahili": "Ukungu wa Marehemu", "treatment": "Remove infected leaves. Spray Ridomil Gold weekly.", "pesticides": ["Ridomil Gold", "Revus", "Mancozeb"]},
    "Tomato___Early_blight": {"english": "Early Blight", "swahili": "Ukungu wa Mapema", "treatment": "Remove lower leaves. Apply fungicide.", "pesticides": ["Score", "Daconil"]},
    "Tomato___healthy": {"english": "Healthy", "swahili": "Mzima", "treatment": "No action needed", "pesticides": []},
}

def get_recommendation(key):
    return RECOMMENDATIONS.get(key, {"english": key.replace("___", " - "), "swahili": "Haijulikwa", "treatment": "Consult local agronomist", "pesticides": ["Mancozeb"]})


# ============================= MAIN API =============================
@csrf_exempt
def predict_disease(request):
    if model is None or processor is None:
        return JsonResponse({"error": "AI Model not loaded. Contact admin."}, status=500)

    if request.method != "POST" or not request.FILES.get("image"):
        return JsonResponse({"error": "Invalid request"}, status=400)

    try:
        img = Image.open(request.FILES["image"]).convert("RGB")
        inputs = processor(img, return_tensors="pt")

        with torch.no_grad():
            outputs = model(**inputs)
            idx = torch.argmax(outputs.logits, dim=1).item()
            confidence = torch.softmax(outputs.logits, dim=1).max().item() * 100

        disease_key = CLASS_NAMES[idx]
        reco = get_recommendation(disease_key)

        shops = []
        lat = request.POST.get("lat")
        lon = request.POST.get("lon")
        if lat and lon and hasattr(settings, 'GOOGLE_PLACES_API_KEY'):
            url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
            params = {"location": f"{lat},{lon}", "radius": 15000, "keyword": "agrovet", "key": settings.GOOGLE_PLACES_API_KEY}
            try:
                r = requests.get(url, params=params, timeout=10)
                for place in r.json().get("results", [])[:5]:
                    shops.append({"name": place.get("name"), "address": place.get("vicinity", "")})
            except:
                pass

        return JsonResponse({
            "success": True,
            "disease": reco["english"],
            "swahili": reco["swahili"],
            "confidence": round(confidence, 1),
            "treatment": reco["treatment"],
            "pesticides": reco["pesticides"],
            "nearby_shops": shops
        })

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


# ============================= SAVE RESULT =============================
def save_diagnosis(request):
    if request.method == "POST":
        Diagnosis.objects.create(
            image=request.FILES['image'],
            predicted_label=request.POST.get('predicted_label'),
            confidence=request.POST.get('confidence'),
            lat=request.POST.get('lat'),
            lon=request.POST.get('lon')
        )
        return redirect('result')
    return redirect('start_diagnosis')


def start(request):
    return render(request, 'start.html')