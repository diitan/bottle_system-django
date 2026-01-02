# orders/urls.py
from django.urls import path
from . import views

app_name = "orders"

urlpatterns = [
    path("order/", views.order_form, name="order_form"),
]
