#!/bin/bash

echo "🚀 Starting deployment..."

# Check if the repository exists in /root/equb
if [ ! -d "/root/equb" ]; then
  echo "📁 Repository not found, cloning it..."
  git clone https://github.com/mengistuabebe06/Equb_App_Backend /root/equb
else
  # Change to the repository directory
  cd /root/equb || exit
  echo "📥 Pulling latest code..."
  git pull origin main
fi

echo "🐍 Activating virtual environment..."
source venv/bin/activate

echo "📦 Installing requirements..."
pip install -r requirements.txt

echo "📂 Collecting static files..."
python manage.py collectstatic --noinput

echo "🗃️ Running migrations..."
python manage.py makemigrations
python manage.py migrate

echo "🔁 Restarting services..."
sudo systemctl restart gunicorn
sudo systemctl restart nginx

echo "✅ Deployment complete!"
