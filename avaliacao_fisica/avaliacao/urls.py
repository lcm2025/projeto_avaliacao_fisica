from django.urls import path
from . import views

app_name = 'avaliacao'

urlpatterns = [
    # Páginas principais
    path('pacientes/', views.lista_pacientes, name='lista_pacientes'),
    path('pacientes/novo/', views.novo_paciente, name='novo_paciente'),
    
    # URLs para pacientes específicos
    path('pacientes/<int:paciente_id>/avaliacao/nova/', views.nova_avaliacao, name='nova_avaliacao'),
    path('pacientes/<int:paciente_id>/historico/', views.historico_avaliacoes, name='historico_avaliacoes'),
    
    # Relatório (agora usando ID da avaliação)
    path('avaliacoes/<int:pk>/relatorio/', views.relatorio_completo, name='relatorio_completo'),
]