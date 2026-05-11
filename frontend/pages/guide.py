from dash import register_page
import dash_core_components as dcc

register_page(__name__)


def layout(**kwargs):
    return dcc.Markdown(
        """

## User Guide

### How to Use the Interactive Outbreak Simulator

1. **Select Disease Model:** Choose which epidemiological model to use (SEIRS, SEATIRD, etc.).
2. **Select State:** Choose which US state to simulate.
3. **Set Disease Parameters:** Configure the disease characteristics including reproduction number, incubation period, and other epidemiological parameters.
4. **Select Initial Cases:** Specify the number of cases per county and age group in the low severity risk group.
5. **Configure Interventions:** Set up non-pharmaceutical interventions or release vaccines from a stockpile.
6. **Run Simulation:** Click the "Play" button to start the simulation. You can pause it at any time.
7. **View Results:** Monitor the outbreak progression through the map, epidemic curve, and county data table. When finished, hit Pause, then use the bottom scroll bar to investigate different days. Click on compartment names in the legend to remove them from the plot.

---

### Tips & Need to Knows

- **Max time is 10min:** Each simulation will run for at most 10 minutes, so if the epidemic stops progressing this may be why.
- **Day limit is 200:** The epidemic will stop progressing at 200 days.
- **Stochastic SEATIRD is slow:** This stochastic model is the Gillespie Algorithm and will create an event queue for each individual exposed. A large population will take a long time to get through the queue and update per day.
- **Texas is slow:** Texas has the most counties of any US state and takes a long time to advance a simulation when the epidemic is in multiple counties. In general, daily simulation time increases with the number of nodes in the network (counties in the state).
- **All infectious travel in SEIR:** The SEIR model does not have an asymptomatic compartment, so we're assuming everyone in I is willing to travel while infectious. Future versions will let you control this proportion within the dashboard.
- **Hit pause and take screenshots:** You can zoom into the map and deselect compartments in the line plot while paused. We're working on a data export button as well, so in the meantime pause, zoom, explore, and take a screenshot.

---

### Disease Models Available

- **Deterministic vs Stochastic:** Deterministic uses Euler's Method to advance the simulation and can move fractions of a person; Stochastic is a Poisson draw (SEIR/S) or the Gillespie Algorithm (SEATIRD) moving only integer people. All models have a stochastic Binomial draw for new infections spread between counties.
- **SEIR:** Susceptible-Exposed-Infectious-Recovered — basic compartmental model.
- **SEIRS:** SEIR with waning immunity — Recovered can become susceptible again.
- **SEATIRD:** Adds Asymptomatic (A), Treatable (T), and Deceased (D) compartments to capture severity of disease.
<!-- - **SEIHRD:** Includes Hospitalization (H) and 3 infectious compartments (Asymptomatic, Pre-symptomatic, and Symptomatic) tracking. -->

---

### SEIR and SEIRS Model

- **S - Susceptible:** Individuals who can become infected.
- **E - Exposed:** Individuals who have been exposed but are not yet infectious.
- **I - Infectious:** Infectious individuals; the travel model assumes 20% are asymptomatic.
- **R - Recovered:** Individuals who have recovered and are immune, unless the immune period is set to a positive non-zero number.

---

### SEATIRD Model

- **S - Susceptible:** Individuals who can become infected.
- **E - Exposed:** Individuals who have been exposed but are not yet infectious.
- **A - Asymptomatic:** Infectious individuals without symptoms.
- **T - Treatable:** Symptomatic individuals who can receive antiviral treatment (planned intervention).
- **I - Infectious:** Symptomatic infectious individuals.
- **R - Recovered:** Individuals who have recovered and are immune.
- **D - Deceased:** Individuals who have died from the disease.



    """,
        style=({'padding': '20px', 'maxWidth': '800px', 'margin': '0 auto'}),
    )
