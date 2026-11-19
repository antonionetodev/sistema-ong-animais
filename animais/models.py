
from django.db import models, transaction
from django.core.exceptions import ValidationError
from django.utils import timezone


class Animal(models.Model):
    ESPECIES = [
        ('Cachorro', 'Cachorro'),
        ('Gato', 'Gato'),
        ('Outro', 'Outro'),
    ]

    SEXOS = [
        ('Macho', 'Macho'),
        ('Fêmea', 'Fêmea'),
        ('Não identificado', 'Não identificado'),
    ]

    PORTES = [
        ('Pequeno', 'Pequeno'),
        ('Médio', 'Médio'),
        ('Grande', 'Grande'),
    ]

    # Onde o animal está (separado da situação dele)
    LOCALIZACOES = [
        ('Abrigo 1', 'Abrigo 1'),
        ('Abrigo 2', 'Abrigo 2'),
        ('Abrigo 3', 'Abrigo 3'),
        ('Lar temporário', 'Lar temporário'),
        ('Internado', 'Internado'),
    ]

    # Situação do animal
    STATUS = [
        ('Em tratamento', 'Em tratamento'),
        ('Disponível', 'Disponível'),
        ('Não disponível', 'Não disponível'),
        ('Adotado', 'Adotado'),
        ('Falecido', 'Falecido'),
    ]

    ORIGENS = [
        ('Maus-tratos', 'Maus-tratos'),
        ('Abandono', 'Abandono'),
        ('Atropelamento', 'Atropelamento'),
        ('Outro', 'Outro'),
    ]

    nome = models.CharField('Nome', max_length=100)
    especie = models.CharField('Espécie', max_length=20, choices=ESPECIES)
    especie_outra = models.CharField(
        'Qual espécie?', max_length=60, blank=True,
        help_text='Preencha quando a espécie for "Outro" (ex.: macaco, coruja, cavalo)'
    )
    raca = models.CharField('Raça', max_length=100, blank=True)
    idade = models.PositiveIntegerField(
        'Idade aproximada (anos)', null=True, blank=True,
        help_text='Use 0 para filhotes com menos de 1 ano'
    )
    sexo = models.CharField('Sexo', max_length=20, choices=SEXOS)
    porte = models.CharField('Porte', max_length=20, choices=PORTES)
    pelagem = models.CharField(
        'Pelagem', max_length=100, blank=True,
        help_text='Cor e tipo de pelo/penas (ex.: caramelo, curto)'
    )

    localizacao = models.CharField(
        'Localização', max_length=30, choices=LOCALIZACOES, default='Abrigo 1'
    )
    status = models.CharField(
        'Situação',
        max_length=30,
        choices=STATUS,
        default='Disponível'
    )
    motivo_indisponivel = models.CharField(
        'Motivo (não disponível)', max_length=200, blank=True,
        help_text='Obrigatório quando a situação for "Não disponível"'
    )

    origem = models.CharField(
        'Origem', max_length=30, choices=ORIGENS, blank=True
    )
    data_entrada = models.DateField(
        'Data de entrada na ONG', null=True, blank=True
    )
    temperamento = models.CharField(
        'Temperamento', max_length=200, blank=True,
        help_text='Ex.: dócil, medroso, não se dá bem com gatos'
    )
    info_clinica = models.TextField(
        'Informações clínicas', blank=True,
        help_text='Doenças, castração, medicações, alergias...'
    )
    descricao = models.TextField('Observações', blank=True)

    foto = models.ImageField(
        'Foto',
        upload_to='animais/',
        blank=True,
        null=True
    )

    data_cadastro = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['nome']
        verbose_name = 'Animal'
        verbose_name_plural = 'Animais'

    def clean(self):
        super().clean()
        erros = {}
        if self.especie == 'Outro' and not self.especie_outra.strip():
            erros['especie_outra'] = 'Informe qual é a espécie.'
        if self.status == 'Não disponível' and not self.motivo_indisponivel.strip():
            erros['motivo_indisponivel'] = 'Informe o motivo de o animal não estar disponível.'
        if erros:
            raise ValidationError(erros)

    @property
    def especie_exibicao(self):
        if self.especie == 'Outro' and self.especie_outra:
            return self.especie_outra.capitalize()
        return self.especie

    @property
    def cor_status(self):
        return {
            'Disponível': 'success',
            'Em tratamento': 'warning',
            'Não disponível': 'secondary',
            'Adotado': 'primary',
            'Falecido': 'dark',
        }.get(self.status, 'light')

    def __str__(self):
        return self.nome


class Vacina(models.Model):
    """Registro de doses: vacinas, vermífugos e antiparasitários."""

    TIPOS = [
        ('Vacina', 'Vacina'),
        ('Vermífugo', 'Vermífugo'),
        ('Antiparasitário', 'Antiparasitário'),
    ]

    animal = models.ForeignKey(
        Animal,
        on_delete=models.CASCADE,
        related_name='vacinas'
    )

    tipo = models.CharField('Tipo', max_length=20, choices=TIPOS, default='Vacina')
    nome = models.CharField(
        'Nome/produto', max_length=100,
        help_text='Ex.: V10, Antirrábica, Drontal, Bravecto'
    )
    data_aplicacao = models.DateField('Data de aplicação')
    proxima_dose = models.DateField('Próxima dose', null=True, blank=True)
    observacao = models.CharField('Observação', max_length=200, blank=True)

    class Meta:
        ordering = ['-data_aplicacao']
        verbose_name = 'Vacina/vermífugo/antiparasitário'
        verbose_name_plural = 'Vacinas, vermífugos e antiparasitários'

    def __str__(self):
        return f'{self.nome} - {self.animal.nome}'


class Anexo(models.Model):
    animal = models.ForeignKey(
        Animal,
        on_delete=models.CASCADE,
        related_name='anexos'
    )

    arquivo = models.FileField('Arquivo', upload_to='anexos/')
    descricao = models.CharField(
        'Descrição', max_length=200, blank=True,
        help_text='Ex.: exame de sangue, receita, termo de adoção'
    )
    data_envio = models.DateTimeField('Enviado em', auto_now_add=True, null=True)

    class Meta:
        ordering = ['-id']

    @property
    def nome_arquivo(self):
        return self.arquivo.name.rsplit('/', 1)[-1]

    def __str__(self):
        return f'Anexo - {self.animal.nome}'


class Adotante(models.Model):
    nome = models.CharField(max_length=150)
    telefone = models.CharField(max_length=20)
    email = models.EmailField(blank=True)
    endereco = models.CharField(max_length=255, blank=True)
    observacoes = models.TextField(blank=True)
    data_cadastro = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Adotante'
        verbose_name_plural = 'Adotantes'
        ordering = ['nome']

    def __str__(self):
        return self.nome


class SolicitacaoAdocao(models.Model):
    STATUS_SOLICITACAO = [
        ('Pendente', 'Pendente'),
        ('Aprovada', 'Aprovada'),
        ('Recusada', 'Recusada'),
        ('Cancelada', 'Cancelada'),
    ]

    animal = models.ForeignKey(
        Animal,
        on_delete=models.PROTECT,
        related_name='solicitacoes_adocao'
    )

    adotante = models.ForeignKey(
        Adotante,
        on_delete=models.PROTECT,
        related_name='solicitacoes_adocao'
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_SOLICITACAO,
        default='Pendente'
    )

    data_solicitacao = models.DateTimeField(auto_now_add=True)

    data_aprovacao = models.DateTimeField(
        null=True,
        blank=True
    )

    observacoes = models.TextField(blank=True)

    class Meta:
        verbose_name = 'Solicitação de adoção'
        verbose_name_plural = 'Solicitações de adoção'
        ordering = ['-data_solicitacao']

        constraints = [
            models.UniqueConstraint(
                fields=['animal'],
                condition=models.Q(status='Aprovada'),
                name='unica_adocao_aprovada_por_animal'
            )
        ]

    def clean(self):
        super().clean()

        if not self.animal_id:
            return

        animal = Animal.objects.get(pk=self.animal_id)

        if self.pk:
            anterior = SolicitacaoAdocao.objects.filter(
                pk=self.pk
            ).first()
        else:
            anterior = None

        # Não permite trocar o animal de uma adoção aprovada.
        if anterior and anterior.status == 'Aprovada':
            if anterior.animal_id != self.animal_id:
                raise ValidationError({
                    'animal': 'Não é permitido trocar o animal de uma adoção aprovada.'
                })

        # Uma aprovação existente pode ser editada sem
        # exigir que o animal volte a ficar disponível.
        mesma_aprovacao = (
            anterior is not None
            and anterior.status == 'Aprovada'
            and self.status == 'Aprovada'
            and anterior.animal_id == self.animal_id
        )

        if self.status == 'Aprovada' and not mesma_aprovacao:
            if animal.status != 'Disponível':
                raise ValidationError({
                    'animal': 'Este animal não está disponível para adoção.'
                })

        if self.status == 'Pendente' and animal.status != 'Disponível':
            if not (
                anterior
                and anterior.status == 'Pendente'
                and anterior.animal_id == self.animal_id
            ):
                raise ValidationError({
                    'animal': 'Este animal não está disponível para adoção.'
                })

        outra_aprovacao = SolicitacaoAdocao.objects.filter(
            animal_id=self.animal_id,
            status='Aprovada'
        )

        if self.pk:
            outra_aprovacao = outra_aprovacao.exclude(pk=self.pk)

        if self.status == 'Aprovada' and outra_aprovacao.exists():
            raise ValidationError({
                'animal': 'Este animal já possui uma adoção aprovada.'
            })

    def save(self, *args, **kwargs):
        with transaction.atomic():
            # Bloqueia o animal durante a operação nos
            # bancos que suportam SELECT FOR UPDATE.
            if self.animal_id:
                animal = Animal.objects.select_for_update().get(
                    pk=self.animal_id
                )
            else:
                animal = None

            anterior = None

            if self.pk:
                anterior = SolicitacaoAdocao.objects.filter(
                    pk=self.pk
                ).first()

            self.full_clean()

            aprovacao_nova = (
                self.status == 'Aprovada'
                and (
                    anterior is None
                    or anterior.status != 'Aprovada'
                )
            )

            if aprovacao_nova:
                self.data_aprovacao = timezone.now()

            elif self.status != 'Aprovada':
                self.data_aprovacao = None

            super().save(*args, **kwargs)

            if aprovacao_nova and animal:
                animal.status = 'Adotado'
                animal.save(update_fields=['status'])

    def __str__(self):
        return f'{self.adotante.nome} - {self.animal.nome}'
