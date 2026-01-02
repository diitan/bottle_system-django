from django.contrib import admin
from .models import Order

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id','full_name','phone','email','total_price','is_paid','created_at')
    list_filter = ('is_paid','created_at')
    search_fields = ('full_name','phone','email')
from django.contrib import admin

# Register your models here.
