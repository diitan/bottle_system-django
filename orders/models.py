from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Order(models.Model):
    user = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)

    full_name = models.CharField(max_length=120)
    phone = models.CharField(max_length=20)
    email = models.EmailField()
    birth_year = models.PositiveIntegerField()
    address = models.CharField(max_length=255)

    qty_low = models.PositiveIntegerField(default=0)
    qty_mid = models.PositiveIntegerField(default=0)
    qty_high = models.PositiveIntegerField(default=0)

    delivery_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)

    total_price = models.PositiveIntegerField(default=0)
    is_paid = models.BooleanField(default=False)
    paid_at = models.DateTimeField(null=True, blank=True)

    def calc_total(self):
        return self.qty_low * 50 + self.qty_mid * 60 + self.qty_high * 70

    def __str__(self):
        return f"Order #{self.id} - {self.full_name} - {self.total_price}đ"
from django.db import models

# Create your models here.
