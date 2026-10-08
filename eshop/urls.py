from django.contrib import admin
from django.urls import path, include
from mentrend import views

urlpatterns = [
    path('staff/', admin.site.urls),
    path('', include('mentrend.urls'))
]
