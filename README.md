# Sistema de gestão – Associação de Proteção Animal Peludinhos

Sistema web (Python + Django + SQLite) para a ONG controlar os animais acolhidos,
vacinas/vermífugos/antiparasitários, documentos, adoções e atendimentos/ajudas.
O acesso é só com login (a dona da ONG e a Lilian).

## Como rodar

```bash
python -m venv venv
venv\Scripts\activate        # Windows  (Linux/Mac: source venv/bin/activate)
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser   # cria o login
python manage.py dados_exemplo     # opcional: cadastra dados de exemplo
python manage.py runserver
```

Abra http://127.0.0.1:8000 e entre com o usuário criado.

## O que tem no sistema

| Tela | Endereço | O que faz |
|---|---|---|
| Painel | `/` | Números gerais, onde estão os animais, espécies, avisos de doses, últimos cadastros |
| Animais | `/animais/` | Lista com busca e filtros (espécie, situação, local, porte); cadastro, edição e exclusão |
| Ficha do animal | `/animais/<id>/` | Todos os dados, doses, anexos e histórico de adoção |
| Adoções | `/animais/adocoes/` | Registro de adoções; ao aprovar, o animal vira "Adotado" automaticamente |
| Adotantes | `/animais/adotantes/` | Cadastro das pessoas que adotam |
| Atendimentos | `/atendimentos/` | Ajudas a animais que não ficam no abrigo (castração, ração, resgate...) |
| Avisos | `/avisos/` | Doses atrasadas e que vencem nos próximos 7, 15 ou 30 dias |
| Admin | `/admin/` | Área administrativa do Django (criar usuários etc.) |

### Cadastro do animal
- **Espécie:** Cachorro, Gato ou Outro (com campo "Qual espécie?", ex.: macaco, coruja, cavalo).
- **Localização** (onde está): Abrigo 1, 2, 3, Lar temporário ou Internado.
- **Situação** (como está): Em tratamento, Disponível, Não disponível (com motivo obrigatório), Adotado ou Falecido.
- Raça, sexo, idade aproximada, porte, pelagem, origem (maus-tratos, abandono, atropelamento, outro),
  data de entrada, temperamento, informações clínicas, observações e foto.

### Doses
Cada registro tem **tipo** (Vacina, Vermífugo ou Antiparasitário), nome/produto, data de aplicação,
próxima dose e observação. A próxima dose alimenta os avisos do painel.

## Testes

```bash
python manage.py test
```
