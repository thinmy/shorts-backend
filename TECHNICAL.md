# Documentação Técnica - Shorts Platform

## Arquitetura do Sistema

### Backend (Django)

#### Apps Django

1. **Authentication** (`apps.authentication`)
   - Modelo customizado de usuário
   - OAuth2 com Google
   - Gerenciamento de contas sociais
   - Endpoints: `/api/auth/`

2. **Videos** (`apps.videos`)
   - Upload e processamento de vídeos
   - Download do YouTube via yt-dlp
   - Gerenciamento de tags
   - Tasks do Celery para processamento
   - Endpoints: `/api/videos/`

3. **Social Integration** (`apps.social_integration`)
   - Upload para múltiplas plataformas
   - Agendamento de publicações
   - Analytics básicas
   - Endpoints: `/api/social/`

4. **AI Processing** (`apps.ai_processing`)
   - Transcrição com OpenAI/Groq/Gemini
   - Análise de conteúdo
   - Geração de tags automáticas
   - Endpoints: `/api/ai/`

#### Tecnologias Principais

- **Django 5.0** - Framework web
- **Django REST Framework** - APIs REST
- **Celery** - Tasks assíncronas
- **PostgreSQL** - Banco de dados principal
- **Redis** - Cache e broker do Celery
- **yt-dlp** - Download de vídeos
- **moviepy** - Processamento de vídeo
- **ffmpeg** - Codificação de vídeo

#### Tasks do Celery

1. `download_youtube_video` - Download de vídeos do YouTube
2. `process_video` - Processamento geral de vídeos
3. `generate_thumbnail` - Geração de thumbnails
4. `extract_transcription` - Transcrição com IA
5. `compress_video` - Compressão de vídeos
6. `upload_to_social_platform` - Upload para redes sociais

### Frontend (Next.js)

#### Estrutura

```
src/
├── app/           # App Router (Next.js 14)
├── components/    # Componentes reutilizáveis
├── lib/          # Utilitários e configurações
├── hooks/        # Custom React hooks
└── types/        # Tipos TypeScript
```

#### Tecnologias

- **Next.js 14** - Framework React com SSR
- **TypeScript** - Tipagem estática
- **Tailwind CSS** - Framework CSS
- **Shadcn/ui** - Biblioteca de componentes
- **React Query** - Gerenciamento de estado server
- **Axios** - Cliente HTTP
- **NextAuth.js** - Autenticação

#### Gerenciamento de Estado

- **Local**: useState, useReducer, localStorage
- **Remoto**: React Query para APIs
- **Global**: Context API para dados do usuário

### Integrações de IA

#### OpenAI
- **Whisper**: Transcrição de áudio
- **GPT-3.5/4**: Análise de conteúdo e geração de tags

#### Google Gemini
- **Gemini Pro**: Análise multimodal
- **Future**: Transcrição direta

#### Groq
- **Whisper Large V3**: Transcrição rápida

### Integração com Redes Sociais

#### YouTube
- **YouTube Data API v3**
- Upload de vídeos
- Gerenciamento de canal

#### Instagram
- **Instagram Graph API**
- Stories e posts de vídeo
- Requires Business Account

#### Twitter/X
- **Twitter API v2**
- Upload de mídia
- Tweets com vídeo

#### TikTok
- **TikTok API**
- Upload de vídeos
- Requires Developer Account

## Fluxo de Dados

### Upload de Vídeo

1. Frontend envia arquivo para `/api/videos/`
2. Django salva arquivo e cria registro no banco
3. Celery task `process_video` é iniciado
4. Sub-tasks são criadas:
   - `generate_thumbnail`
   - `extract_transcription`
   - `compress_video`
5. Status é atualizado conforme conclusão

### Download do YouTube

1. Frontend envia URL para `/api/videos/youtube/download/`
2. Celery task `download_youtube_video` é iniciado
3. yt-dlp baixa o vídeo
4. Vídeo é salvo e processamento normal inicia

### Publicação Social

1. Frontend seleciona vídeo e plataformas
2. Requisição para `/api/social/upload/`
3. Celery task `upload_to_social_platform` para cada plataforma
4. APIs específicas são chamadas
5. URLs e IDs externos são salvos

## Configuração de Ambiente

### Variáveis Essenciais

```env
# Database
DATABASE_URL=postgresql://user:pass@host:port/db

# Redis
REDIS_URL=redis://host:port/db

# AI Services
OPENAI_API_KEY=sk-...
GEMINI_API_KEY=...
GROQ_API_KEY=...

# OAuth
GOOGLE_OAUTH2_CLIENT_ID=...
GOOGLE_OAUTH2_CLIENT_SECRET=...

# Social APIs
YOUTUBE_API_KEY=...
INSTAGRAM_ACCESS_TOKEN=...
TWITTER_API_KEY=...
TIKTOK_ACCESS_TOKEN=...
```

## Deployment

### Docker Compose (Desenvolvimento)

```bash
docker-compose up -d
```

### Produção

1. Use PostgreSQL gerenciado
2. Redis com persistência
3. CDN para arquivos de mídia (S3 + CloudFront)
4. Load balancer (nginx)
5. Monitoring (Sentry, DataDog)
6. Backup automatizado

### Escalabilidade

- **Horizontal**: Múltiplas instâncias do Django
- **Celery Workers**: Escalar conforme carga
- **Database**: Read replicas para consultas
- **Media**: CDN e storage distribuído

## Monitoramento

### Métricas Importantes

- Tempo de processamento de vídeos
- Taxa de sucesso de uploads sociais
- Uso das APIs de IA
- Performance do banco de dados
- Status dos workers Celery

### Logs

- Django: Aplicação e erros
- Celery: Tasks e workers
- nginx: Acesso e proxy
- PostgreSQL: Query logs (produção)

## Segurança

### Implementadas

- OAuth2 para autenticação
- CORS configurado
- Validação de uploads
- Rate limiting (via nginx)
- Sanitização de dados

### A Implementar

- Rate limiting por usuário
- Watermarking de vídeos
- Auditoria de ações
- Backup criptografado

## Performance

### Otimizações Implementadas

- Compressão de vídeos automática
- Thumbnails otimizadas
- Cache de consultas frequentes
- Paginação de resultados

### Futuras Otimizações

- CDN para vídeos
- Transcoding adaptativo
- Cache de thumbnails
- Database indexing avançado

## Troubleshooting

### Problemas Comuns

1. **Celery tasks falham**
   - Verificar Redis connection
   - Verificar dependências (ffmpeg)
   - Logs do worker

2. **Upload de vídeo falha**
   - Tamanho do arquivo
   - Formato suportado
   - Espaço em disco

3. **APIs sociais falham**
   - Tokens expirados
   - Rate limits
   - Permissões da conta

### Debug

```bash
# Logs do Celery
docker-compose logs celery

# Status do Redis
docker-compose exec redis redis-cli ping

# Logs do Django
docker-compose logs backend

# Conectar ao banco
docker-compose exec postgres psql -U postgres shorts_platform
```
