// export an object storing disease parameter presets
// these presets were taken from the old C++ desktop app
// used in DiseaseParameters.js (in Home View) to display and load preset diseases
const scenarios = {
    "Slow Transmission, Mild Severity (2009 H1N1)": {
      id: 1,
      disease_name: "2009 H1N1",
      R0: 1.2,
      beta_scale: 10.0,
      tau: 1.2,
      kappa: 1.9,
      gamma: 4.1,
      chi: 1.0,
      rho: 0.39,
      nu: [0.000022319,0.000040975,0.000083729,0.000061809,0.000008978]
    },
    "Slow Transmission, High Severity (1918 Influenza)": {
      id: 2,
      disease_name: "1918 Influenza",
      R0: 1.2,
      beta_scale: 10.0,
      tau: 1.2,
      kappa: 1.9,
      gamma: 4.1,
      chi: 1.0,
      rho: 0.39,
      nu: [0.002013710,0.000766899,0.001312944,0.000481093,0.000127993]
    },
    "Fast Transmission, Mild Severity (2009 H1N1)": {
      id: 3,
      disease_name: "2009 H1N1",
      R0: 1.8,
      beta_scale: 10.0,
      tau: 1.2,
      kappa: 1.9,
      gamma: 4.1,
      chi: 1.0,
      rho: 0.39,
      nu: [0.000022319,0.000040975,0.000083729,0.000061809,0.000008978]
    },
    "Fast Transmission, High Severity (1918 Influenza)": {
      id: 4,
      disease_name: "1918 Influenza",
      R0: 1.8,
      beta_scale: 10.0,
      tau: 1.2,
      kappa: 1.9,
      gamma: 4.1,
      chi: 1.0,
      rho: 0.39,
      nu: [0.002013710,0.000766899,0.001312944,0.000481093,0.000127993]
    }
  };

export default scenarios;
