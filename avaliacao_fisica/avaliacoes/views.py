from django.shortcuts import render
from .forms import AvaliacaoFisicaForm

def nova_avaliacao(request):
    form = AvaliacaoFisicaForm()
    return render(request, 'avaliacoes/nova_avaliacao.html', {'form': form})


