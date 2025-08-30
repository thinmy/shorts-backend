#!/bin/bash

# Script para backup do banco de dados

BACKUP_DIR="./backups"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="shorts_platform_backup_$DATE.sql"

echo "🗃️ Criando backup do banco de dados..."

# Criar diretório de backup se não existir
mkdir -p $BACKUP_DIR

# Fazer backup
docker-compose exec -T postgres pg_dump -U postgres shorts_platform > "$BACKUP_DIR/$BACKUP_FILE"

if [ $? -eq 0 ]; then
    echo "✅ Backup criado com sucesso: $BACKUP_DIR/$BACKUP_FILE"
    
    # Comprimir o backup
    gzip "$BACKUP_DIR/$BACKUP_FILE"
    echo "🗜️ Backup comprimido: $BACKUP_DIR/$BACKUP_FILE.gz"
    
    # Manter apenas os 7 backups mais recentes
    find $BACKUP_DIR -name "*.sql.gz" -type f -mtime +7 -delete
    echo "🧹 Backups antigos removidos (mantendo últimos 7 dias)"
else
    echo "❌ Erro ao criar backup"
    exit 1
fi
