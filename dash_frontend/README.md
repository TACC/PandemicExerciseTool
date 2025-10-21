# Pandemic Exercise Tool - Dash Frontend

This is a Python Dash conversion of the React frontend for the Pandemic Exercise Tool. It maintains the same functionality and user interface as the original React application while providing a Python-based web interface.

## Features

- **Interactive Simulation**: Real-time pandemic simulation with play/pause controls
- **Parameter Configuration**: Set disease parameters, initial cases, and interventions
- **Visualization**: 
  - Geographic map showing disease spread across Texas counties
  - Epidemic curve with SEATIRD compartmental model
  - County-by-county data table
- **Toggle Views**: Switch between count and percentage displays
- **User Guide**: Comprehensive instructions and model information

## Architecture

The application is structured with modular components:

- `app.py`: Main Dash application with layout and callbacks
- `api_client.py`: Backend API integration for simulation management
- `data_loader.py`: Texas counties data loading and processing
- `visualization.py`: Chart and map generation utilities

## Setup and Installation

### Local Development

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Ensure the Django backend is running on `localhost:8000`

3. Run the Dash application:
```bash
python app.py
```

4. Access the application at `http://localhost:8050`

### Docker Deployment

1. Build the Docker image:
```bash
docker build -t pandemic-dash-frontend .
```

2. Run the container:
```bash
docker run -p 8050:8050 --network host pandemic-dash-frontend
```

## API Integration

The frontend connects to the Django backend running on `localhost:8000` with the following endpoints:

- `POST /api/pet/` - Create simulation parameters
- `GET /api/pet/{id}/run` - Start simulation execution
- `GET /api/output/{day}` - Retrieve simulation results for specific day
- `GET /api/delete/{task_id}` - Stop running simulation
- `GET /api/reset` - Reset simulation state

## Key Components

### Navigation
- **Home**: Main simulation interface
- **User Guide**: Instructions and model documentation

### Main Interface Panels
- **Left Panel**: Parameter configuration and intervention settings
- **Middle Panel**: Geographic map and epidemic curve charts
- **Right Panel**: County data summary table
- **Bottom Panel**: Simulation controls and timeline slider

### Simulation Flow
1. Configure disease parameters (R₀, incubation period, etc.)
2. Select initial case locations and counts
3. Set up interventions (NPIs, vaccines, antivirals)
4. Save scenario to prepare simulation
5. Play simulation and monitor real-time results
6. Review historical data using timeline controls

## Data Sources

- Texas county geographic data
- Population demographics
- FIPS codes for county identification

## Model Information

The application implements a SEATIRD compartmental epidemiological model:
- **S**: Susceptible
- **E**: Exposed
- **A**: Asymptomatic
- **T**: Treatable
- **I**: Infected
- **R**: Recovered
- **D**: Deceased

## Development Notes

This Dash frontend maintains exact feature parity with the original React application, including:
- Same parameter inputs and validation
- Identical visualization layouts and interactions
- Matching simulation control behavior
- Equivalent user interface elements and styling

The conversion preserves all functionality while leveraging Python's ecosystem for data processing and visualization.