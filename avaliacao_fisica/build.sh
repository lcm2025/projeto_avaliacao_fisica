#!/usr/bin/env bash
# Exit on error
set -o errexit

# 1. Cria estrutura de diretórios necessária
mkdir -p templates/registration
mkdir -p staticfiles

# 2. Instala dependências
pip install -r requirements.txt

# 3. Coleta arquivos estáticos (com verificação)
echo "Coletando arquivos estáticos..."
python manage.py collectstatic --noinput --clear

# 4. Aplica migrações
echo "Aplicando migrações do banco de dados..."
python manage.py migrate

# 5. (Opcional) Cria superusuário se não existir
echo "from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.create_superuser('admin', 'admin@example.com', 'senha') if not User.objects.filter(username='admin').exists() else None" | python manage.py shell