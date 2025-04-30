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
           # Calcula % gordura se dobras foram fornecidas
            if avaliacao.protocolo and any([
                avaliacao.triceps, avaliacao.subescapular,
                avaliacao.torax, avaliacao.abdominal,
                avaliacao.coxa, avaliacao.axilar_media,
                avaliacao.suprailiaca
            ]):
                soma_dobras = sum([
                    avaliacao.triceps or 0,
                    avaliacao.subescapular or 0,
                    avaliacao.torax or 0,
                    avaliacao.abdominal or 0,
                    avaliacao.coxa or 0,
                    avaliacao.axilar_media or 0,
                    avaliacao.suprailiaca or 0
                ])
                
                percentual, _ = calcular_gordura(
                soma_dobras if avaliacao.protocolo == 'POLLOCK_7' else (avaliacao.triceps + avaliacao.subescapular + avaliacao.torax + avaliacao.abdominal),
                paciente.idade,
                paciente.sexo,
                avaliacao.protocolo
                )
                avaliacao.percentual_gordura = percentual
            
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

def gerar_grafico_medidas(avaliacoes, medidas_selecionadas):
    plt.switch_backend('Agg')
    fig, ax = plt.subplots(figsize=(12, 6))
    
    datas = [av.data_avaliacao for av in avaliacoes]
    
    for medida in medidas_selecionadas:
        valores = [getattr(av, medida) for av in avaliacoes if getattr(av, medida)]
        if valores:
            ax.plot(datas[:len(valores)], valores, marker='o', label=medida.replace('_', ' ').title())
    
    ax.set_title('Evolução de Medidas Antropométricas')
    ax.set_ylabel('Medida (mm)')
    ax.legend()
    ax.grid(True, linestyle='--', alpha=0.6)
    fig.autofmt_xdate()
    
    buffer = BytesIO()
    plt.savefig(buffer, format='png', dpi=100, bbox_inches='tight')
    plt.close()
    return base64.b64encode(buffer.getvalue()).decode('utf-8')

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
        
        # Gráfico de medidas padrão
        medidas_padrao = ['cintura', 'quadril', 'braco_direito']
        graficos['medidas'] = gerar_grafico_medidas(todas_avaliacoes, medidas_padrao)
    
    return render(request, 'avaliacao/relatorio_completo.html', {
        'avaliacao': avaliacao_atual,
        'paciente': paciente,
        'graficos': graficos,
        'tem_historico': todas_avaliacoes.count() > 1,
        'avaliacoes_anteriores': todas_avaliacoes.exclude(pk=avaliacao_atual.pk),
        'titulo': f'Relatório - {paciente.nome}'
    })

def calcular_gordura(soma_dobras, idade, sexo, protocolo):
    """
    Calcula % de gordura para diferentes protocolos
    Retorna (percentual_gordura, fórmula_usada)
    """
    if protocolo == 'POLLOCK_7':
        if sexo == 'M':
            densidade = (
                1.112 - (0.00043499 * soma_dobras) + 
                (0.00000055 * soma_dobras**2) - 
                (0.00028826 * idade)
            )
        else:
            densidade = (
                1.097 - (0.00046971 * soma_dobras) + 
                (0.00000056 * soma_dobras**2) - 
                (0.00012828 * idade)
            )
        formula = "Pollock 7 dobras"
    
    elif protocolo == 'FALKNER_4':
        if sexo == 'M':
            densidade = 1.1714 - (0.00061 * soma_dobras) + (0.0000096 * soma_dobras**2)
        else:
            densidade = 1.1581 - (0.00056 * soma_dobras) + (0.000008 * soma_dobras**2)
        formula = "Falkner 4 dobras"
    
    percentual = (4.95 / densidade - 4.5) * 100
    return round(percentual, 1), formula

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