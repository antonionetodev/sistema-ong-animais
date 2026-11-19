from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q, Sum
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from animais.models import Animal, SolicitacaoAdocao

from .avisos import calcular_avisos
from .forms import AtendimentoForm
from .models import Atendimento


@login_required
def dashboard(request):
    hoje = timezone.localdate()
    animais = Animal.objects.all()

    por_status = animais.values('status').annotate(total=Count('id')).order_by('-total')
    sob_cuidado = animais.exclude(status__in=['Adotado', 'Falecido'])
    por_especie = (
        sob_cuidado.values('especie', 'especie_outra')
        .annotate(total=Count('id')).order_by('-total')
    )
    por_localizacao = sob_cuidado.values('localizacao').annotate(total=Count('id')).order_by('localizacao')

    atend_mes = Atendimento.objects.filter(data__year=hoje.year, data__month=hoje.month)
    avisos = calcular_avisos()

    contexto = {
        'total_animais': animais.count(),
        'no_abrigo': sob_cuidado.count(),
        'disponiveis': animais.filter(status='Disponível').count(),
        'em_tratamento': animais.filter(status='Em tratamento').count(),
        'adotados': animais.filter(status='Adotado').count(),
        'nao_disponiveis': animais.filter(status='Não disponível').count(),
        'falecidos': animais.filter(status='Falecido').count(),
        'por_localizacao': por_localizacao,
        'adocoes_pendentes': SolicitacaoAdocao.objects.filter(status='Pendente').count(),
        'por_status': por_status,
        'por_especie': por_especie,
        'atendimentos_mes': atend_mes.count(),
        'custo_mes': atend_mes.aggregate(total=Sum('custo'))['total'] or 0,
        'atendimentos_andamento': Atendimento.objects.filter(situacao='Em andamento').count(),
        'ultimos_atendimentos': Atendimento.objects.all()[:5],
        'ultimos_animais': animais.order_by('-data_cadastro')[:5],
        'avisos': avisos,
        'total_avisos': len(avisos['atrasados']) + len(avisos['proximos']),
    }
    return render(request, 'painel/dashboard.html', contexto)


@login_required
def avisos(request):
    opcoes = [7, 15, 30]
    try:
        dias = int(request.GET.get('dias', 7))
    except ValueError:
        dias = 7
    if dias not in opcoes:
        dias = 7
    contexto = calcular_avisos(dias)
    contexto['opcoes_dias'] = opcoes
    return render(request, 'painel/avisos.html', contexto)


@login_required
def atendimento_lista(request):
    atendimentos = Atendimento.objects.all()
    busca = request.GET.get('q', '').strip()
    tipo = request.GET.get('tipo', '')
    situacao = request.GET.get('situacao', '')

    if busca:
        atendimentos = atendimentos.filter(
            Q(nome_animal__icontains=busca) | Q(responsavel__icontains=busca)
            | Q(local__icontains=busca) | Q(descricao__icontains=busca)
            | Q(especie__icontains=busca)
        )
    if tipo:
        atendimentos = atendimentos.filter(tipo=tipo)
    if situacao:
        atendimentos = atendimentos.filter(situacao=situacao)

    return render(request, 'painel/atendimento_lista.html', {
        'atendimentos': atendimentos,
        'tipos': Atendimento.TIPOS,
        'situacoes': Atendimento.SITUACOES,
        'total_custo': atendimentos.aggregate(total=Sum('custo'))['total'] or 0,
    })


@login_required
def atendimento_form(request, pk=None):
    atendimento = get_object_or_404(Atendimento, pk=pk) if pk else None
    form = AtendimentoForm(request.POST or None, instance=atendimento)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Atendimento salvo com sucesso.')
        return redirect('atendimento_lista')
    return render(request, 'painel/atendimento_form.html', {
        'form': form,
        'atendimento': atendimento,
    })


@login_required
def atendimento_excluir(request, pk):
    atendimento = get_object_or_404(Atendimento, pk=pk)
    if request.method == 'POST':
        atendimento.delete()
        messages.success(request, 'Atendimento excluído.')
        return redirect('atendimento_lista')
    return render(request, 'painel/atendimento_excluir.html', {'atendimento': atendimento})
