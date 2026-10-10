from django.contrib import admin
from django.utils.html import format_html
from .models import ContactMessage, Order, Product


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
  list_display = (
      "id",
      "user",
      "product_name",
      "quantity",
      "total_price",
      "payment_method",
      "created_at",
  )
  search_fields = ("user__username", "product_name", "address")
  list_filter = ("created_at", "payment_method")
  date_hierarchy = "created_at"  # Adds a nice date drill-down filter at the top
  actions = ["mark_as_shipped"]

  def mark_as_shipped(self, request, queryset):
    for order in queryset:
      pass
    self.message_user(request, "Selected orders marked as shipped.")

  mark_as_shipped.short_description = "Mark selected orders as shipped"


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
  list_display = ("product_thumbnail", "name", "price")
  search_fields = ("name",)
  list_editable = ("price",)  # Allows you to edit prices right from the list view!

  def product_thumbnail(self, obj):
    if obj.image:
      return format_html(
          '<img src="{}" style="width: 45px; height: 45px; object-fit: cover;'
          ' border-radius: 4px;" />',
          obj.image.url,
      )
    return "No Image"

  product_thumbnail.short_description = "Image Preview"


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
  list_display = ("name", "email", "subject", "created_at")
  search_fields = ("name", "email", "subject", "message")
  list_filter = ("created_at",)
  date_hierarchy = "created_at"
  readonly_fields = (
      "name",
      "email",
      "subject",
      "message",
      "created_at",
  )