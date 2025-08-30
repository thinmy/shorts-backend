#!/bin/bash

# Script para configuração inicial do projeto

echo "🚀 Configurando Shorts Platform..."

# Verificar se o Docker está instalado
if ! command -v docker &> /dev/null; then
    echo "❌ Docker não encontrado. Por favor, instale o Docker primeiro."
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose não encontrado. Por favor, instale o Docker Compose primeiro."
    exit 1
fi

# Copiar arquivos de ambiente se não existirem
if [ ! -f backend/.env ]; then
    echo "📋 Copiando arquivo de ambiente do backend..."
    cp backend/.env.example backend/.env
    echo "✅ Arquivo backend/.env criado. Por favor, configure suas variáveis de ambiente."
fi

if [ ! -f frontend/.env.local ]; then
    echo "📋 Copiando arquivo de ambiente do frontend..."
    cp frontend/.env.example frontend/.env.local
    echo "✅ Arquivo frontend/.env.local criado. Por favor, configure suas variáveis de ambiente."
fi

# Subir os serviços
echo "🐳 Subindo os serviços Docker..."
docker-compose up -d postgres redis

# Aguardar o banco estar pronto
echo "⏳ Aguardando PostgreSQL estar pronto..."
sleep 10

# Executar migrações
echo "🗃️ Executando migrações do banco de dados..."
docker-compose run --rm backend python manage.py migrate

# Criar superusuário (opcional)
read -p "Deseja criar um superusuário? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    docker-compose run --rm backend python manage.py createsuperuser
fi

# Instalar dependências do frontend
echo "📦 Instalando dependências do frontend..."
cd frontend && npm install && cd ..

echo "🎉 Configuração concluída!"
echo ""
echo "Para iniciar o desenvolvimento:"
echo "  - Backend: docker-compose up backend"
echo "  - Frontend: cd frontend && npm run dev"
echo "  - Celery: docker-compose up celery"
echo ""
echo "Ou execute tudo junto: npm run dev"
