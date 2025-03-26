from django import forms
from .models import AvaliacaoFisica

class AvaliacaoFisicaForm(forms.ModelForm):
    class Meta:
        model = AvaliacaoFisica
        fields = ['data_nascimento', 'metabolismo_basal', 'idade_corporal', 'gordura_visceral', 'imc', 'torax', 'axilar', 'abdomen', 'coxa']  # Incluindo os campos desejados