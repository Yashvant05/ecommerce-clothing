from django.contrib import admin
from django.urls import path
from . import views

admin.site.site_header = "MenTrend Administration"
admin.site.site_title = "MenTrend Admin Portal"
admin.site.index_title = "Welcome to MenTrend Management Dashboard"

urlpatterns = [
    path('', views.index, name='home'),
    path('signup/', views.signup, name='signup'),
    path('login/', views.log_in, name='log_in'),
    path('buynow/', views.buynow, name='buynow'),
    path('logout/', views.logout, name='logout'),
    path('pay/', views.initiate_payment, name='initiate_payment'),  # 👈 for online payment
    path('payment-success/', views.payment_success, name='payment_success'),  # 👈 after payment
    path('forgot-password/', views.forgot_password, name='forgot_password'),
    path('reset-password/<uidb64>/<token>/', views.reset_password, name='reset_password')
]