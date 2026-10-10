from django.db import models
from django.contrib.auth.models import User

class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product_name = models.CharField(max_length=100)
    product_price = models.FloatField()
    quantity = models.IntegerField()
    total_price = models.FloatField()
    payment_method = models.CharField(max_length=50, default="cod")
    address = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    # payment_method = models.CharField(max_length=10, choices=[('cod', 'Cash on Delivery'), ('online', 'Online')])
    # is_paid = models.BooleanField(default=False)


class ContactMessage(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField()
    subject = models.CharField(max_length=255)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Message from {self.name} ({self.email})"

class Product(models.Model):
  name = models.CharField(max_length=200)
  price = models.DecimalField(max_digits=10, decimal_places=2)
  image_path = models.ImageField(upload_to="products/", blank=True, null=True)
  alt_text = models.CharField(max_length=200, blank=True, null=True)

  def __str__(self):
    return self.name