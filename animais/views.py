from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from .forms import AdocaoForm, AdotanteForm, AnexoForm, AnimalForm, VacinaForm
from .models import Adotante, Anexo, Animal, SolicitacaoAdocao, Vacina


# ---------------------------------------------------------------- animais

@login_required
def lista_animais(request):
    animais = Animal.objects.all()

    busca = request.GET.get('q', '').strip()
    filtros = {
        'especie': request.GET.get('especie', ''),
        'status': request.GET.get('status', ''),
        'localizacao': request.GET.get('localizacao', ''),
        'porte': request.GET.get('porte', ''),
    }

    if busca:
        animais = animais.filter(
            Q(nome__icontains=busca) | Q(raca__icontains=busca)
            | Q(especie_outra__icontains=busca) | Q(pelagem__icontains=busca)
        )
    for campo, valor in filtros.items():
        if valor:
            animais = animais.filter(**{campo: valor})

    return render(request, 'animais/lista.html', {
        'animais': animais,
        'busca': busca,
        'filtros': filtros,
        'especies': Animal.ESPECIES,
        'situacoes': Animal.STATUS,
        'localizacoes': Animal.LOCALIZACOES,
        'portes': Animal.PORTES,
    })


@login_required
def detalhe_animal(request, animal_id):
    animal = get_object_or_404(Animal, id=animal_id)

    return render(request, 'animais/detalhe.html', {
        'animal': animal,
        'vacina_form': VacinaForm(),
        'anexo_form': AnexoForm(),
        'adocoes': animal.solicitacoes_adocao.select_related('adotante'),
    })


@login_required
def animal_form(request, animal_id=None):
    animal = get_object_or_404(Animal, id=animal_id) if animal_id else None
    form = AnimalForm(request.POST or None, request.FILES or None, instance=animal)
    if request.method == 'POST' and form.is_valid():
        animal = form.save()
        messages.success(request, f'{animal.nome} salvo com sucesso.')
        return redirect('detalhe_animal', animal.id)
    return render(request, 'animais/animal_form.html', {'form': form, 'animal': animal})


@login_required
def animal_excluir(request, animal_id):
    animal = get_object_or_404(Animal, id=animal_id)
    if animal.solicitacoes_adocao.exists():
        messages.error(
            request,
            'Este animal tem adoções registradas e não pode ser excluído. '
            'Se for o caso, mude a situação para "Falecido" ou "Adotado".'
        )
        return redirect('detalhe_animal', animal.id)
    if request.method == 'POST':
        nome = animal.nome
        animal.delete()
        messages.success(request, f'{nome} foi excluído.')
        return redirect('lista_animais')
    return render(request, 'animais/confirmar_exclusao.html', {
        'objeto': animal.nome,
        'aviso': 'As vacinas e os anexos deste animal também serão apagados.',
        'voltar': ('detalhe_animal', animal.id),
    })


# ---------------------------------------------------------------- vacinas

@login_required
def vacina_form(request, animal_id=None, pk=None):
    vacina = get_object_or_404(Vacina, pk=pk) if pk else None
    animal = vacina.animal if vacina else get_object_or_404(Animal, id=animal_id)
    form = VacinaForm(request.POST or None, instance=vacina)
    if request.method == 'POST' and form.is_valid():
        vacina = form.save(commit=False)
        vacina.animal = animal
        vacina.save()
        messages.success(request, f'{vacina.tipo} "{vacina.nome}" registrado(a).')
        return redirect('detalhe_animal', animal.id)
    return render(request, 'animais/vacina_form.html', {
        'form': form, 'animal': animal, 'vacina': vacina,
    })


@login_required
def vacina_excluir(request, pk):
    vacina = get_object_or_404(Vacina, pk=pk)
    animal_id = vacina.animal_id
    if request.method == 'POST':
        vacina.delete()
        messages.success(request, 'Registro de dose excluído.')
        return redirect('detalhe_animal', animal_id)
    return render(request, 'animais/confirmar_exclusao.html', {
        'objeto': f'{vacina.tipo} {vacina.nome} ({vacina.data_aplicacao:%d/%m/%Y})',
        'voltar': ('detalhe_animal', animal_id),
    })


# ---------------------------------------------------------------- anexos

@login_required
def anexo_novo(request, animal_id):
    animal = get_object_or_404(Animal, id=animal_id)
    form = AnexoForm(request.POST or None, request.FILES or None)
    if request.method == 'POST' and form.is_valid():
        anexo = form.save(commit=False)
        anexo.animal = animal
        anexo.save()
        messages.success(request, 'Arquivo anexado.')
        return redirect('detalhe_animal', animal.id)
    return render(request, 'animais/anexo_form.html', {'form': form, 'animal': animal})


@login_required
def anexo_excluir(request, pk):
    anexo = get_object_or_404(Anexo, pk=pk)
    animal_id = anexo.animal_id
    if request.method == 'POST':
        anexo.arquivo.delete(save=False)
        anexo.delete()
        messages.success(request, 'Anexo excluído.')
        return redirect('detalhe_animal', animal_id)
    return render(request, 'animais/confirmar_exclusao.html', {
        'objeto': anexo.descricao or anexo.nome_arquivo,
        'voltar': ('detalhe_animal', animal_id),
    })


# ---------------------------------------------------------------- adotantes

@login_required
def adotante_lista(request):
    adotantes = Adotante.objects.all()
    busca = request.GET.get('q', '').strip()
    if busca:
        adotantes = adotantes.filter(
            Q(nome__icontains=busca) | Q(telefone__icontains=busca) | Q(email__icontains=busca)
        )
    return render(request, 'animais/adotante_lista.html', {'adotantes': adotantes, 'busca': busca})


@login_required
def adotante_form(request, pk=None):
    adotante = get_object_or_404(Adotante, pk=pk) if pk else None
    form = AdotanteForm(request.POST or None, instance=adotante)
    if request.method == 'POST' and form.is_valid():
        adotante = form.save()
        messages.success(request, f'Adotante {adotante.nome} salvo.')
        proximo = request.GET.get('next')
        if proximo == 'adocao':
            return redirect(f"{reverse('adocao_nova')}?adotante={adotante.pk}")
        return redirect('adotante_lista')
    return render(request, 'animais/adotante_form.html', {'form': form, 'adotante': adotante})


# ---------------------------------------------------------------- adoções

@login_required
def adocao_lista(request):
    adocoes = SolicitacaoAdocao.objects.select_related('animal', 'adotante')
    status = request.GET.get('status', '')
    if status:
        adocoes = adocoes.filter(status=status)
    return render(request, 'animais/adocao_lista.html', {
        'adocoes': adocoes,
        'status_atual': status,
        'opcoes_status': SolicitacaoAdocao.STATUS_SOLICITACAO,
    })


@login_required
def adocao_form(request, pk=None):
    adocao = get_object_or_404(SolicitacaoAdocao, pk=pk) if pk else None
    inicial = {}
    if not adocao:
        inicial = {k: request.GET[k] for k in ('animal', 'adotante') if request.GET.get(k)}
    form = AdocaoForm(request.POST or None, instance=adocao, initial=inicial)
    if request.method == 'POST' and form.is_valid():
        adocao = form.save()
        if adocao.status == 'Aprovada':
            messages.success(request, f'Adoção aprovada! {adocao.animal.nome} agora está como "Adotado".')
        else:
            messages.success(request, 'Adoção salva.')
        return redirect('adocao_lista')
    return render(request, 'animais/adocao_form.html', {'form': form, 'adocao': adocao})

