#!/bin/bash

echo "Starting Pandemic Exercise Tool with Dash Frontend"
echo "=================================================="

# Check if Docker is available
if ! command -v docker &> /dev/null; then
    echo "Error: Docker is not installed or not in PATH"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "Error: Docker Compose is not installed or not in PATH"
    exit 1
fi

# Build and start services
echo "Building and starting services..."
docker-compose -f docker-compose-dash.yml up --build -d

echo ""
echo "Services starting up..."
echo "- MongoDB: localhost:27017"
echo "- Redis: localhost:6379"
echo "- Django Backend: localhost:8000"
echo "- Dash Frontend: localhost:8050"
echo ""

# Wait for services to be ready
echo "Waiting for services to be ready..."
sleep 10

# Check if services are running
if docker-compose -f docker-compose-dash.yml ps | grep -q "Up"; then
    echo "✓ Services are running successfully!"
    echo ""
    echo "🎉 Pandemic Exercise Tool is ready!"
    echo "   Frontend: http://localhost:8050"
    echo "   Backend API: http://localhost:8000"
    echo ""
    echo "To stop the services, run:"
    echo "   docker-compose -f docker-compose-dash.yml down"
else
    echo "✗ Some services failed to start. Check logs with:"
    echo "   docker-compose -f docker-compose-dash.yml logs"
fi