from django.db import models


class PET(models.Model):

    disease_name = models.CharField(max_length=100)
    R0 = models.FloatField()
    beta_scale = models.FloatField()
    tau = models.FloatField()
    kappa = models.FloatField()
    gamma = models.FloatField()
    chi = models.FloatField()
    rho = models.FloatField()
    nu = models.TextField()

    initial_infected = models.TextField(null=True)
    npis = models.TextField(null=True)

    antiviral_effectiveness = models.FloatField(null=True)
    antiviral_wastage_factor = models.FloatField(null=True)
    antiviral_stockpile = models.TextField(null=True)

    vaccine_wastage_factor = models.FloatField(null=True)
    vaccine_pro_rata = models.CharField(max_length=8, choices={'children':'children', 'pro_rata':'pro_rata'}, null=True)
    vaccine_adherence = models.TextField(null=True)
    vaccine_effectiveness = models.TextField(null=True)
    vaccine_stockpile = models.TextField(null=True)
    
    def __str__(self):
        return(f'{self.disease_name}, R0={self.R0}, nu={self.nu}') 




#{
#  "output": "OUTPUT.json",
#  "number_of_realizations": "1",
#  "data": {
#    "population": "data/texas/county_age_matrix_small.csv",
#    "contact": "data/texas/contact_matrix.csv",
#    "flow": "data/texas/work_matrix_rel.csv",
#    "high_risk_ratios": "data/texas/high_risk_ratios.csv",
#    "flow_reduction": "data/texas/flow_reduction.csv",
#    "relative_susceptibility": "data/texas/relative_susceptibility.csv",
#    "nu_value_matrix": "data/texas/nu_value_matrix.csv"
#  },
#  "parameters": {
#    "R0": "1.2",
#    "beta_scale": "10",
#    "tau": "1.2",
#    "kappa": "1.9",
#    "gamma": "4.1",
#    "chi": "1.0",
#    "rho": "0.39",
#    "nu": "high"
#  },
#  "initial_infected": [
#    {
#      "county": "453",
#      "infected": "100",
#      "age_group": "1"
#    },
#    {
#      "county": "113",
#      "infected": "100",
#      "age_group": "1"
#    },
#    {
#      "county": "201",
#      "infected": "100",
#      "age_group": "1"
#    },
#    {
#      "county": "141",
#      "infected": "100",
#      "age_group": "1"
#    },
#    {
#      "county": "375",
#      "infected": "100",
#      "age_group": "1"
#    }
#  ],
#  "non_pharma_interventions": [
#    {
#      "day": "50",
#      "effectiveness": "0.4",
#      "halflife": "10.0"
#    },
#    {
#      "day": "200",
#      "effectiveness": "0.6",
#      "halflife": "50.0"
#    }
#  ],
#  "antivirals": {
#    "antiviral_effectiveness": "1.5",
#    "antiviral_wastage_factor": "60",
#    "antiviral_stockpile": [
#      {
#        "day": "103",
#        "amount": "17830"
#      },
#      {
#        "day": "110",
#        "amount": "65310"
#      },
#      {
#        "day": "117",
#        "amount": "33900"
#      },
#      {
#        "day": "124",
#        "amount": "92230"
#      },
#      {
#        "day": "131",
#        "amount": "48340"
#      }
#    ] 
#  },
#  "vaccines": {
#    "vaccine_wastage_factor": "60",
#    "vaccine_pro_rata": "children",
#    "vaccine_adherence": [
#      "0.4345",
#      "0.298",
#      "0.388",
#      "0.450",
#      "0.696"
#    ],
#    "vaccine_effectiveness": [
#      "0.8",
#      "0.8",
#      "0.8",
#      "0.8",
#      "0.8"
#    ],
#    "vaccine_stockpile": [
#      {
#        "day": "203",
#        "amount": "178300"
#      },
#      {
#        "day": "210",
#        "amount": "653100"
#      },
#      {
#        "day": "217",
#        "amount": "339000"
#      },
#      {
#        "day": "224",
#        "amount": "922300"
#      },
#      {
#        "day": "231",
#        "amount": "483400"
#      }
#    ]
#  }
#}
