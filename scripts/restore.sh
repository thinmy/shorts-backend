#!/bin/bash

# Script para restaurar backup do banco de dados

if [ -z "$1" ]; then
    echo "Uso: ./restore.sh <arquivo_backup.sql.gz>"
    echo "Exemplo: ./restore.sh backups/shorts_platform_backup_20240101_120000.sql.gz"
    exit 1
fi

BACKUP_FILE=$1

if [ ! -f "$BACKUP_FILE" ]; then
    echo "❌ Arquivo de backup não encontrado: $BACKUP_FILE"
    exit 1
fi

echo "⚠️ ATENÇÃO: Esta operação irá substituir todos os dados do banco atual!"
read -p "Tem certeza que deseja continuar? (digite 'sim' para confirmar): " -r
if [[ ! $REPLY = "sim" ]]; then
    echo "Operação cancelada."
    exit 1
fi

echo "🗃️ Restaurando backup do banco de dados..."

# Parar serviços que usam o banco
echo "⏹️ Parando serviços..."
docker-compose stop backend celery celery-beat

# Descomprimir se necessário
if [[ $BACKUP_FILE == *.gz ]]; then
    echo "📤 Descomprimindo backup..."
    gunzip -c "$BACKUP_FILE" > /tmp/restore.sql
    RESTORE_FILE="/tmp/restore.sql"
else
    RESTORE_FILE="$BACKUP_FILE"
fi

# Restaurar banco
echo "📥 Restaurando dados..."
docker-compose exec -T postgres psql -U postgres -c "DROP DATABASE IF EXISTS shorts_platform;"
docker-compose exec -T postgres psql -U postgres -c "CREATE DATABASE shorts_platform;"
docker-compose exec -T postgres psql -U postgres shorts_platform < "$RESTORE_FILE"

if [ $? -eq 0 ]; then
    echo "✅ Backup restaurado com sucesso!"
    
    # Limpar arquivo temporário
    if [[ $BACKUP_FILE == *.gz ]]; then
        rm /tmp/restore.sql
    fi
    
    # Reiniciar serviços
    echo "🚀 Reiniciando serviços..."
    docker-compose up -d backend celery celery-beat
    
    echo "🎉 Restauração concluída!"
else
    echo "❌ Erro ao restaurar backup"
    exit 1
fi
