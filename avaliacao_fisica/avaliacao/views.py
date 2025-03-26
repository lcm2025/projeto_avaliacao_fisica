from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Paciente, Avaliacao
from .forms import PacienteForm, AvaliacaoForm
import matplotlib.pyplot as plt
from io import BytesIO
import base64

@login_required
def lista_pacientes(request):
    pacientes = Paciente.objects.all().order_by('nome')
    return render(request, 'avaliacao/lista_pacientes.html', {
        'pacientes': pacientes,
        'titulo': 'Lista de Pacientes'
    })

@login_required
def novo_paciente(request):
    if request.method == 'POST':
        form = PacienteForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('avaliacao:lista_pacientes')
    else:
        form = PacienteForm()
    
    return render(request, 'avaliacao/form_paciente.html', {
        'form': form,
        'titulo': 'Novo Paciente'
    })

@login_required
def nova_avaliacao(request, paciente_id):
    paciente = get_object_or_404(Paciente, pk=paciente_id)
    
    if request.method == 'POST':
        form = AvaliacaoForm(request.POST)
        if form.is_valid():
            avaliacao = form.save(commit=False)
            avaliacao.paciente = paciente
            # Calcula % gordura se todas dobras forem fornecidas
            if all([
                avaliacao.torax, avaliacao.triceps, avaliacao.abdominal,
                avaliacao.coxa, avaliacao.axilar_media,
                avaliacao.subescapular, avaliacao.suprailiaca
            ]):
                avaliacao.percentual_gordura = calcular_gordura_pollock(
                    soma_dobras=avaliacao.soma_7_dobras,
                    idade=paciente.idade,
                    sexo=paciente.sexo
                )
            
            avaliacao.save()
            return redirect('avaliacao:historico_avaliacoes', paciente_id=paciente.id)
    else:
        form = AvaliacaoForm()
    
    return render(request, 'avaliacao/form_avaliacao.html', {
        'form': form,
        'paciente': paciente,
        'avaliacoes_anteriores': Avaliacao.objects.filter(paciente=paciente).order_by('-data_avaliacao')[:3],
        'titulo': f'Nova Avaliação - {paciente.nome}'
    })

@login_required
def historico_avaliacoes(request, paciente_id):
    paciente = get_object_or_404(Paciente, pk=paciente_id)
    avaliacoes = Avaliacao.objects.filter(paciente=paciente).order_by('-data_avaliacao')
    
    return render(request, 'avaliacao/historico.html', {
        'paciente': paciente,
        'avaliacoes': avaliacoes,
        'titulo': f'Histórico - {paciente.nome}'
    })

@login_required
def relatorio_completo(request, pk):
    avaliacao_atual = get_object_or_404(Avaliacao, pk=pk)
    paciente = avaliacao_atual.paciente
    todas_avaliacoes = Avaliacao.objects.filter(paciente=paciente).order_by('data_avaliacao')
    
    # Garante que a avaliação atual está incluída
    if avaliacao_atual not in todas_avaliacoes:
        todas_avaliacoes = list(todas_avaliacoes) + [avaliacao_atual]
        todas_avaliacoes.sort(key=lambda x: x.data_avaliacao)
    
    graficos = {}
    
    if todas_avaliacoes.count() > 1:
        graficos['peso'] = gerar_grafico(
            todas_avaliacoes, 
            'data_avaliacao', 
            'peso', 
            'Evolução do Peso (kg)', 
            'kg',
            destaque=avaliacao_atual.data_avaliacao
        )
        
        graficos['gordura'] = gerar_grafico(
            todas_avaliacoes, 
            'data_avaliacao', 
            'percentual_gordura', 
            'Evolução do % Gordura', 
            '%',
            destaque=avaliacao_atual.data_avaliacao
        )
        
        graficos['imc'] = gerar_grafico(
            todas_avaliacoes, 
            'data_avaliacao', 
            'imc', 
            'Evolução do IMC', 
            '',
            destaque=avaliacao_atual.data_avaliacao
        )
        graficos['composicao'] = gerar_grafico_pizza(
            massa_gorda=avaliacao_atual.percentual_gordura,
            massa_magra=100 - avaliacao_atual.percentual_gordura,  # Calcula % massa magra
            titulo=f"Composição Corporal - {paciente.nome}"
        )
    
    return render(request, 'avaliacao/relatorio_completo.html', {
        'avaliacao': avaliacao_atual,
        'paciente': paciente,
        'graficos': graficos,
        'tem_historico': todas_avaliacoes.count() > 1,
        'avaliacoes_anteriores': todas_avaliacoes.exclude(pk=avaliacao_atual.pk),
        'titulo': f'Relatório - {paciente.nome}'
    })

def calcular_gordura_pollock(soma_dobras, idade, sexo):
    """
    Calcula % de gordura pelo protocolo de Pollock 7 dobras
    Fórmulas válidas para adultos (18-60 anos)
    """
    densidade_corporal = (
        1.112 - (0.00043499 * soma_dobras) + 
        (0.00000055 * soma_dobras**2) - 
        (0.00028826 * idade)
    ) if sexo == 'M' else (
        1.097 - (0.00046971 * soma_dobras) + 
        (0.00000056 * soma_dobras**2) - 
        (0.00012828 * idade)
    )
    
    percentual_gordura = (4.95 / densidade_corporal - 4.5) * 100
    return round(percentual_gordura, 1)

def gerar_grafico(queryset, campo_x, campo_y, titulo, unidade, destaque=None):
    """Gera gráfico de linha temporal horizontal com destaque"""
    datas = [getattr(item, campo_x) for item in queryset]  # Objetos date
    valores = [getattr(item, campo_y) for item in queryset]
    
    plt.switch_backend('Agg')
    fig, ax = plt.subplots(figsize=(10, 4))
    
    # Gráfico de linha
    ax.plot(datas, valores, marker='o', linestyle='-', color='#3498db', linewidth=2, label='Evolução')
    
    # Destacar avaliação atual
    if destaque:
        idx = datas.index(destaque)
        ax.scatter(datas[idx], valores[idx], color='#e74c3c', s=100, label='Avaliação Atual')
        ax.axhline(y=valores[idx], color='#e74c3c', linestyle='--', alpha=0.3)  # Linha horizontal
    
    # Formatação
    ax.set_title(titulo, pad=10)
    ax.set_ylabel(unidade)
    ax.grid(True, linestyle='--', alpha=0.6)
    ax.legend()
    fig.autofmt_xdate()  # Ajusta rótulos das datas
    
    buffer = BytesIO()
    plt.savefig(buffer, format='png', dpi=100, bbox_inches='tight')
    plt.close()
    return base64.b64encode(buffer.getvalue()).decode('utf-8')

def gerar_grafico_pizza(massa_gorda, massa_magra, titulo):
    """Gera um gráfico de pizza para composição corporal"""
    labels = ['Massa Gorda', 'Massa Magra']
    sizes = [massa_gorda, massa_magra]
    colors = ['#ff6384', '#36a2eb']  # Rosa para gordura, azul para massa magra
    explode = (0.1, 0)  # Destaca a fatia da massa gorda
    
    plt.switch_backend('Agg')
    fig, ax = plt.subplots(figsize=(6, 6))
    
    wedges, texts, autotexts = ax.pie(
        sizes,
        explode=explode,
        labels=labels,
        colors=colors,
        autopct='%1.1f%%',
        shadow=True,
        startangle=90,
        textprops={'fontsize': 12, 'fontweight': 'bold'}
    )
    
    ax.set_title(titulo, pad=20, fontweight='bold')
    ax.axis('equal')  # Garante que o gráfico fique circular
    
    buffer = BytesIO()
    plt.savefig(buffer, format='png', dpi=100, bbox_inches='tight', transparent=True)
    plt.close()
    return base64.b64encode(buffer.getvalue()).decode('utf-8')