from django.urls import path
from . import views

urlpatterns = [
    path('', views.lista_animais, name='lista_animais'),
    path('novo/', views.animal_form, name='animal_novo'),
    path('<int:animal_id>/', views.detalhe_animal, name='detalhe_animal'),
    path('<int:animal_id>/editar/', views.animal_form, name='animal_editar'),
    path('<int:animal_id>/excluir/', views.animal_excluir, name='animal_excluir'),

    path('<int:animal_id>/doses/nova/', views.vacina_form, name='vacina_nova'),
    path('doses/<int:pk>/editar/', views.vacina_form, name='vacina_editar'),
    path('doses/<int:pk>/excluir/', views.vacina_excluir, name='vacina_excluir'),

    path('<int:animal_id>/anexos/novo/', views.anexo_novo, name='anexo_novo'),
    path('anexos/<int:pk>/excluir/', views.anexo_excluir, name='anexo_excluir'),

    path('adotantes/', views.adotante_lista, name='adotante_lista'),
    path('adotantes/novo/', views.adotante_form, name='adotante_novo'),
    path('adotantes/<int:pk>/editar/', views.adotante_form, name='adotante_editar'),

    path('adocoes/', views.adocao_lista, name='adocao_lista'),
    path('adocoes/nova/', views.adocao_form, name='adocao_nova'),
    path('adocoes/<int:pk>/editar/', views.adocao_form, name='adocao_editar'),
]
