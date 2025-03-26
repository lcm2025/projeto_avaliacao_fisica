from django import forms
from .models import Paciente, Avaliacao
from django.core.validators import MinValueValidator, MaxValueValidator

class PacienteForm(forms.ModelForm):
    class Meta:
        model = Paciente
        fields = '__all__'
        widgets = {
            'data_nascimento': forms.DateInput(attrs={'type': 'date'}),
            'sexo': forms.RadioSelect(),
            'observacoes': forms.Textarea(attrs={'rows': 3}),
        }

class AvaliacaoForm(forms.ModelForm):
    class Meta:
        model = Avaliacao
        exclude = ['paciente', 'data_avaliacao']
        widgets = {
            'observacoes': forms.Textarea(attrs={'rows': 3}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Validações básicas
        self.fields['altura'].validators.extend([MinValueValidator(0.5), MaxValueValidator(2.5)])
        self.fields['peso'].validators.extend([MinValueValidator(20), MaxValueValidator(300)])