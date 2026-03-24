from django.contrib import admin
from django.urls import path, include
from core import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('class-results/<int:class_id>/<str:term>/', views.class_results, name='class_results'),
    
    path('', include('core.urls')),   # ← VERY IMPORTANT
]
