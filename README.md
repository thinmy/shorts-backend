# Shorts Platform - Monorepo

Uma plataforma completa para criação, edição e compartilhamento de vídeos curtos com integração de IA e redes sociais.

## 🚀 Tecnologias

### Backend
- **Python 3.13** com **Django 5.0**
- **Django REST Framework** para APIs
- **Celery** para processamento em background
- **PostgreSQL** como banco de dados
- **Redis** para cache e broker do Celery
- **yt-dlp** para download de vídeos do YouTube
- **moviepy** e **ffmpeg** para processamento de vídeo
- **OpenAI**, **Gemini** e **Groq** para IA (transcrição e análise)
- **OAuth2** com Google (expansível para outras redes)

### Frontend
- **React 18** com **Next.js 14**
- **TypeScript** para tipagem
- **Tailwind CSS** para estilização
- **Shadcn/ui** para componentes
- **React Query** para gerenciamento de estado remoto
- **LocalStorage** para estado local
- **NextAuth.js** para autenticação

### Integrações Sociais
- **YouTube API** - Upload e gerenciamento
- **Instagram Graph API** - Publicação de stories e posts
- **Twitter API v2** - Tweets com mídia
- **TikTok API** - Upload de vídeos

## 📁 Estrutura do Projeto

```
shorts-backend/
├── backend/                 # Django backend
│   ├── config/             # Configurações Django
│   ├── apps/               # Apps Django
│   │   ├── authentication/ # Autenticação e usuários
│   │   ├── videos/         # Gerenciamento de vídeos
│   │   ├── social_integration/ # Integração redes sociais
│   │   └── ai_processing/  # Processamento com IA
│   ├── utils/              # Utilitários
│   ├── media/              # Arquivos de mídia
│   └── requirements.txt    # Dependências Python
├── frontend/               # Next.js frontend
│   ├── src/
│   │   ├── app/           # App Router (Next.js 14)
│   │   ├── components/    # Componentes React
│   │   ├── lib/           # Utilitários e configurações
│   │   ├── hooks/         # Custom hooks
│   │   └── types/         # Tipos TypeScript
│   └── package.json       # Dependências Node.js
├── docker/                # Configurações Docker
├── scripts/               # Scripts úteis
├── docker-compose.yml     # Orquestração Docker
└── package.json          # Scripts do monorepo
```

## 🛠️ Configuração e Instalação

### Pré-requisitos
- Python 3.13+
- Node.js 18+
- PostgreSQL 15+
- Redis 7+
- FFmpeg

### 1. Clone o repositório
```bash
git clone <repository-url>
cd shorts-backend
```

### 2. Configuração com Docker (Recomendado)
```bash
# Copiar arquivos de ambiente
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env

# Subir os serviços
docker-compose up -d

# Executar migrações
docker-compose exec backend python manage.py migrate

# Criar superusuário
docker-compose exec backend python manage.py createsuperuser
```

### 3. Configuração Local

#### Backend
```bash
cd backend

# Criar ambiente virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate     # Windows

# Instalar dependências
pip install -r requirements.txt

# Configurar variáveis de ambiente
cp .env.example .env
# Editar .env com suas configurações

# Executar migrações
python manage.py migrate

# Criar superusuário
python manage.py createsuperuser

# Executar servidor
python manage.py runserver
```

#### Frontend
```bash
cd frontend

# Instalar dependências
npm install

# Configurar variáveis de ambiente
cp .env.example .env.local
# Editar .env.local com suas configurações

# Executar servidor de desenvolvimento
npm run dev
```

#### Celery (em terminal separado)
```bash
cd backend

# Worker
celery -A config worker -l info

# Beat (scheduler) - em outro terminal
celery -A config beat -l info
```

## 🔧 Configuração das APIs

### Variáveis de Ambiente Necessárias

#### APIs de IA
```env
OPENAI_API_KEY=sk-...
GEMINI_API_KEY=...
GROQ_API_KEY=...
```

#### OAuth Google
```env
GOOGLE_OAUTH2_CLIENT_ID=...
GOOGLE_OAUTH2_CLIENT_SECRET=...
```

#### APIs de Redes Sociais
```env
YOUTUBE_API_KEY=...
INSTAGRAM_ACCESS_TOKEN=...
TWITTER_API_KEY=...
TWITTER_API_SECRET=...
TIKTOK_ACCESS_TOKEN=...
```

## 🚀 Uso

### Fluxo Principal

1. **Autenticação**: Login via Google OAuth
2. **Upload de Vídeo**: Upload direto ou download do YouTube
3. **Processamento**: Automático via Celery
   - Geração de thumbnail
   - Transcrição com IA
   - Compressão/otimização
   - Análise de conteúdo
4. **Edição**: Interface para editar metadados
5. **Publicação**: Compartilhamento em múltiplas plataformas

### APIs Principais

#### Autenticação
- `POST /api/auth/register/` - Registro
- `GET /api/auth/profile/` - Perfil do usuário
- `POST /api/auth/social/connect/` - Conectar rede social

#### Vídeos
- `GET /api/videos/` - Listar vídeos
- `POST /api/videos/` - Upload de vídeo
- `POST /api/videos/youtube/download/` - Download do YouTube
- `GET /api/videos/{id}/processing-status/` - Status do processamento

#### IA
- `POST /api/ai/transcribe/` - Transcrever vídeo
- `POST /api/ai/analyze/` - Analisar conteúdo

#### Redes Sociais
- `GET /api/social/platforms/` - Plataformas disponíveis
- `POST /api/social/upload/` - Publicar em redes sociais

## 📊 Monitoramento

### Logs
- Backend: Django logs
- Celery: Worker e beat logs
- Frontend: Next.js logs

### Métricas
- Status dos workers Celery
- Tempo de processamento de vídeos
- Uso de APIs externas

## 🧪 Testes

```bash
# Backend
cd backend
python manage.py test

# Frontend
cd frontend
npm test

# Tudo
npm run test
```

## 🚢 Deploy

### Produção com Docker
```bash
# Build
docker-compose -f docker-compose.prod.yml build

# Deploy
docker-compose -f docker-compose.prod.yml up -d
```

### Considerações de Produção
- Usar PostgreSQL em servidor dedicado
- Redis com persistência
- CDN para arquivos de mídia (AWS S3 + CloudFront)
- Load balancer para múltiplas instâncias
- Monitoramento com Sentry/DataDog
- Backup automatizado do banco

## 📝 Licença

MIT License

## 🤝 Contribuição

1. Fork o projeto
2. Crie uma branch para sua feature
3. Commit suas mudanças
4. Push para a branch
5. Abra um Pull Request

## 📞 Suporte

Para dúvidas e suporte, abra uma issue no GitHub.