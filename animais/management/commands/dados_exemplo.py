"""Cria alguns animais, doses, adoções e atendimentos de exemplo.

Uso: python manage.py dados_exemplo
Útil para testar e para gravar o vídeo de apresentação.
"""
from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from animais.models import Adotante, Animal, SolicitacaoAdocao, Vacina
from painel.models import Atendimento


class Command(BaseCommand):
    help = 'Cadastra dados de exemplo (animais, doses, adoções e atendimentos).'

    def handle(self, *args, **options):
        hoje = timezone.localdate()
        animais = [
            dict(nome='Caramelo', especie='Cachorro', raca='SRD', sexo='Macho', idade=3, porte='Médio',
                 pelagem='Caramelo, curto', localizacao='Abrigo 1', status='Disponível', origem='Abandono',
                 temperamento='Dócil e brincalhão', info_clinica='Castrado. Saudável.'),
            dict(nome='Mel', especie='Gato', raca='SRD', sexo='Fêmea', idade=1, porte='Pequeno',
                 pelagem='Tricolor', localizacao='Lar temporário', status='Disponível', origem='Abandono',
                 temperamento='Carinhosa'),
            dict(nome='Thor', especie='Cachorro', raca='Pitbull', sexo='Macho', idade=5, porte='Grande',
                 pelagem='Cinza', localizacao='Internado', status='Em tratamento', origem='Atropelamento',
                 temperamento='Calmo', info_clinica='Fratura na pata traseira, em recuperação no Prontodog.'),
            dict(nome='Luna', especie='Cachorro', raca='SRD', sexo='Fêmea', idade=8, porte='Pequeno',
                 pelagem='Preta', localizacao='Abrigo 2', status='Não disponível', origem='Maus-tratos',
                 motivo_indisponivel='Idosa e muito medrosa, fica no abrigo', temperamento='Medrosa'),
            dict(nome='Sábio', especie='Outro', especie_outra='coruja', sexo='Não identificado', porte='Pequeno',
                 localizacao='Abrigo 3', status='Em tratamento', origem='Atropelamento',
                 info_clinica='Asa machucada. Aguardando soltura.'),
            dict(nome='Pingo', especie='Gato', sexo='Macho', idade=0, porte='Pequeno', pelagem='Branco',
                 localizacao='Abrigo 1', status='Disponível', origem='Abandono', temperamento='Filhote agitado'),
        ]
        criados = 0
        for dados in animais:
            dados.setdefault('data_entrada', hoje - timedelta(days=60))
            animal, novo = Animal.objects.get_or_create(nome=dados['nome'], defaults=dados)
            criados += novo
            if novo:
                Vacina.objects.create(animal=animal, tipo='Vacina', nome='V10' if animal.especie == 'Cachorro' else 'V4',
                                      data_aplicacao=hoje - timedelta(days=360), proxima_dose=hoje + timedelta(days=5))
                Vacina.objects.create(animal=animal, tipo='Vermífugo', nome='Drontal',
                                      data_aplicacao=hoje - timedelta(days=100), proxima_dose=hoje - timedelta(days=10))
                Vacina.objects.create(animal=animal, tipo='Antiparasitário', nome='Bravecto',
                                      data_aplicacao=hoje - timedelta(days=20), proxima_dose=hoje + timedelta(days=70))

        adotante, _ = Adotante.objects.get_or_create(
            nome='Maria da Silva', defaults={'telefone': '(69) 99999-0000', 'endereco': 'Porto Velho'})
        if not SolicitacaoAdocao.objects.exists():
            bob, _ = Animal.objects.get_or_create(
                nome='Bob', defaults=dict(especie='Cachorro', sexo='Macho', porte='Médio', idade=2,
                                          localizacao='Abrigo 2', status='Disponível', origem='Abandono'))
            SolicitacaoAdocao.objects.create(animal=bob, adotante=adotante, status='Aprovada')
            SolicitacaoAdocao.objects.create(
                animal=Animal.objects.get(nome='Mel'), adotante=adotante, status='Pendente')

        if not Atendimento.objects.exists():
            Atendimento.objects.create(tipo='Castração', nome_animal='Pretinha', especie='Gato',
                                       responsavel='Dona Ana', local='Bairro Nacional', custo=120)
            Atendimento.objects.create(tipo='Doação de ração', especie='Cachorro', responsavel='Seu José',
                                       local='Distrito de Jaci-Paraná', custo=80, situacao='Concluído')

        self.stdout.write(self.style.SUCCESS(f'Pronto! {criados} animal(is) novo(s) cadastrado(s).'))
