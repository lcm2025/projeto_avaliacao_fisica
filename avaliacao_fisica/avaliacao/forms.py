from django import forms
from .models import Paciente, Avaliacao
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone

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
    # Campo de data explícito
    data_avaliacao = forms.DateField(
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'form-control',
            'required': 'required'
        }),
        input_formats=['%Y-%m-%d'],
        required=True,
        initial=timezone.now().date()
    )
    # Validação personalizada para dobras cutâneas
    def validate_dobra(value):
        if value is not None and (value < 3 or value > 60):
            raise forms.ValidationError("A dobra deve estar entre 3 e 60 mm")

    class Meta:
        model = Avaliacao
        fields = [
            'data_avaliacao',
            'protocolo',
            'altura',
            'peso',
            'percentual_gordura',
            'massa_magra',
            'gordura_visceral',
            'tmb',
            'idade_metabolica',
            'observacoes',
            # Dobras cutâneas
            'torax',
            'triceps',
            'abdominal',
            'coxa',
            'axilar_media',
            'subescapular',
            'suprailiaca',
            # Medidas antropométricas
            'braco_direito',
            'braco_esquerdo',
            'antebraco_direito',
            'antebraco_esquerdo',
            'cintura',
            'quadril',
            'tronco',
            'abdomen',
            'coxa_direita',
            'coxa_esquerda',
            'panturrilha_direita',
            'panturrilha_esquerda'
        ]
        widgets = {
            'protocolo': forms.Select(attrs={
                'class': 'form-select',
                'onchange': 'toggleProtocolFields()'  # JavaScript para alternar campos
            }),
            'observacoes': forms.Textarea(attrs={'rows': 3}),
            'torax': forms.NumberInput(attrs={'step': '0.1', 'class': 'dobra-input'}),
            'triceps': forms.NumberInput(attrs={'step': '0.1', 'class': 'dobra-input'}),
            'abdominal': forms.NumberInput(attrs={'step': '0.1', 'class': 'dobra-input'}),
            'coxa': forms.NumberInput(attrs={'step': '0.1', 'class': 'dobra-input'}),
            'axilar_media': forms.NumberInput(attrs={'step': '0.1', 'class': 'dobra-input'}),
            'subescapular': forms.NumberInput(attrs={'step': '0.1', 'class': 'dobra-input'}),
            'suprailiaca': forms.NumberInput(attrs={'step': '0.1', 'class': 'dobra-input'}),
            'braco_direito': forms.NumberInput(attrs={'step': '0.1', 'class': 'medida-input'}),
            'braco_esquerdo': forms.NumberInput(attrs={'step': '0.1', 'class': 'medida-input'}),
            'antebraco_direito': forms.NumberInput(attrs={'step': '0.1', 'class': 'medida-input'}),
            'antebraco_esquerdo': forms.NumberInput(attrs={'step': '0.1', 'class': 'medida-input'}),
            'cintura': forms.NumberInput(attrs={'step': '0.1', 'class': 'medida-input'}),
            'quadril': forms.NumberInput(attrs={'step': '0.1', 'class': 'medida-input'}),
            'tronco': forms.NumberInput(attrs={'step': '0.1', 'class': 'medida-input'}),
            'abdomen': forms.NumberInput(attrs={'step': '0.1', 'class': 'medida-input'}),
            'coxa_direita': forms.NumberInput(attrs={'step': '0.1', 'class': 'medida-input'}),
            'coxa_esquerda': forms.NumberInput(attrs={'step': '0.1', 'class': 'medida-input'}),
            'panturrilha_direita': forms.NumberInput(attrs={'step': '0.1', 'class': 'medida-input'}),
            'panturrilha_esquerda': forms.NumberInput(attrs={'step': '0.1', 'class': 'medida-input'}),
        }
        labels = {
            
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Validações básicas
        self.fields['altura'].validators.extend([MinValueValidator(0.5), MaxValueValidator(2.5)])
        self.fields['peso'].validators.extend([MinValueValidator(20), MaxValueValidator(300)])
        
        # Torna todos os campos de dobras não obrigatórios inicialmente
        dobra_fields = ['triceps', 'subescapular', 'torax', 'abdominal', 
                       'coxa', 'axilar_media', 'suprailiaca']
        for field in dobra_fields:
            self.fields[field].required = False
            
        medidas_fields = [
            'braco_direito', 'braco_esquerdo', 'antebraco_direito', 'antebraco_esquerdo',
            'cintura', 'quadril', 'tronco', 'abdomen',
            'coxa_direita', 'coxa_esquerda', 'panturrilha_direita', 'panturrilha_esquerda'
        ]
        for field in medidas_fields:
            self.fields[field].required = False
            self.fields[field].validators.append(self.validate_dobra)

    def clean(self):
        cleaned_data = super().clean()
        protocolo = cleaned_data.get('protocolo')
        
        # Se não foi selecionado protocolo ou é None, não valida dobras
        if not protocolo:
            return cleaned_data
        
        # Verifica se pelo menos um método foi preenchido (dobras OU bioimpedância)
        tem_bioimpedancia = any([
            cleaned_data.get('percentual_gordura'),
            cleaned_data.get('massa_magra'),
            cleaned_data.get('gordura_visceral')
        ])
        
        tem_dobras = any([
            cleaned_data.get('triceps'),
            cleaned_data.get('subescapular'),
            cleaned_data.get('torax'),
            cleaned_data.get('abdominal'),
            cleaned_data.get('coxa'),
            cleaned_data.get('axilar_media'),
            cleaned_data.get('suprailiaca')
        ])
        
        if not tem_bioimpedancia and not tem_dobras:
            raise forms.ValidationError(
                "Informe pelo menos os dados de bioimpedância ou as dobras cutâneas conforme o protocolo selecionado."
            )
        
        # Validação específica por protocolo (apenas se foram informadas dobras)
        if tem_dobras:
            if protocolo == 'POLLOCK_7':
                required_fields = [
                    'triceps', 'subescapular', 'torax', 'abdominal',
                    'coxa', 'axilar_media', 'suprailiaca'
                ]
            elif protocolo == 'FALKNER_4':
                required_fields = ['triceps', 'subescapular', 'torax', 'abdominal']
            
            for field in required_fields:
                if not cleaned_data.get(field):
                    self.add_error(field, f"Este campo é obrigatório quando usando o protocolo {protocolo}")

        return cleaned_data

       
    @staticmethod
    def validate_dobra(value):
        if value is not None and (value < 3 or value > 60):
            raise forms.ValidationError("A dobra deve estar entre 3 e 60 mm")