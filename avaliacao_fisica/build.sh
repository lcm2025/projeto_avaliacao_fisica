#!/usr/bin/env bash
# Exit on error

# Verifique se a pasta de templates existe
mkdir -p templates/registration
mkdir -p avaliacao/templates/avaliacao

set -o errexit

# Modify this line as needed for your package manager (pip, poetry, etc.)
pip install -r requirements.txt

# Convert static asset files
python manage.py collectstatic --no-input

# Apply any outstanding database migrations
python manage.py migrate