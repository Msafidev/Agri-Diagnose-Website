from django.contrib import admin
from .models import Subscriber, ContactMessage

@admin.register(Subscriber)
class SubscriberAdmin(admin.ModelAdmin):
    list_display = ('email', 'subscribed_at')
    search_fields = ('email',)


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ("name", "phone", "email", "created_at")
    search_fields = ("name", "phone", "email")
    list_filter = ("created_at",)
    ordering = ("-created_at",)


# @admin.register(Diagnosis)
# class DiagnosisAdmin(admin.ModelAdmin):
#     list_display = ("predicted_label", "confidence", "timestamp", "lat", "lon")
#     search_fields = ("predicted_label",)
#     list_filter = ("timestamp",)
