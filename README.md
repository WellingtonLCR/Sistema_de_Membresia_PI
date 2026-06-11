# Igreja Membresia

Sistema web para gerenciamento de membros de igreja, desenvolvido com **Python**, **Flask** e **MySQL**. Permite cadastrar membros com cargos e células, registrar contribuições financeiras e controlar o acesso ao sistema por meio de login e sessão.

---

## Índice

- [Funcionalidades](#funcionalidades)
- [Tecnologias utilizadas](#tecnologias-utilizadas)
- [Como baixar e rodar o projeto](#como-baixar-e-rodar-o-projeto)
- [Credenciais de acesso padrão](#credenciais-de-acesso-padrão)
- [Estrutura do projeto](#estrutura-do-projeto)
- [Desenvolvedores](#desenvolvedores)

---

## Funcionalidades

- **Autenticação** — Login e logout com verificação de senha (hash), proteção de rotas e controle de sessão
- **Membros** — Cadastro, listagem, visualização, edição e exclusão de membros com dados pessoais, endereço, cargo, célula e status
- **Cargos** — CRUD completo de cargos/funções (Pastor, Diácono, etc.)
- **Células** — Cadastro e gestão de células com líder, dia/horário e endereço do encontro
- **Contribuições** — Registro e listagem de contribuições financeiras (Dízimo, Oferta, Missões, Construção, Outros) com totalizador mensal
- **Dashboard** — Visão geral com contadores de membros ativos, células ativas e contribuições do mês, além dos últimos membros cadastrados
- **Admin padrão automático** — Na primeira execução, o sistema cria automaticamente um usuário administrador caso o banco esteja vazio

---

## Tecnologias utilizadas

| Camada | Tecnologia |
|---|---|
| Linguagem | Python 3.10+ |
| Framework web | Flask 3.1.0 |
| Banco de dados | MySQL (via XAMPP) |
| Conector MySQL | mysql-connector-python 9.1.0 |
| Segurança de senhas | Werkzeug 3.1.3 |
| Front-end | Bootstrap 5.3.3 + Bootstrap Icons 1.11.3 |
| Templates | Jinja2 (incluso no Flask) |

---

## Como baixar e rodar o projeto

### Pré-requisitos

Certifique-se de ter instalado na sua máquina:

- **Git**
- **Python 3.10 ou superior** (com "Add Python to PATH" marcado na instalação)
- **XAMPP** com o módulo **MySQL** ativo

> Antes de continuar, abra o **XAMPP Control Panel** e clique em **Start** no módulo MySQL.

---

### Passo 1 — Clonar o repositório

```bash
cd %USERPROFILE%\Desktop
git clone https://github.com/WellingtonLCR/Sistema_de_Membresia_PI.git
cd Sistema_de_Membresia_PI
```

---

### Passo 2 — Criar e ativar o ambiente virtual

```bash
python -m venv venv
venv\Scripts\activate
```

O terminal exibirá `(venv)` no início da linha quando o ambiente estiver ativo.

---

### Passo 3 — Instalar as dependências

```bash
pip install -r requirements.txt
```

---

### Passo 4 — Verificar a conexão com o banco

Abra o arquivo `db.py` e confira as configurações de conexão:

```python
_DB_PARAMS = {
    'host':     'localhost',
    'user':     'root',
    'password': '',          # preencha se definiu senha no XAMPP
    'database': 'igreja_membros',
    ...
}
```

Faça o mesmo ajuste na função `iniciar_bd()` no final do mesmo arquivo.

---

### Passo 5 — Rodar a aplicação

```bash
python app.py
```

Na primeira execução, o terminal exibirá:

```
Banco e tabelas inicializados com sucesso!
Admin criado: admin@igreja.com / admin1234
 * Running on http://127.0.0.1:5000
```

Acesse `http://127.0.0.1:5000` no navegador.

---

## Credenciais de acesso padrão

| Campo | Valor |
|---|---|
| E-mail | admin@igreja.com |
| Senha | admin1234 |

> Recomenda-se alterar a senha padrão após o primeiro login.

---

## Estrutura do projeto

```
Sistema_de_Membresia_PI/
├── static/
│   └── css/
│       └── style.css
├── templates/
│   ├── auth/
│   │   └── login.html
│   └── dashboard/
│       ├── cargos/
│       │   ├── form.html
│       │   └── listar.html
│       ├── celulas/
│       │   ├── form.html
│       │   └── listar.html
│       ├── contribuicoes/
│       │   ├── form.html
│       │   └── listar.html
│       ├── membros/
│       │   ├── form.html
│       │   ├── listar.html
│       │   └── visualizar.html
│       ├── equipe.html
│       └── home.html
├── app.py
├── db.py
├── schema.sql
├── requirements.txt
└── .gitignore
```

---

## Desenvolvedores

Projeto desenvolvido para a disciplina de **Programação para Internet — ILP951** · Fatec Jahu · 2026.

| Nome | Área | GitHub | LinkedIn |
|---|---|---|---|
| Wellington Luis Costa Ribeiro | Front-end & UI/UX | [WellingtonLCR](https://github.com/WellingtonLCR) | [LinkedIn](https://www.linkedin.com/in/wellington-luis-costa-ribeiro-51452018a/) |
| Thiago Souza | Back-end & Banco de Dados | — | — |
