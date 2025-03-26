from django.urls import path
from . import views

urlpatterns = [
    path('nova/', views.nova_avaliacao, name='nova_avaliacao'),
]
