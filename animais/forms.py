from django import forms

from .models import Adotante, Anexo, Animal, SolicitacaoAdocao, Vacina


class EstiloBootstrapMixin:
    """Aplica as classes do Bootstrap em todos os campos do formulário."""

    def aplicar_estilo(self):
        for field in self.fields.values():
            widget = field.widget
            if isinstance(widget, (forms.Select, forms.SelectMultiple)):
                css = 'form-select'
            elif isinstance(widget, forms.CheckboxInput):
                css = 'form-check-input'
            else:
                css = 'form-control'
            widget.attrs.setdefault('class', css)
            # Texto da opção vazia em português
            if isinstance(field, forms.ChoiceField) and not isinstance(field, forms.ModelChoiceField):
                field.choices = [
                    ('', 'Selecione...') if valor == '' else (valor, rotulo)
                    for valor, rotulo in field.choices
                ]
            elif isinstance(field, forms.ModelChoiceField):
                field.empty_label = 'Selecione...'


DATA = {'type': 'date'}


class AnimalForm(EstiloBootstrapMixin, forms.ModelForm):
    class Meta:
        model = Animal
        fields = [
            'nome', 'especie', 'especie_outra', 'raca', 'sexo', 'idade',
            'porte', 'pelagem', 'localizacao', 'status', 'motivo_indisponivel',
            'origem', 'data_entrada', 'temperamento', 'info_clinica',
            'descricao', 'foto',
        ]
        widgets = {
            'data_entrada': forms.DateInput(attrs=DATA, format='%Y-%m-%d'),
            'info_clinica': forms.Textarea(attrs={'rows': 3}),
            'descricao': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.aplicar_estilo()


class VacinaForm(EstiloBootstrapMixin, forms.ModelForm):
    class Meta:
        model = Vacina
        fields = ['tipo', 'nome', 'data_aplicacao', 'proxima_dose', 'observacao']
        widgets = {
            'data_aplicacao': forms.DateInput(attrs=DATA, format='%Y-%m-%d'),
            'proxima_dose': forms.DateInput(attrs=DATA, format='%Y-%m-%d'),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.aplicar_estilo()

    def clean(self):
        dados = super().clean()
        aplicacao = dados.get('data_aplicacao')
        proxima = dados.get('proxima_dose')
        if aplicacao and proxima and proxima < aplicacao:
            self.add_error('proxima_dose', 'A próxima dose não pode ser antes da aplicação.')
        return dados


class AnexoForm(EstiloBootstrapMixin, forms.ModelForm):
    class Meta:
        model = Anexo
        fields = ['arquivo', 'descricao']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.aplicar_estilo()


class AdotanteForm(EstiloBootstrapMixin, forms.ModelForm):
    class Meta:
        model = Adotante
        fields = ['nome', 'telefone', 'email', 'endereco', 'observacoes']
        widgets = {'observacoes': forms.Textarea(attrs={'rows': 3})}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.aplicar_estilo()


class AdocaoForm(EstiloBootstrapMixin, forms.ModelForm):
    class Meta:
        model = SolicitacaoAdocao
        fields = ['animal', 'adotante', 'status', 'observacoes']
        widgets = {'observacoes': forms.Textarea(attrs={'rows': 3})}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Em uma adoção nova só aparecem os animais disponíveis.
        if not self.instance.pk:
            self.fields['animal'].queryset = Animal.objects.filter(status='Disponível')
        self.aplicar_estilo()
