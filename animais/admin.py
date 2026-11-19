
from django.contrib import admin

from .models import (
    Animal,
    Vacina,
    Anexo,
    Adotante,
    SolicitacaoAdocao,
)


# CADASTRO DE ANIMAIS

@admin.register(Animal)
class AnimalAdmin(admin.ModelAdmin):
    list_display = (
        'nome',
        'especie',
        'raca',
        'porte',
        'localizacao',
        'status',
    )

    list_filter = (
        'especie',
        'porte',
        'localizacao',
        'status',
        'origem',
    )

    search_fields = ('nome', 'raca', 'especie_outra')


# CADASTRO DE VACINAS

@admin.register(Vacina)
class VacinaAdmin(admin.ModelAdmin):
    list_display = (
        'nome',
        'tipo',
        'animal',
        'data_aplicacao',
        'proxima_dose',
    )

    list_filter = ('tipo',)

    search_fields = (
        'nome',
        'animal__nome',
    )


# CADASTRO DE ANEXOS

@admin.register(Anexo)
class AnexoAdmin(admin.ModelAdmin):
    list_display = (
        'animal',
        'descricao',
    )

    search_fields = (
        'animal__nome',
        'descricao',
    )


# CADASTRO DE ADOTANTES

@admin.register(Adotante)
class AdotanteAdmin(admin.ModelAdmin):
    list_display = (
        'nome',
        'telefone',
        'email',
        'data_cadastro',
    )

    search_fields = (
        'nome',
        'telefone',
        'email',
    )

    ordering = ('nome',)


# SOLICITAÇÕES DE ADOÇÃO

@admin.register(SolicitacaoAdocao)
class SolicitacaoAdocaoAdmin(admin.ModelAdmin):
    list_display = (
        'animal',
        'adotante',
        'status',
        'data_solicitacao',
        'data_aprovacao',
    )

    list_filter = (
        'status',
        'animal',
    )

    search_fields = (
        'animal__nome',
        'adotante__nome',
    )

    readonly_fields = (
        'data_solicitacao',
        'data_aprovacao',
    )

    list_select_related = (
        'animal',
        'adotante',
    )

    ordering = ('-data_solicitacao',)
