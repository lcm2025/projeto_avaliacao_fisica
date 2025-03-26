from django.db import models
from django.contrib.auth.models import User
from datetime import date

class Paciente(models.Model):
    SEXO_CHOICES = [('M', 'Masculino'), ('F', 'Feminino')]
    
    nome = models.CharField(max_length=100)
    sexo = models.CharField(max_length=1, choices=SEXO_CHOICES)
    data_nascimento = models.DateField()
    telefone = models.CharField(max_length=15, blank=True)
    email = models.EmailField(blank=True)
    observacoes = models.TextField(blank=True)
    
    @property
    def idade(self):
        hoje = date.today()
        return hoje.year - self.data_nascimento.year - (
            (hoje.month, hoje.day) < (self.data_nascimento.month, self.data_nascimento.day)
        )
    
    def __str__(self):
        return self.nome

class Avaliacao(models.Model):
    paciente = models.ForeignKey(Paciente, on_delete=models.CASCADE, related_name='avaliacoes')
    data_avaliacao = models.DateTimeField(auto_now_add=True)
    altura = models.FloatField(help_text="Altura em metros")
    peso = models.FloatField(help_text="Peso em kg")
    percentual_gordura = models.FloatField(verbose_name="% Gordura")
    massa_magra = models.FloatField()
    gordura_visceral = models.IntegerField()
    tmb = models.IntegerField(verbose_name="Taxa Metabólica Basal")
    idade_metabolica = models.IntegerField()
    observacoes = models.TextField(blank=True)

    # Dobras cutâneas (em mm)
    torax = models.FloatField('Tórax', null=True, blank=True)
    triceps = models.FloatField('Tríceps', null=True, blank=True)
    abdominal = models.FloatField('Abdominal', null=True, blank=True)
    coxa = models.FloatField('Coxa', null=True, blank=True)
    axilar_media = models.FloatField('Axilar Média', null=True, blank=True)
    subescapular = models.FloatField('Subescapular', null=True, blank=True)
    suprailiaca = models.FloatField('Supra-ilíaca', null=True, blank=True)

    @property
    def soma_7_dobras(self):
        return sum([
            self.torax or 0,
            self.triceps or 0,
            self.abdominal or 0,
            self.coxa or 0,
            self.axilar_media or 0,
            self.subescapular or 0,
            self.suprailiaca or 0
        ])
    
    class Meta:
        ordering = ['-data_avaliacao']
    
    @property
    def imc(self):
        return self.peso / (self.altura ** 2)
    
    def __str__(self):
        return f"Avaliação de {self.paciente.nome} em {self.data_avaliacao.date()}"