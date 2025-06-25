
# Як запустити проект
1. Клонування та налаштування
bash# Клонування репозиторію
git clone https://github.com/AntonyNest/MLOps.git
cd MLOps

## Створення віртуального середовища
python -m venv venv
source venv/bin/activate  # Linux/Mac

#### або venv\Scripts\activate  # Windows

## Встановлення залежностей
pip install -r requirements.txt
2. Ініціалізація DVC
bash# Ініціалізація DVC
dvc init

## Додання віддаленого сховища (MinIO)
dvc remote add -d minio s3://MLOps
dvc remote modify minio endpointurl http://localhost:9000
dvc remote modify minio access_key_id minioadmin
dvc remote modify minio secret_access_key minioadmin

## Запуск пайплайну
dvc repro
3. Запуск інфраструктури
bash# Запуск всіх сервісів
docker-compose up -d

## Перевірка статусу
docker-compose ps

## Структура проекту
mlops-data-platform/
├── data/
│   ├── raw/                    # Необроблені дані
│   ├── labeled/                # Розмічені дані
│   └── processed/              # Оброблені дані для ML
├── docker/
│   ├── docker-compose.yml      # Інфраструктура
│   └── label-studio/
│       └── Dockerfile
├── dvc/
│   ├── .dvc/                   # DVC конфігурація
│   ├── dvc.yaml               # DVC пайплайн
│   └── params.yaml            # Параметри
├── scripts/
│   ├── setup_data.py          # Ініціалізація датасету
│   ├── export_labels.py       # Експорт розмітки
│   └── validate_data.py       # Валідація даних
├── notebooks/
│   └── data_exploration.ipynb # Аналіз даних
├── .dvcignore
├── .gitignore
├── requirements.txt
└── README.md

## Build scripts for different environments


#!/bin/bash
## build.sh - Build script for production

set -e

echo "Building MLOps Platform containers..."

## Build base images
docker build -t mlops-platform:base .
docker build -t mlops-platform:processor -f docker/Dockerfile.processor .
docker build -t mlops-platform:api -f docker/Dockerfile.api .
docker build -t mlops-platform:jupyter -f docker/Dockerfile.jupyter .
docker build -t mlops-platform:monitoring -f docker/Dockerfile.monitoring .

echo "All containers built successfully!"

## Tag for registry
if [ "$1" = "push" ]; then
    echo "Tagging and pushing to registry..."
    
    docker tag mlops-platform:base registry.example.com/mlops-platform:base
    docker tag mlops-platform:processor registry.example.com/mlops-platform:processor
    docker tag mlops-platform:api registry.example.com/mlops-platform:api
    
    docker push registry.example.com/mlops-platform:base
    docker push registry.example.com/mlops-platform:processor
    docker push registry.example.com/mlops-platform:api
    
    echo "Images pushed to registry!"
fi

---

#!/bin/bash  
## build-dev.sh - Development build script

set -e

echo "Building development containers..."

## Build with development target
docker-compose -f docker-compose.yml -f docker-compose.override.yml build

echo "Development containers ready!"
echo "Run: docker-compose -f docker-compose.yml -f docker-compose.override.yml up -d"