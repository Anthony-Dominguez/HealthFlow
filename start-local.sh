#!/bin/bash
# Start HealthFlow+ Locally (without Docker for app, but using Docker for databases)

set -e

echo "🚀 Starting HealthFlow+ (Local Development Mode)"
echo ""

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo -e "${RED}❌ Docker is not running${NC}"
    echo "Please start Docker Desktop and try again"
    exit 1
fi

echo -e "${BLUE}📦 Starting Database Services...${NC}"

# Start PostgreSQL if not running
if ! docker ps | grep -q healthflow-postgres; then
    echo "Starting PostgreSQL..."
    docker run -d --name healthflow-postgres \
        -e POSTGRES_PASSWORD=postgres \
        -e POSTGRES_DB=healthflow \
        -p 5432:5432 \
        pgvector/pgvector:pg15 2>/dev/null || docker start healthflow-postgres
fi

# Start Redis if not running
if ! docker ps | grep -q healthflow-redis; then
    echo "Starting Redis..."
    docker run -d --name healthflow-redis \
        -p 6379:6379 \
        redis:7-alpine 2>/dev/null || docker start healthflow-redis
fi

echo -e "${GREEN}✅ Database services started${NC}"
echo ""

# Wait for PostgreSQL to be ready
echo "Waiting for PostgreSQL to be ready..."
sleep 3

# Check if schema needs to be loaded
echo -e "${BLUE}📊 Checking database schema...${NC}"
SCHEMA_EXISTS=$(docker exec healthflow-postgres psql -U postgres -d healthflow -tAc "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema='public' AND table_name='users';")

if [ "$SCHEMA_EXISTS" = "0" ]; then
    echo "Loading database schema..."
    docker exec -i healthflow-postgres psql -U postgres -d healthflow < healthflow_schema.sql
    echo -e "${GREEN}✅ Database schema loaded${NC}"
else
    echo -e "${GREEN}✅ Database schema already exists${NC}"
fi

echo ""
echo -e "${BLUE}🔧 Starting Backend...${NC}"
echo "Backend will be available at: ${GREEN}http://localhost:8000${NC}"
echo ""

# Start backend in a new terminal (macOS)
if [[ "$OSTYPE" == "darwin"* ]]; then
    osascript -e 'tell application "Terminal" to do script "cd '$(pwd)'/backend && source venv/bin/activate 2>/dev/null || python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt && uvicorn app.main:app --reload"'
fi

echo -e "${BLUE}🎨 Starting Frontend...${NC}"
echo "Frontend will be available at: ${GREEN}http://localhost:3000${NC}"
echo ""

# Start frontend in a new terminal (macOS)
if [[ "$OSTYPE" == "darwin"* ]]; then
    osascript -e 'tell application "Terminal" to do script "cd '$(pwd)'/frontend && npm install && npm run dev"'
fi

echo ""
echo -e "${GREEN}✨ HealthFlow+ is starting!${NC}"
echo ""
echo "Services:"
echo "  🌐 Frontend:  http://localhost:3000"
echo "  🔌 Backend:   http://localhost:8000"
echo "  📚 API Docs:  http://localhost:8000/docs"
echo "  🗄️  Database: postgresql://postgres:postgres@localhost:5432/healthflow"
echo ""
echo "To stop:"
echo "  docker stop healthflow-postgres healthflow-redis"
echo ""
