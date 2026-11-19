from datetime import timedelta

from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils import timezone

from .models import Adotante, Animal, SolicitacaoAdocao, Vacina


def dados_animal(**extra):
    dados = {
        'nome': 'Rex', 'especie': 'Cachorro', 'sexo': 'Macho', 'porte': 'Médio',
        'localizacao': 'Abrigo 1', 'status': 'Disponível',
    }
    dados.update(extra)
    return dados


class AnimalModelTests(TestCase):
    def test_especie_outro_exige_qual(self):
        a = Animal(**dados_animal(especie='Outro'))
        with self.assertRaises(ValidationError) as ctx:
            a.full_clean()
        self.assertIn('especie_outra', ctx.exception.message_dict)
        a.especie_outra = 'coruja'
        a.full_clean()
        self.assertEqual(a.especie_exibicao, 'Coruja')

    def test_nao_disponivel_exige_motivo(self):
        a = Animal(**dados_animal(status='Não disponível'))
        with self.assertRaises(ValidationError) as ctx:
            a.full_clean()
        self.assertIn('motivo_indisponivel', ctx.exception.message_dict)


class AdocaoTests(TestCase):
    def test_aprovar_adocao_marca_animal_como_adotado(self):
        animal = Animal.objects.create(**dados_animal())
        adotante = Adotante.objects.create(nome='Maria', telefone='69 99999-0000')
        SolicitacaoAdocao.objects.create(animal=animal, adotante=adotante, status='Aprovada')
        animal.refresh_from_db()
        self.assertEqual(animal.status, 'Adotado')


@override_settings(MEDIA_ROOT='/tmp/teste-media-ong')
class TelasAnimaisTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user('dona', password='senha-teste-123')

    def test_telas_exigem_login(self):
        r = self.client.get(reverse('lista_animais'))
        self.assertEqual(r.status_code, 302)
        self.assertIn(reverse('login'), r['Location'])

    def test_fluxo_completo(self):
        self.client.force_login(self.user)

        # cadastra um animal de espécie "Outro"
        r = self.client.post(reverse('animal_novo'), dados_animal(
            nome='Pipoca', especie='Outro', especie_outra='macaco', origem='Maus-tratos',
            pelagem='marrom', temperamento='agitado', info_clinica='ferimento na pata',
            localizacao='Internado', status='Em tratamento', idade=2,
        ))
        animal = Animal.objects.get(nome='Pipoca')
        self.assertRedirects(r, reverse('detalhe_animal', args=[animal.id]))
        self.assertEqual(animal.localizacao, 'Internado')

        # telas abrem
        for url in [reverse('lista_animais'), reverse('detalhe_animal', args=[animal.id]),
                    reverse('animal_editar', args=[animal.id]), reverse('vacina_nova', args=[animal.id]),
                    reverse('anexo_novo', args=[animal.id]), reverse('adocao_lista'),
                    reverse('adocao_nova'), reverse('adotante_lista'), reverse('adotante_novo'),
                    reverse('lista_animais') + '?especie=Outro&localizacao=Internado&q=pipo']:
            self.assertEqual(self.client.get(url).status_code, 200, url)

        # registra vermífugo
        hoje = timezone.localdate()
        self.client.post(reverse('vacina_nova', args=[animal.id]), {
            'tipo': 'Vermífugo', 'nome': 'Drontal', 'data_aplicacao': hoje.isoformat(),
            'proxima_dose': (hoje + timedelta(days=90)).isoformat(),
        })
        self.assertEqual(Vacina.objects.get().tipo, 'Vermífugo')

        # anexa arquivo
        arquivo = SimpleUploadedFile('exame.pdf', b'%PDF-1.4 teste', content_type='application/pdf')
        self.client.post(reverse('anexo_novo', args=[animal.id]), {'arquivo': arquivo, 'descricao': 'Exame'})
        self.assertEqual(animal.anexos.count(), 1)

        # fica disponível e é adotado pela tela
        self.client.post(reverse('animal_editar', args=[animal.id]), dados_animal(
            nome='Pipoca', especie='Outro', especie_outra='macaco', localizacao='Abrigo 2',
            status='Disponível',
        ))
        self.client.post(reverse('adotante_novo'), {'nome': 'João', 'telefone': '69 98888-0000'})
        adotante = Adotante.objects.get()
        r = self.client.post(reverse('adocao_nova'), {
            'animal': animal.id, 'adotante': adotante.id, 'status': 'Aprovada',
        })
        self.assertRedirects(r, reverse('adocao_lista'))
        animal.refresh_from_db()
        self.assertEqual(animal.status, 'Adotado')

        # animal com adoção não pode ser excluído
        self.client.post(reverse('animal_excluir', args=[animal.id]))
        self.assertTrue(Animal.objects.filter(pk=animal.pk).exists())
