# Rodando o projeto Python/Django localmente

## Clonar Projeto do GitHub
(Você deve estar logado no GitHub com acesso ao projeto ou o projeto deve ser público)

## Setup inicial do ambiente virtual no VS Code
Navegue até o diretório do projeto e execute os seguintes comandos:

### Linux
\```bash
sudo apt-get install python3-venv
python3 -m venv .venv
source .venv/bin/activate
\```

### macOS

python3 -m venv .venv
source .venv/bin/activate


### Windows

py -3 -m venv .venv
.venv\scripts\activate


## Instalar dependências
Navegue até o diretório `.venv` do projeto e execute:

  pip install -r requirements.txt


## Configuração de ambiente
- Ter e ajustar o arquivo `.env` na raiz do projeto com as variáveis marcadas como **"desenvolvimento"** ativas e as **"produção"** comentadas/desativadas.
- Verificar se o `settings.py` está com as linhas marcadas como **"desenvolvimento"** ativas e as marcadas como **"produção"** comentadas/desativadas.

## Criação do Banco de Dados
**Nota**: Se você ainda não tem PostgreSQL instalado, instale-o seguindo esses links:
- [PostgreSQL Documentation](https://www.postgresql.org/docs/15/index.html)
- [Installation Tutorial](https://www.postgresql.org/docs/15/tutorial-install.html)

### Criar o banco de dados interno para desenvolvimento
Use a mesma senha e nome do BD que está no `.env` na parte de **"desenvolvimento"**. No prompt de comandos raiz do seu computador (não precisa ser no venv), execute:

psql -U postgres   
CREATE DATABASE nome_do_db;

### Migrações
Dentro do venv do projeto, execute:

python manage.py migrate

python manage.py makemigrations

python manage.py migrate


### Criar usuário admin / superuser
Dentro do venv do projeto, execute:

python manage.py createsuperuser


## Configuração de Filas (Opcional)
Se seu projeto usa filas gerenciadas pelo django-q, para ativá-lo execute:

python manage.py qcluster


## Rodar o projeto
Para rodar o projeto, no venv, execute:

python manage.py runserver


