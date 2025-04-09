#!/bin/bash

# Deployment script for Django on VPS

echo "🔄 Deployment Started..."
echo "🔄 Pulling latest changes from Git..."
# cd /home/YOUR_USER/YOUR_PROJECT_NAME || exit
git pull origin main

echo "🐍 Activating virtual environment..."
source venv/bin/activate

echo "📦 Installing dependencies..."
pip install -r requirements.txt


echo "🧹 Collecting static files..."
python manage.py collectstatic --noinput

echo "🔄 Applying database migrations..."
python manage.py makemigrations 
python manage.py migrate

#deactivate the virtual environment 
echo "🔄 Deactivating virtual environment..."
deactivate

#reload application so new changes could be reflected
pushd Equb_App_Backend
touch wsgi.py
popd

echo "🚀 Restarting Gunicorn..."
sudo systemctl restart gunicorn

echo "✅ Deployment finished!"
