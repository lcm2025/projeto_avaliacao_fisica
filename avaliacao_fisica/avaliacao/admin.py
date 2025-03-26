from django.contrib import admin
from .models import Paciente, Avaliacao  # Importe seus modelos

@admin.register(Paciente)
class PacienteAdmin(admin.ModelAdmin):
    list_display = ('nome', 'sexo', 'data_nascimento', 'telefone')
    search_fields = ('nome', 'telefone')
    list_filter = ('sexo',)
    date_hierarchy = 'data_nascimento'

@admin.register(Avaliacao)
class AvaliacaoAdmin(admin.ModelAdmin):
    list_display = ('paciente', 'data_avaliacao', 'peso', 'altura', 'imc')
    list_filter = ('paciente', 'data_avaliacao')
    search_fields = ('paciente__nome',)
    date_hierarchy = 'data_avaliacao'