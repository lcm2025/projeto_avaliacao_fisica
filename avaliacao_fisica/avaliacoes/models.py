from django.db import models

# Create your models here.
class AvaliacaoFisica(models.Model):
    nome = models.CharField(max_length=100)
    idade = models.IntegerField()
    peso = models.FloatField()
    altura = models.FloatField()
    data_nascimento = models.DateField()

    #Bioimpedancia
    gordura_percentual = models.FloatField()
    massa_magra = models.FloatField()
    metabolismo_basal = models.FloatField()
    idade_corporal = models.IntegerField()
    gordura_visceral = models.FloatField()
    imc = models.FloatField()

    #Dobras cutâneas
    triceps = models.FloatField()
    subescapular = models.FloatField()
    suprailiaca = models.FloatField()
    torax = models.FloatField()
    axilar = models.FloatField()
    abdomen = models.FloatField()
    coxa = models.FloatField()

    data_avaliacao = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.nome} - {self.data_avaliacao.strftime('%d/%m/%Y')}"













