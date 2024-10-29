// instructions for using the web interface, adapted from written tutorials provided during 10/16/2024 epiEngage demo
// NOTE: any changes made SINCE 10/16/2024 are NOT reflected in this guide
// <Instructions /> is rendered in the accordion buttons of UserGuide.js
import React from 'react';

const Instructions = () => {
  return (
    <div className="instructions">
      <section className="text">
        <p>Set the scenario with the 'Set Scenario' button in the top-left corner of the screen</p>
        <img src={ require('../images/userGuide-setScenario.png') } alt="Setting the Scenario" />
        <p>Select 'Disease Parameters' from the dropdown menu to specify starting conditions for the outbreak</p>
        <ul className="bullet-points">
          <li>R0: average number of secondary infections in a susceptible population</li>
          <li>Latency period (days): average number of days spent asymptomatic immediately after infection</li>
          <li>Asymptomatic period (days): average number of days spent infectious, but not yet symptomatic</li>
          <li>Symptomatic period (days): average number of days spent symptomatic and infectious</li>
          <li>Infection fatality rate (proportion): proportion of infections that lead to death</li>
        </ul>
        <img src={ require('../images/userGuide-parameters1.png') } alt="Selecting Parameters" />
        <img src={ require('../images/userGuide-parameters2.png') } alt="Inputting Parameters" />
        <p>Load a preset scenario from the catalog and hit the 'Save' button</p>
        <img src={ require('../images/userGuide-presetSave.png') } alt="Saving Parameters" />
        <p>Select 'Initial Cases' from the dropdown menu to specify initial infections </p>
        <img src={ require('../images/userGuide-InitialCases1.png') } alt="Saving Parameters" />
        <p>Click the '+ Add Cases' button to add initial cases for a particular county</p>
        <img src={ require('../images/userGuide-InitialCases2.png') } alt="Saving Parameters" />
        <p>For instance, enter the following entries:</p>
        <ul className="bullet-points">
          <li>Location: Travis</li>
          <li>Number of Cases: 100</li>
          <li>Age Group: 0-4 years</li>
        </ul>
        <img src={ require('../images/userGuide-InitialCases3.png') } alt="Adding Initial Cases" />
        <ul className="bullet-points">
          <li>Location: Harris</li>
          <li>Number of Cases: 100</li>
          <li>Age Group: 0-4 years</li>
        </ul>
        <img src={ require('../images/userGuide-InitialCases4.png') } alt="Additional Initial Cases" />
        <p>After adding cases, click 'Save and Close' to submit initial cases</p>
        <p>Saved scenario parameters and initial cases will be summarized in the left-hand panel</p>
        {/* <img src={ require('./images/userGuide-summaryPanel.png') } alt="Summary Panel" /> */}
        <p>Click the 'Play' button in the bottom-left corner to run the simulation</p>
        <img src={ require('../images/userGuide-playScenario.png') } alt="Running the Simulation" style={{ width: '50%' }} />
        <p>Hovering over the map will display the infections for specific counties</p>
        <img src={ require('../images/userGuide-onHover.png') } alt="Hovering over Counties" style={{ width: '50%' }}/>
        <p>The infection map can be toggled to display the number of infected individuals per county</p>
        <img src={ require('../images/userGuide-countToggle.png') } alt="Toggling Absolute Counts" style={{ width: '50%' }}/>
        <p>Hover over the line chart at the bottom of the screen to see total statewide compartment counts</p>
        <img src={ require('../images/userGuide-lineChart.png') } alt="Line Chart" style={{ width: '50%' }} />
        <p>Clicking on a compartment in the legend will toggle that compartment on or off in the line chart</p>
        <img src={ require('../images/userGuide-toggleCompartments.png') } alt="Toggling Compartments" style={{ width: '50%' }}/>
        <p>
          The table on the right-hand side of the screen can be sorted alphabetically by county or in 
          ascending/descending order based on infections or deaths
        </p>
        <p>
          Use the search bar above the table to search for specific counties
        </p>
        <img src={ require('../images/userGuide-countySearch.png') } alt="Searching for Counties" style={{ width: "50%" }} />
        <p>The 'Pause' button will halt the simulation</p>
        <img src={ require('../images/userGuide-pause.png') } alt="Pausing the Simulation" style={{ width: '50%' }}/>
        <p>Once the simulation is paused, slide the timeline back and forth to navigate to specific days</p>
        <img src={ require('../images/userGuide-timelineSlide.png') } alt="Scrubbing the Timeline" style={{ width: '50%' }} />
        <p>
          To change disease parameters, edit initial cases, or include non-pharmaceutical interventions, the simulation
          must first be reset. Clicking the 'Reset Simulation' button in the left-hand pane will reset the simulator
        </p>
        <img src={ require('../images/userGuide-resetButton.png') } alt="Reset Button" />
        <p>Interventions are added using the '+ Add Interventions' button beneath the 'Set Scenario' button</p>
        <img src={ require('../images/userGuide-setScenario.png') } alt="Setting the Scenario" />
        <p>
          Select 'Non-Pharmaceutical' from the dropdown menu to add non-pharmaceutical interventions, or NPIs
        </p>
        <img src={ require('../images/userGuide-NPIs1.png') } alt="Selecting NPIs" />
        <p> Click the 'Add New NPI' button to confirm NPI parameters</p>
        <ul className="bullet-points">
          <li>NPI start (simulation day): day of simulation on which the NPI is initiated</li>
          <li>NPI duration (days): the number of days the NPI is active</li>
          <li>
            NPI effectiveness (proportion): age-specific reduction in susceptibility 
            (0 = no protection; 1 = complete protection)
          </li>
        </ul>
        <img src={ require('../images/userGuide-NPIs2.png') } alt="Selecting NPIs" />
        <p>After adding, click 'Save' to submit NPIs to the simulator</p>
        <img src={ require('../images/userGuide-NPIs3.png') } alt="Saving NPIs" />
        <p>Clicking 'Interventions' in the left-hand summary pane will display intervention information</p>
        <img src={ require('../images/userGuide-NPIs4.png') } alt="Summarized NPIs" />
      </section>
    </div>
  )
};

export default Instructions;
