import React from 'react';
import './UserGuideView.css'; // Ensure this CSS file is updated


const appendixData = [
  {
    filename: 'contact_matrix.5',
    description: '5x5 matrix of contact ratios between age groups',
    contents: [
      '45.1228487783,8.7808312353,11.7757947836,6.10114751268,4.02227175596',
      '8.7808312353,41.2889143668,13.3332813497,7.847051289,4.22656343551',
      '11.7757947836,13.3332813497,21.4270155984,13.7392636644,6.92483172729',
      '6.10114751268,7.847051289,13.7392636644,18.0482119252,9.45371062356',
      '4.02227175596,4.22656343551,6.92483172729,9.45371062356,14.0529294262'

    ]
  },
  {
    filename: 'county_age_matrix.5',
    description: 'Populations for each county divided into age groups',
    contents: [
      '"fips","0-4","5-24","25-49","50-64","65+"',
      '1,3292,13222,23406,9535,6898',
      '3,1134,4152,3997,2234,1803',
      '5,6223,23990,27426,14327,10768',
      '7,1314,6019,6481,5964,5454',
      '...',
      '501,690,2275,2152,1288,903',
      '503,1198,4880,5090,3504,3576',
      '505,1335,4794,4170,1973,1898',
      '507,1044,4097,3550,1835,1348',

    ]
  },
  {
    filename: 'flow_reduction.5',
    description: 'List of flow reduction values for each age group',
    contents: [
      '10.0',
      '2.0',
      '1.0',
      '1.0',
      '2.0'
    ]
  },
  {
    filename: 'high_risk_ratios.5',
    description: 'List of risk ratio for each age group',
    contents: [
      '0.0803804',
      '0.146264700734',
      '0.21454520795',
      '0.337052864254',
      '0.529643792782'
    ]
  },
  {
    filename: 'nu_value_matrix.5',
    description: 'Nx4 columns (N=num of age groups) low/high death rate x low/high risk. Nu is the transmitting (asymptomatic/treatable/infectious) to deceased rate',
    contents: [
      '0.0000223193,0.000201089,0.00201371,0.0200626',
      '0.0000409747056486,0.000370019305934,0.000766898700611,0.00724895553818',
      '0.0000837293183202,0.000756613214362,0.00131294401009,0.0127322284368',
      '0.0000618089564208,0.000557948045036,0.000481092688113,0.00443918094028',
      '0.00000897814893927,0.0000808383088526,0.000127992694545,0.00116150251502'
      
    ]
  },
  {
    filename: 'relative_susceptibility.5',
    description: 'List of relative susceptibility for each age group',
    contents: [
      '1.00',
      '0.98',
      '0.94',
      '0.91',
      '0.66'
      
    ]
  },
  {
    filename: 'vaccine_adherence.5',
    description: 'List of vaccine adherences for each age group',
    contents: [
      '0.4345',
      '0.2983',
      '0.3885',
      '0.45',
      '0.696'
      
    ]
  },
  {
    filename: 'vaccine_effectiveness.5',
    description: 'List of vaccine effectiveness for each age group',
    contents: [
      '0.8',
      '0.8',
      '0.8',
      '0.8',
      '0.8'
    ]
  },
  {
    filename: 'work_matrix_rel.csv',
    description: 'NxN matrix (N=num of counties) for travel flow',
    contents: [
      '0.835120481928,0.0,0.000361445783133,0.0,0.0, ...',
      '0.0,0.781945589448,0.0,0.0,0.0, ...',
      '0.000120973839407,0.0,0.909420837744,0.0,0.0, ...',
      '0.0,0.0,0.0,0.628093245666,0.0, ...',
      '0.0,0.0,0, ...',
      '0,0.0,0.365157944366, ...',
      '...'
      
    ]
  }

];

const UserGuideView = () => {
  return (
    <div className="user-guide-view">
      <section className="text">
        <h2>Pandemic Exercise Simulator</h2>
        <p>Updated as of 8/6/2024</p>
        <a href="https://github.com/TACC/PandemicExerciseSimulator" target="_blank" rel="noopener noreferrer" className="github-link">
        https://github.com/TACC/PandemicExerciseSimulator
        </a>
        <p><strong>Overview:</strong> This is a Python implementation of a Pandemic Exercise Simulator using a SEATIRD compartment model and binomial travel model. The simulator was implemented in such a way that it is modular, and can use alternative disease models, travel models, and eventually interventions (e.g. PHAs, antivirals, vaccines).</p>
        <p>
        This simulator can be run using the command line interface. It will also be the main calculation engine behind the graphical web app, hosted here (in development): </p>
        <a href="https://github.com/TACC/PandemicExerciseTool" target="_blank" rel="noopener noreferrer" className="github-link">
        https://github.com/TACC/PandemicExerciseTool
        </a>
        <p></p>
        <p className="needed-section">
          <strong>Needed: </strong>This tool is still in development and will benefit from testing and expert review. In particular, we need:
        </p>
        <ul className="bullet-points">
          <li>Review of the Stochastic SEATIRD Disease Model implementation.</li>
          <li>Review of the Binomial Travel Model implementation.</li>
          <li>A range of example input data and parameters, as well as expected outputs for testing and verification.</li>
        </ul>
        <p><strong>Data Description</strong></p>
        <p>This simulator expects the following inputs to be present:</p>
      </section>

      <section className="table-section">
        <table className="guide-table">
          <thead>
            <tr>
              <th>File Name</th>
              <th>Description</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td>INPUT.json</td>
              <td>Simulation properties file</td>
            </tr>
            <tr>
              <td>contact_matrix.5</td>
              <td>NxN matrix (N=num of age groups) of contact ratios between age groups</td>
            </tr>
            <tr>
              <td>county_age_matrix.5</td>
              <td>Populations for each county divided into age groups</td>
            </tr>
            <tr>
              <td>flow_reduction.5</td>
              <td>List of flow reduction values for each age group</td>
            </tr>
            <tr>
              <td>high_risk_ratios.5</td>
              <td>List of risk ratio for each age group</td>
            </tr>
            <tr>
              <td>nu_value_matrix.5</td>
              <td>Nx4 columns (N=num of age groups) low/high death rate x low/high risk. Nu is the transmitting (asymptomatic/treatable/infectious) to deceased rate</td>
            </tr>
            <tr>
              <td>relative_susceptibility.5</td>
              <td>List of relative susceptibility for each age group</td>
            </tr>
            <tr>
              <td>vaccine_adherence.5</td>
              <td>List of vaccine adherences for each age group</td>
            </tr>
            <tr>
              <td>vaccine_effectiveness.5</td>
              <td>List of vaccine effectiveness for each age group</td>
            </tr>
            <tr>
              <td>work_matrix_rel.csv</td>
              <td>NxN matrix (N=num of counties) for travel flow</td>
            </tr>
          </tbody>
        </table>
        <p>(Samples of each of these files are provided at the end of this document.)</p>
      </section>

      <section className="text">
        <p><strong>Parameter Description</strong></p>
        <p>The simulator expects the following parameters to be defined in the INPUT.json file:</p>
      </section>

      <section className="table-section">
        <table className="guide-table">
          <thead>
            <tr>
              <th>File Name</th>
              <th>Example</th>
              <th>Description</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td>R0</td>
              <td>1.2</td>
              <td>Basic reproduction number associated with the pandemic</td>
            </tr>
            <tr>
              <td>beta_scale</td>
              <td>65</td>
              <td>R0 correction factor – R0 is divided by this number and stored as beta</td>
            </tr>
            <tr>
              <td>tau</td>
              <td>1.2</td>
              <td>Latency period (days)</td>
            </tr>
            <tr>
              <td>kappa</td>
              <td>1.9</td>
              <td>Asymptomatic infectious period (days)</td>
            </tr>
            <tr>
              <td>gamma</td>
              <td>4.1</td>
              <td>Total infectious period (days)</td>
            </tr>
            <tr>
              <td>chi</td>
              <td>1.0</td>
              <td>Treatable to infectious rate (days)?</td>
            </tr>
            <tr>
              <td>rho</td>
              <td>0.39</td>
              <td>Multiplier to reduce the age-specific mixing rate pattern to account for reduced rate of contact when traveling</td>
            </tr>
            <tr>
              <td>nu_high</td>
              <td>yes</td>
              <td>Use high mortality rates (yes) or low mortality rates (no)</td>
            </tr>
            <tr>
              <td>vaccine_wastage_factor</td>
              <td>60</td>
              <td>Half the vaccine stockpile will be wasted every N days</td>
            </tr>
            <tr>
              <td>antiviral_effectiveness</td>
              <td>0.15</td>
              <td>Antiviral effectiveness is the probability that an individual treated within the treatment window will recover</td>
            </tr>
            <tr>
              <td>antiviral_wastage_factor</td>
              <td>60</td>
              <td>Half the antiviral stockpile will be wasted every N days</td>
            </tr>
          </tbody>
        </table>
      </section>
      <br></br>
      <section className="text">
        <p><strong>Main Simulation Engine</strong></p>
        <p>The simulation begins in the main loop of src/simulator.py. The following pseudocode roughly describes the workflow:</p>
      </section>

      <section className="code-section">
        <h3>Example Code</h3>
        <pre className="code-chunk">
          <code>
{`1  properties <= input_properties(argument.properties)
2  parameters <= load_model_parameters(properties)
3  simulation_time <= instantiate_day(argument.day)
4  network <= load_population_file(properties)
5  travel_flow <= load_travel_flow_data(properties)
6  disease_model <= instantiate_disease_model()
7  disease_model.set_initial_conditions(parameters.initial_infected)
8  travel_model <= instantiate_travel_model()
9  writer <= instantiate_writer(output_filename)
10 
11 # run() method
12 for each DAY:
13     for each NODE in NETWORK
14         increment day
15         # distributions, treatments, stockpiles go here
16         disease_model.simulate()
17     travel_model.travel()
18     writer.write_output()
`}
          </code>
        </pre>
      </section>


      <section className="text">
        <p>A plain text description of the workflow is as follows:</p>
        <ul className="bullet-points">
          <li><strong>Line 1: </strong>All simulation properties are read in from the input file. This includes parameters, names of data files, initial conditions (e.g. initial number of infected per age group per county), public health announcement schedule, and vaccine stockpile schedule.</li>
          <li><strong>Line 2: </strong>The data files are all opened and read in and stored alongside other parameters in a <i>parameters</i> object.</li>
          <li><strong>Line 3: </strong>The <i>simulation_time</i> is set by the user on the command line in number of days. The <i>simulation_time</i> object is used to control the flow of the simulation and store the state of the simulation.</li>
          <li><strong>Line 4: </strong>The <i>network</i> object contains a list of nodes, each node in this case containing the compartment data for a county. In several steps, the network object is instantiated, the population data file is read in and mapped to nodes, then the initial Susceptible population is partitioned between high risk and low risk compartments based on input high-risk ratios.</li>
          <li><strong>Line 5: </strong>The <i>travel_flow</i> data is read in and stored as an NxN matrix where N is the number of nodes in the <i>network</i></li>
          <li><strong>Line 6-7: </strong>A <i>disease_model</i> is instantiated. Currently only one model is available. Once additional models are implemented, this is where we will have a decision tree to choose between multiple models based on user input. The <i>disease_model</i> then sets some initial conditions including initial number of infected per age group per county. Initial infected are moved from Susceptible to Exposed. Moving population to Exposed also triggers new events to be added to the event queue – see description of Disease Model below. </li>
          <li><strong>Line 8: </strong>The <i>travel_model</i> is instantiated. Only one model is available at this time, but this is where we would have a decision tree to choose between multiple models. </li>
          <li><strong>Line 9: </strong>The <i>writer</i> object is used to write the simulation state to file or database.</li>
          <li><strong>Line 12: </strong>Iterate over each day</li>
          <li><strong>Line 13: </strong>Iterate over each <i>node</i> in the network </li>
          <li><strong>Line 15: </strong>(IN DEVELOPMENT) Before applying <i>disease_model</i>, handle distributions, treatments, and stockpiles. </li>
          <li><strong>Line 16: </strong>The <i>simulate()</i> method is the entrypoint into the main simulation logic for the disease_model, described in more detail below. </li>
          <li><strong>Line 17: </strong>After each node has been simulated, then the <i>travel_model</i> runs once per day to account for transmission during travel between nodes, described in more detail below.</li>
          <li><strong>Line 18: </strong>Each day, write output snapshot of the entire state of the system for restarts, mapping, plotting, etc.</li>
        </ul>
      </section>
      <section className="text">
        <p><strong>Disease Model</strong></p>
        <p>The current implementation, Stochastic SEATIRD, was adapted from a previous code base. The main entrypoint to this disease model is a method called <strong>simulate()</strong>, which is called for each day, for each node, from <strong>src/simulator.py</strong>. This method models the progression of individuals through different stages of disease, including susceptible, exposed, asymptomatic, treatable, infectious, recovered, and deceased. The output of the method is the updated state of the population, including the number of individuals in each disease stage for each age group, risk group, and vaccination status, at the end of the simulation period.</p>
        <p>The main logic of the method is to work through an <i>“event queue” </i> associated with each node. Events are either <i>transitions</i> from one compartment to another (e.g. I => R), or contacts. The event queue is initialized by the user-input initial infected, then it continues to take on new events through the course of simulation.</p>
        <p>A plain text description of the workflow is as follows:</p>
      </section>
      <ul className="bullet-points">
      <li><strong>Line 2:</strong> The event_queue is a list of possible transitions that can occur. It is seeded with new events every time someone transitions from Susceptible to Exposed. It is seeded for the first time when the user inputs initial infections in the parameters. The list of possible events include:
        <ul className="sub-list">
          <li>{'{EtoA, AtoT, AoR, AtoD, TtoI, TtoR, TtoD, ItoR, ItoD, CONTACT}'}</li>
        </ul>
      </li>
      <li><strong>Line 3-4:</strong> The next action taken depends on what type of event is pulled off the queue. </li>
      <li><strong>Line 5-6:</strong> If the event type is one of {'{EtoA, AtoT, AtoR, AtoD}'}, then:
        <ul className="sub-list">
          <li>The old compartment is decremented by one and the new compartment is incremented by one. For example, if the event is EtoA, then one individual is moved from the Exposed compartment into the Asymptomatic compartment. Then the event is removed from the queue.</li>
        </ul>
      </li>
      <li><strong>Line 7-9:</strong> If the event type is one of {'{TtoI, TtoR, TtoD, ItoR, ItoD}'}, then:
        <ul className="sub-list">
          <li>A function called keep_event() is called that will return True or False based on a probabilistic check. If True, then the transition between compartments occurs. If False, then the transition does not occur, but a counter is incremented. As the number of skipped events increases, the likelihood of skipping an event decreases. Following either outcome (True or False), the event is discarded from the queue.</li>
        </ul>
      </li>
      <li><strong>Line 10:</strong> The last type of event is a CONTACT event.</li>
      <li><strong>Line 11:</strong> A probabilistic check called keep_contact() is performed. If the check fails (False), a counter is incremented and increases the likelihood of the check passing (True) the next time.</li>
      <li><strong>Line 12-15:</strong> If the keep_contact() check returns True, then an individual is moved from Susceptible to Exposed. Next, a new Schedule object is instantiated with the current time. The Schedule object models the timing of transition of disease through the various compartments for that Exposed individual. The math (described below) uses some random number generation and information about the current population and disease parameters to determine which events will occur. Finally, the parameters of the Schedule object will seed new transition events and new contact events into the queue.</li>
    </ul>  

    

    <section className="text">


      <p>The main logic of the Stochastic SEATIRD model happens inside the Schedule object. Every time an individual is exposed (whether through user-defined initial infected OR through contact events), a new Schedule object is instantiated which defines the timing for all subsequent transitions for that individual. Given a time in units of simulation day, the Schedule object solves the following equations to determine transition time (T) to other compartments:</p>
     
     
     
      <p>Ta = rand_exp(tau) + now</p>
      <p>Tt = rand_exp(kappa) + Ta</p>
      <p>Ti = chi + Tt</p>
      <p>T{'d<=a'} = rand_exp(nu) + Ta</p>
      <p>T{'d=t,i'} = rand_exp(nu) + Tt</p>
      <p>T{'r<=a'} = rand_exp(gamma) + Ta</p>
      <p>T{'r<=t,i'} = rand_exp(gamma) + Tt</p>
      <br></br>
      <p>Where: </p> 

      <ul className="bullet-points">
          <li><strong>Ta</strong> is time from exposed to asymptomatic</li>
          <li><strong>Tt</strong> is time from asymptomatic to treatable</li>
          <li><strong>Ti</strong> is time from treatable to infectious</li>
          <li><strong>T{'d<=a'}</strong> is time from asymptomatic to deceased</li>
          <li><strong>T{'d=t,i'}</strong> is time from treatable/infectious to deceased</li>
          <li><strong>T{'r<=a'}</strong> is time from asymptomatic to recovered</li>
          <li><strong>T{'r<=t,i'}</strong> is time from treatable/infectious to recovered</li>
          <li><strong>now</strong> is the current day</li>
          <li><strong>tau</strong> is latency period in days</li>
          <li><strong>kappa</strong> is asymptomatic period in days</li>
          <li><strong>chi</strong> is treatable to infectious rate in days</li>
          <li><strong>nu</strong> is mortality rate</li>
          <li><strong>gamma</strong> is total infectious period in days</li>
      </ul>
      <p>The function called rand_exp() returns the negative log of a random value [0,1) divided by the provided value.</p>
      <p>The values of the different possible transition times determine the path that the individual will take through the compartments. For example, if T{'r<=i'} {'<'} T{'d<=i'}, then the individual will recover (not die) from the infectious period. The path through compartments will determine the identity of events that are seeded onto the event queue.</p>
     </section>

     <section className="text">
        <p><strong>Travel Model</strong></p>
        <p>The current travel model implemented is a Binomial travel model. The travel() method is called from src/simulator.py at the end of each day – after the disease model simulation logic has been applied to each node. In the travel model, all pairwise node combinations are considered. “Sink” refers to the node where people travel to, “Source” refers to the node where people travel from.</p>
        <p>The following pseudocode roughly describes the workflow:</p>
      </section>

      <section className="code-section">
        <pre className="code-chunk">
          <code>
{`1	# travel() method, given NETWORK, DISEASE_MODEL, PARAMS
2	for each SINK NODE:
3	  for each SOURCE NODE:
4	    if flow SINK-to-SOURCE > 0 or flow SOURCE-to-SINK > 0:
5	      for each AGE_1
6	        # adjust beta by PHA effectiveness
7	        for each AGE_2
8	          num_contacts1 += compute_infectious_contacts(SINK to SOURCE)
9	          num_contacts2 += compute_infectious_contacts(SOURCE to SINK)
10	        probabilities += sum(num_contacts1, num_contacts2)
11	
12	  for each COMPARTMENT:
13	    probability <= calculate_probability(probabilities)
14	    num_exposures <= binomial(SINK.susceptible(), probability)
15	    disease_model.expose(SINK, num_exposures)

`}
          </code>
        </pre>
      </section>

      <section className="text">
        <p>A plain text description of the Binomial travel model is as follows:</p>
        <ul className="bullet-points">
          <li><strong>Line 2: </strong>Iterate over every node in the network – this outer iteration is referred to as the sink node, where the infections are occurring.</li>
          <li><strong>Line 3: </strong>Iterate over every node in the network – this inner iteration is referred to as the source node, where the infections are coming from.</li>
          <li><strong>Line 4: </strong>Check in the travel flow input file (in this case called “work_matrix_rel.csv”). If there is a non-zero travel flow value between either the sink-to-source or source-to-sink nodes, then proceed to Line 5, else skip to next source node.</li>
          <li><strong>Line 5: </strong>Iterate over each age group – outer iteration.</li>
          <li><strong>Line 6: </strong>Adjust the value of beta by PHA effectiveness (in progress).</li>
          <li><strong>Line 7: </strong>Iterate over each age group – inner iteration.</li>
          <li><strong>Line 8: </strong>Count the number of infectious contacts that occur during travel from the sink node to the source node</li>
          <li><strong>Line 9: </strong>Count the number of infectious contacts that occur during travel from the source node to the sink node</li>
          <li><strong>Line 10: </strong>After counting the number of infectious contacts that occur across all age groups (inner iteration), divide that count by the total population of the node, multiply by the travel flow data, and add to the probabilities list.</li>
          <li><strong>Line 12: </strong>Iterate over each combination of age group, risk group, and vaccine status group on the sink node.</li>
          <li><strong>Line 13: </strong>Calculate a probability of exposure based on the probabilities (for unvaccinated group) list and the vaccine_effectiveness list (for vaccinated group).</li>
          <li><strong>Line 14: </strong>Use a binomial expression given the total number of susceptible individuals on the sink node and the probability of exposure to calculate the number of individuals in the sink node that were exposed.</li>
          <li><strong>Line 15: </strong>Use the disease_model to expose that number of individuals on the SINK node.</li>
       </ul>
       <p>The main objective of this model is to compute the number of individuals that were infected from travel in each age group in each node. Then, it calls the disease model to transition those individuals from Susceptible => Exposed. In the first step, it calculates the number of infectious contacts that occur for each age group as:</p>
       <p>NIC{'sink=>source'} = (Transmitting * beta * rho * contact_rate * sigma) / flow_reduction</p>
       <p>NIC{'source=>sink'} = (Asymptomatic * beta * rho * contact_rate * sigma) / flow_reduction</p>
       <p>Where:</p>
        <ul className="bullet-points">
            <li><strong>NIC{'sink=>source'}</strong> is the number of infectious contacts that occur during travel from the sink node to the source nodes</li>
            <li><strong>NIC{'source=>sink'}</strong> is the number of infectious contacts that occur during travel from the source node to the sink node</li>
            <li><strong>Transmitting</strong> is the number of transmitting individuals in the source node (asymptomatic, treatable, or infectious)</li>
            <li><strong>Asymptomatic</strong> is the number of asymptomatic individuals in the source node</li>
            <li><strong>beta</strong> is a parameter for the transmissibility of the disease</li>
            <li><strong>rho</strong> is a parameter for the relative decrease in contact rate when travelling</li>
            <li><strong>contact_rate</strong> comes from the matrix of contact rates between age groups</li>
            <li><strong>sigma</strong> is a parameter for the relative susceptibility by age groupy</li>
            <li><strong>flow_reduction</strong> is a parameter representing reduced travel for different age groups</li>
        </ul>
        <p>The model assumes that infectious contacts that occur to sink node individuals travelling to other nodes can occur from contact with any of the transmitting population in source nodes (asymptomatic, treatable, or infectious). On the other hand, the model assumes that treatable and infectious individuals from the source nodes are not themselves travelling. Only asymptomatic individuals from the source nodes can travel to the sink node and create infectious contacts. After enumerating all of the infectious contacts that occur for each age group on the sink node, the probability of transmission for each age group is computed as:</p>
        <p>Prob = ((Flowsink=>source * NICsink=>source) / TotalPopulationsink) + 
                         ((Flowsource=>sink * NICsource=>sink) / TotalPopulationsource)</p>
        <p>Where:</p>

      <ul className="bullet-points">
          <li><strong>Prob</strong> is the probability of transmission per age group</li>
          <li><strong>Flow{'sink=>source'} </strong> is a term for the frequency of individuals traveling from the sink node to the source node taken from the user-input travel flow data</li>
          <li><strong>Flow{'source=>sink'}</strong> is a term for the frequency of individuals traveling from the source node to the sink node taken from the user-input travel flow data</li>
          <li><strong>TotalPopulationsink</strong> is the total population on the sink node</li>
          <li><strong>TotalPopulationsource {'d=t,i'}</strong> is the total population on the source node</li>
      </ul>
       </section> 

        <section className="text">
        <p>After summing up a cumulative probability that transmission occurred for each age group, and from all source nodes, the final step is to use a binomial function to calculate the actual number of individuals that are exposed on the sink node.</p>
        <p>NumExposures = rand_binomial(Susceptible, Prob)</p>
        <p>Where:</p>
        </section>

        <ul className="bullet-points">
          <li><strong>NumExposures</strong> is the actual number of individuals who are exposed on the sink node per age group, per risk group, per vaccine status group</li>
          <li><strong>rand_binomial()</strong> is a function that generates a random integer from a binomial distribution, given</li>
          <li><strong>Susceptible </strong> is the number of Susceptible individuals on the sink node per age group, per risk group, per vaccine status group</li>
        </ul>
      
        <section className="text">
        <p>In this model, the value of Prob is also modulated by the user-input vaccine effectiveness parameters for the vaccinated group.</p>
        </section>

        <section className="appendix-section">
        <h3>Appendix</h3>
        {appendixData.map((entry, index) => (
          <div key={index} className="appendix-entry">
            <p><strong>Filename:</strong> {entry.filename}</p>
            <p><strong>Description:</strong> {entry.description}</p>
            <p><strong>Contents:</strong></p>
            <ul className="contents-list">
              {entry.contents.map((content, i) => (
                <li key={i}>{content}</li>
              ))}
            </ul>
          </div>
        ))}
      </section>
    </div>
  );
};

export default UserGuideView;
