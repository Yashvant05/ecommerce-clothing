from django.contrib import admin
from .models import ContactMessage, Order, Product


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
  list_display = ("user", "product_name", "quantity", "total_price", "created_at")
  search_fields = ("user__username", "product_name", "address")
  list_filter = ("created_at",)
  actions = ["mark_as_shipped"]

  def mark_as_shipped(self, request, queryset):
    for order in queryset:
      # TODO: Update an 'is_shipped' status field if you have one in your Order model
      pass
    self.message_user(request, "Selected orders marked as shipped.")

  mark_as_shipped.short_description = "Mark selected orders as shipped"


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
  list_display = ("name", "price", "image_path")
  search_fields = ("name",)


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
  list_display = ("name", "email", "subject")
  search_fields = ("name", "email", "subject")