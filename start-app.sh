#\!/bin/bash

echo "🦠 Starting Pandemic Dash Tool..."
echo "=================================="

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}🧹 Cleaning up previous runs...${NC}"
docker-compose -f docker-compose-dash.yml down -v --remove-orphans > /dev/null 2>&1

echo -e "${BLUE}🏗️  Building and starting containers...${NC}"
docker-compose -f docker-compose-dash.yml up --build -d

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Containers started successfully\!${NC}"
else
    echo -e "${RED}❌ Failed to start containers${NC}"
    exit 1
fi

echo -e "${BLUE}⏳ Waiting for services to initialize...${NC}"
sleep 30

echo -e "${BLUE}🔄 Resetting simulation database...${NC}"
curl -s http://localhost:8000/api/reset > /dev/null 2>&1

echo ""
echo -e "${GREEN}🎉 Application is ready\!${NC}"
echo "=================================="
echo -e "${GREEN}📱 Frontend:${NC} http://localhost:8050"
echo -e "${GREEN}🔧 Backend:${NC}  http://localhost:8000"
echo ""
echo -e "${BLUE}📊 Container Status:${NC}"
docker-compose -f docker-compose-dash.yml ps

echo ""
echo -e "${BLUE}🧪 To test the simulation:${NC}"
echo "1. Open http://localhost:8050 in your browser"
echo "2. Configure a scenario and click 'Play'"
echo "3. Watch realistic epidemic curves (not flat lines\!)"
echo ""
echo -e "${BLUE}🛑 To stop:${NC} docker-compose -f docker-compose-dash.yml down"
EOF < /dev/null