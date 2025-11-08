# HealthFlow+ 🏥

> AI-powered personal health data platform that transforms scattered medical documents into an intelligent, searchable timeline.

## 🚀 Features

- **Document Intelligence**: Upload any medical document (PDFs, images, voice notes) and extract structured data automatically
- **Medical Entity Extraction**: Automatically identify medications, diagnoses, lab results, appointments, and more
- **Unified Timeline**: All your health events in one intelligent chronological view
- **AI Chat Assistant**: Ask natural language questions about your health history with RAG-powered semantic search
- **Voice Journaling**: Record symptoms and notes with automatic transcription
- **HIPAA-Ready Security**: Bank-level encryption with row-level security

## 🏗️ Tech Stack

### Backend
- **FastAPI** (Python 3.11+): High-performance async API
- **Supabase/PostgreSQL**: Database with pgvector for semantic search
- **OpenAI/Anthropic**: LLM for entity extraction and chat
- **Dedalus Labs**: Medical AI agents
- **Celery + Redis**: Background task processing
- **Pydantic V2**: Data validation and serialization

### Frontend
- **Next.js 15**: React framework with App Router
- **Shadcn UI**: Beautiful, accessible component library
- **TailwindCSS**: Utility-first CSS framework
- **React Query**: Data fetching and state management
- **Zustand**: Client-side state management
- **TypeScript**: Type-safe development

### Infrastructure
- **Docker & Docker Compose**: Containerization
- **Nginx**: Reverse proxy and load balancing
- **MinIO/S3**: Object storage for documents
- **Redis**: Caching and task queue
- **PostgreSQL + pgvector**: Vector database

## 📁 Project Structure

```
healthflow/
├── backend/                # FastAPI backend
│   ├── app/
│   │   ├── api/           # API routes
│   │   ├── core/          # Core configuration
│   │   ├── models/        # Database models
│   │   ├── schemas/       # Pydantic schemas
│   │   ├── services/      # Business logic
│   │   ├── tasks/         # Celery tasks
│   │   └── utils/         # Utilities
│   ├── tests/
│   ├── alembic/           # Database migrations
│   ├── Dockerfile
│   └── requirements.txt
│
├── frontend/              # Next.js frontend
│   ├── src/
│   │   ├── app/          # App router pages
│   │   ├── components/   # React components
│   │   ├── lib/          # Utilities and config
│   │   ├── hooks/        # Custom React hooks
│   │   ├── stores/       # Zustand stores
│   │   └── types/        # TypeScript types
│   ├── public/
│   ├── Dockerfile
│   └── package.json
│
├── shared/               # Shared types and schemas
│   └── types/
│
├── docs/                # Documentation
│   ├── api/
│   ├── architecture/
│   └── deployment/
│
├── scripts/             # Utility scripts
│   ├── setup.sh
│   └── migrate.sh
│
├── docker-compose.yml
├── docker-compose.prod.yml
├── .env.example
└── README.md
```

## 🚦 Quick Start

### Prerequisites

- Docker & Docker Compose
- Node.js 18+ (for local development)
- Python 3.11+ (for local development)
- Supabase account (or local Supabase)

### 1. Clone and Setup

```bash
# Clone the repository
git clone <repo-url>
cd healthflow

# Copy environment variables
cp .env.example .env

# Edit .env with your configuration
nano .env
```

### 2. Start with Docker Compose

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

The application will be available at:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

### 3. Local Development Setup

#### Backend

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run migrations
alembic upgrade head

# Start development server
uvicorn app.main:app --reload --port 8000
```

#### Frontend

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

## 🗄️ Database Setup

### Using Supabase Cloud

1. Create a project at [supabase.com](https://supabase.com)
2. Run the schema from `healthflow_schema.sql` in the SQL Editor
3. Update `.env` with your Supabase URL and keys

### Using Local Supabase

```bash
# Install Supabase CLI
npm install -g supabase

# Initialize Supabase
supabase init

# Start local Supabase
supabase start

# Run migrations
supabase db push
```

## 🔐 Environment Variables

See `.env.example` for all required environment variables:

```env
# Database
DATABASE_URL=postgresql://user:pass@localhost:5432/healthflow
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your-anon-key
SUPABASE_SERVICE_KEY=your-service-key

# API Keys
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
DEDALUS_API_KEY=...

# Storage
S3_BUCKET=healthflow-documents
S3_ENDPOINT=...
S3_ACCESS_KEY=...
S3_SECRET_KEY=...

# Redis
REDIS_URL=redis://localhost:6379

# Security
SECRET_KEY=your-secret-key-here
JWT_SECRET=your-jwt-secret-here

# Frontend
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_SUPABASE_URL=...
NEXT_PUBLIC_SUPABASE_ANON_KEY=...
```

## 🧪 Testing

### Backend Tests

```bash
cd backend
pytest tests/ -v --cov=app
```

### Frontend Tests

```bash
cd frontend
npm run test
npm run test:e2e
```

## 📦 Deployment

### Production Build

```bash
# Build all services
docker-compose -f docker-compose.prod.yml build

# Deploy
docker-compose -f docker-compose.prod.yml up -d
```

### Deploy to Cloud

See deployment guides in `docs/deployment/`:
- AWS ECS/Fargate
- Google Cloud Run
- DigitalOcean App Platform
- Vercel (Frontend) + Railway (Backend)

## 🛠️ Development

### API Development

```bash
# Add new migration
cd backend
alembic revision --autogenerate -m "description"

# Apply migration
alembic upgrade head

# Rollback migration
alembic downgrade -1
```

### Frontend Development

```bash
# Add Shadcn component
npx shadcn-ui@latest add button

# Run linting
npm run lint

# Format code
npm run format
```

## 📚 Documentation

- [API Documentation](./docs/api/README.md)
- [Architecture Overview](./docs/architecture/README.md)
- [Database Schema](./docs/database/README.md)
- [Deployment Guide](./docs/deployment/README.md)
- [Contributing Guide](./CONTRIBUTING.md)

## 🔒 Security

- All data encrypted at rest and in transit
- Row-level security (RLS) in Supabase
- HIPAA-compliant infrastructure ready
- Regular security audits and updates
- API rate limiting and authentication

## 📄 License

MIT License - see [LICENSE](./LICENSE) file

## 🤝 Contributing

Contributions are welcome! Please read [CONTRIBUTING.md](./CONTRIBUTING.md) for details.

## 💬 Support

- Documentation: [docs/](./docs)
- Issues: [GitHub Issues](https://github.com/yourorg/healthflow/issues)
- Email: support@healthflow.example

## 🙏 Acknowledgments

- [FastAPI](https://fastapi.tiangolo.com/)
- [Next.js](https://nextjs.org/)
- [Shadcn UI](https://ui.shadcn.com/)
- [Supabase](https://supabase.com/)
- [Dedalus Labs](https://www.dedaluslabs.ai/)

---

Built with ❤️ for better healthcare
