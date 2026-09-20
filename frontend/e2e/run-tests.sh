#!/bin/bash
# Run Playwright E2E tests with backend and frontend servers

set -e

echo "🚀 Starting MauEkspor E2E Tests..."

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Cleanup function
cleanup() {
    echo -e "\n${YELLOW}🛑 Shutting down servers...${NC}"
    [ -n "$BACKEND_PID" ] && kill $BACKEND_PID 2>/dev/null || true
    [ -n "$FRONTEND_PID" ] && kill $FRONTEND_PID 2>/dev/null || true
    wait $BACKEND_PID 2>/dev/null || true
    wait $FRONTEND_PID 2>/dev/null || true
    echo -e "${GREEN}✅ Servers stopped${NC}"
}

# Set trap to cleanup on exit
trap cleanup EXIT

# Start backend
echo -e "${YELLOW}📦 Starting backend server...${NC}"
cd ../backend
MAUEKSPOR_DATABASE_URL=sqlite:///./mauekspor.db .venv/bin/python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 > /tmp/backend.log 2>&1 &
BACKEND_PID=$!
echo -e "${GREEN}✅ Backend started (PID: $BACKEND_PID)${NC}"

# Wait for backend to be ready
echo -e "${YELLOW}⏳ Waiting for backend to be ready...${NC}"
for i in {1..30}; do
    if curl -s http://127.0.0.1:8000/docs > /dev/null 2>&1; then
        echo -e "${GREEN}✅ Backend is ready${NC}"
        break
    fi
    if [ $i -eq 30 ]; then
        echo -e "${RED}❌ Backend failed to start${NC}"
        cat /tmp/backend.log
        exit 1
    fi
    sleep 1
done

# Start frontend
echo -e "${YELLOW}🎨 Starting frontend server...${NC}"
cd ../frontend
pnpm dev > /tmp/frontend.log 2>&1 &
FRONTEND_PID=$!
echo -e "${GREEN}✅ Frontend started (PID: $FRONTEND_PID)${NC}"

# Wait for frontend to be ready
echo -e "${YELLOW}⏳ Waiting for frontend to be ready...${NC}"
for i in {1..30}; do
    if curl -s http://localhost:5173 > /dev/null 2>&1; then
        echo -e "${GREEN}✅ Frontend is ready${NC}"
        break
    fi
    if [ $i -eq 30 ]; then
        echo -e "${RED}❌ Frontend failed to start${NC}"
        cat /tmp/frontend.log
        exit 1
    fi
    sleep 1
done

# Run tests
echo -e "\n${GREEN}🎬 Running Playwright tests...${NC}\n"
pnpm exec playwright test "$@"

# Show report
if [ $? -eq 0 ]; then
    echo -e "\n${GREEN}✅ All tests passed!${NC}"
    echo -e "${YELLOW}📊 View the report with: pnpm test:e2e:report${NC}"
else
    echo -e "\n${RED}❌ Some tests failed${NC}"
    echo -e "${YELLOW}📊 View the report with: pnpm test:e2e:report${NC}"
    exit 1
fi
