from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('calcular-ruta/', views.calcular_ruta, name='calcular_ruta'),
]
