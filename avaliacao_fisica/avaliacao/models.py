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
    PROTOCOLOS = [
        ('POLLOCK_7', 'Pollock 7 Dobras'),
        ('FALKNER_4', 'Falkner 4 Dobras'),
    ]
    
    protocolo = models.CharField(
        max_length=10,
        choices=PROTOCOLOS,
        default='POLLOCK_7'
    )

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

    # Membros Superiores, Medidas MM
    braco_direito = models.FloatField('Braço Direito (mm)', null=True, blank=True)
    braco_esquerdo = models.FloatField('Braço Esquerdo (mm)', null=True, blank=True)
    antebraco_direito = models.FloatField('Antebraço Direito (mm)', null=True, blank=True)
    antebraco_esquerdo = models.FloatField('Antebraço Esquerdo (mm)', null=True, blank=True)
    
    # Tronco, Medidas MM
    cintura = models.FloatField('Cintura (mm)', null=True, blank=True)
    quadril = models.FloatField('Quadril (mm)', null=True, blank=True)
    tronco = models.FloatField('Tronco (mm)', null=True, blank=True)
    abdomen = models.FloatField('Abdômen (mm)', null=True, blank=True)
    
    # Membros Inferiores, Medidas MM
    coxa_direita = models.FloatField('Coxa Direita (mm)', null=True, blank=True)
    coxa_esquerda = models.FloatField('Coxa Esquerda (mm)', null=True, blank=True)
    panturrilha_direita = models.FloatField('Panturrilha Direita (mm)', null=True, blank=True)
    panturrilha_esquerda = models.FloatField('Panturrilha Esquerda (mm)', null=True, blank=True)

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
    
    @property
    def soma_4_dobras(self):
        """Soma para Falkner: tríceps + subescapular + torax + abdominal"""
        return sum([
            self.triceps or 0,
            self.subescapular or 0,
            self.torax or 0,
            self.abdominal or 0
        ])
    
    class Meta:
        ordering = ['-data_avaliacao']
    
    @property
    def imc(self):
        return self.peso / (self.altura ** 2)
    
    def __str__(self):
        return f"Avaliação de {self.paciente.nome} em {self.data_avaliacao.date()}"