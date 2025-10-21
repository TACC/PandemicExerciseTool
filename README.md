# 🦠 Pandemic Dash Tool

A Python Dash-based pandemic simulation application that integrates with the real **PandemicExerciseSimulator** engine to generate scientifically accurate epidemic curves using the SEATIRD epidemiological model.

\![Pandemic Simulation](https://img.shields.io/badge/Status-Working-brightgreen) \![Docker](https://img.shields.io/badge/Docker-Ready-blue) \![Python](https://img.shields.io/badge/Python-Dash-orange)

## ✨ Features

- 🔬 **Real PES Engine**: Uses the actual PandemicExerciseSimulator for scientific accuracy
- 📊 **SEATIRD Model**: Complete epidemiological modeling (Susceptible, Exposed, Asymptomatic, Treatable, Infected, Recovered, Deceased)
- 🗺️ **Texas Counties**: Interactive map with county-level infection visualization
- ⏱️ **Real-time Simulation**: Live epidemic progression with realistic growth curves
- 🐳 **Docker Ready**: Complete containerized deployment
- 🎛️ **Interactive Controls**: Configure disease parameters, initial cases, and interventions

## 🚀 Quick Start

### Prerequisites
- Docker and Docker Compose
- 8GB+ RAM recommended
- Ports 8000, 8050, 6379, 27017 available

### One-Command Startup
```bash
git clone https://github.com/saroshaprasla/PandemicExerciseTool-Dash.git
docker-compose -f docker-compose-dash.yml up --build -d
```

### Access the Application
- **Main Application**: http://localhost:8050
- **Backend API**: http://localhost:8000

## 📋 Detailed Setup

### 1. Clean Start (Recommended)
```bash
# Navigate to project
cd PandemicExerciseTool-Dash

# Complete cleanup and restart
docker-compose -f docker-compose-dash.yml down -v --remove-orphans
docker-compose -f docker-compose-dash.yml up --build -d

# Wait for services to initialize
sleep 30

# Reset simulation database
curl -s http://localhost:8000/api/reset
```

### 2. Verify Installation
```bash
# Check all services are running
docker-compose -f docker-compose-dash.yml ps

# Test backend
curl http://localhost:8000/

# Test frontend
curl -I http://localhost:8050/
```

## 🧪 Test Simulation

Create and run a test scenario:

```bash
# Create 2009 H1N1 scenario
curl -X POST -H "Content-Type: application/json" -d '{
  "disease_name": "2009 H1N1",
  "R0": 1.2,
  "beta_scale": 10.0,
  "tau": 1.2,
  "kappa": 1.9,
  "gamma": 4.1,
  "chi": 1.0,
  "rho": 0.39,
  "nu": "0.000022319,0.000040975,0.000083729,0.000061809,0.000008978",
  "initial_infected": "[{\"county\": \"201\", \"infected\": 100, \"age_group\": \"1\"}]",
  "npis": "[]"
}' http://localhost:8000/api/pet/

# Run simulation (replace 12 with returned ID)
curl http://localhost:8000/api/pet/12/run

# Check results after 30 seconds
sleep 30
curl http://localhost:8000/api/output/10 | jq '.total_summary.I'
```

## 📊 Expected Results

The application generates realistic epidemic curves:
- **Day 10**: ~10,679 infected (early growth)
- **Day 20**: ~37,429 infected (epidemic peak)
- **Day 25**: ~22,935 infected (decline phase)

**No more flat lines at zero\!** 🎉

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Dash Frontend │────│ Django Backend  │────│ Celery Worker   │
│   (Port 8050)   │    │   (Port 8000)   │    │ (PES Simulator) │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
                    ┌─────────────────┐    ┌─────────────────┐
                    │   MongoDB       │    │     Redis       │
                    │  (Port 27017)   │    │   (Port 6379)   │
                    └─────────────────┘    └─────────────────┘
```

### Services
- **dash-frontend**: Python Dash web application
- **django-backend**: REST API and data management
- **celery-worker**: Background simulation processing with real PES engine
- **mongo-db**: Simulation data storage
- **redis**: Celery message broker and caching

## 🔧 Troubleshooting

### Common Issues

**Containers won't start:**
```bash
docker-compose -f docker-compose-dash.yml down -v
docker system prune -f
docker-compose -f docker-compose-dash.yml up --build -d
```

**Old simulation data:**
```bash
curl http://localhost:8000/api/reset
```

**Check logs:**
```bash
docker-compose -f docker-compose-dash.yml logs [service-name]
```

### Success Indicators
- ✅ All 5 containers show "Up" status
- ✅ Frontend loads without errors at http://localhost:8050
- ✅ Backend returns JSON at http://localhost:8000/api/
- ✅ Simulations produce realistic epidemic curves (not flat lines)
- ✅ Maps show infection spread across Texas counties

## 🛑 Stop Application

```bash
docker-compose -f docker-compose-dash.yml down
```

## 📚 Original Projects

This project builds upon:
- [PandemicExerciseTool](https://github.com/TACC/PandemicExerciseTool) - Original React frontend
- [PandemicExerciseSimulator](https://github.com/TACC/PandemicExerciseSimulator) - SEATIRD simulation engine



## 📄 License

This project maintains the same license as the original TACC repositories.
EOF < /dev/null
