from datetime import timedelta

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from animais.models import Animal, Vacina

from .avisos import calcular_avisos
from .models import Atendimento


def criar_animal(nome='Rex', status='Disponível'):
    return Animal.objects.create(nome=nome, especie='Cachorro', sexo='Macho', porte='Médio', status=status)


class AvisosTests(TestCase):
    def setUp(self):
        self.hoje = timezone.localdate()

    def test_atrasado_e_proximo(self):
        a = criar_animal()
        Vacina.objects.create(animal=a, nome='V10', data_aplicacao=self.hoje - timedelta(days=365),
                              proxima_dose=self.hoje - timedelta(days=2))
        Vacina.objects.create(animal=a, nome='Vermífugo', data_aplicacao=self.hoje - timedelta(days=80),
                              proxima_dose=self.hoje + timedelta(days=3))
        Vacina.objects.create(animal=a, nome='Antirrábica', data_aplicacao=self.hoje,
                              proxima_dose=self.hoje + timedelta(days=300))
        r = calcular_avisos(7)
        self.assertEqual([v.nome for v in r['atrasados']], ['V10'])
        self.assertEqual([v.nome for v in r['proximos']], ['Vermífugo'])

    def test_adotado_nao_gera_aviso(self):
        a = criar_animal(status='Adotado')
        Vacina.objects.create(animal=a, nome='V10', data_aplicacao=self.hoje - timedelta(days=400),
                              proxima_dose=self.hoje - timedelta(days=30))
        r = calcular_avisos()
        self.assertEqual(r['atrasados'], [])

    def test_dose_reaplicada_some_do_aviso(self):
        a = criar_animal()
        Vacina.objects.create(animal=a, nome='V10', data_aplicacao=self.hoje - timedelta(days=400),
                              proxima_dose=self.hoje - timedelta(days=30))
        Vacina.objects.create(animal=a, nome='v10', data_aplicacao=self.hoje,
                              proxima_dose=self.hoje + timedelta(days=365))
        r = calcular_avisos()
        self.assertEqual(r['atrasados'], [])
        self.assertEqual(r['proximos'], [])


class TelasTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user('dona', password='senha-teste-123')

    def test_exige_login(self):
        for nome in ['dashboard', 'avisos', 'atendimento_lista', 'atendimento_novo']:
            r = self.client.get(reverse(nome))
            self.assertEqual(r.status_code, 302, nome)
            self.assertIn(reverse('login'), r['Location'])

    def test_telas_abrem_logado(self):
        self.client.force_login(self.user)
        criar_animal()
        Atendimento.objects.create(tipo='Castração', nome_animal='Mimi', especie='Gato', custo=80)
        for nome in ['dashboard', 'avisos', 'atendimento_lista', 'atendimento_novo']:
            self.assertEqual(self.client.get(reverse(nome)).status_code, 200, nome)

    def test_crud_atendimento(self):
        self.client.force_login(self.user)
        r = self.client.post(reverse('atendimento_novo'), {
            'data': timezone.localdate().isoformat(), 'tipo': 'Resgate',
            'nome_animal': 'Coruja', 'especie': 'Coruja', 'situacao': 'Em andamento',
        })
        self.assertRedirects(r, reverse('atendimento_lista'))
        a = Atendimento.objects.get()
        r = self.client.post(reverse('atendimento_editar', args=[a.pk]), {
            'data': a.data.isoformat(), 'tipo': 'Resgate', 'situacao': 'Concluído',
        })
        a.refresh_from_db()
        self.assertEqual(a.situacao, 'Concluído')
        self.client.post(reverse('atendimento_excluir', args=[a.pk]))
        self.assertFalse(Atendimento.objects.exists())
