// export an array of objects containing data structures used in the backend model
// used in the Appendix section at the bottom of UserGuide.js
const appendixData = [
  {
    filename: 'contact_matrix.csv',
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
    filename: 'county_age_matrix.csv',
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
    filename: 'flow_reduction.csv',
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
    filename: 'high_risk_ratios.csv',
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
    filename: 'relative_susceptibility.csv',
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

export default appendixData;
