from django.urls import path
from . import views  # Asegúrate de tener vistas definidas en el archivo views.py

urlpatterns = [
    path('example/', views.example_view, name='example'),
]
