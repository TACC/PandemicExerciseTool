from django.db import models


class PET(models.Model):

    disease_name = models.TextField()
    model_type = models.TextField()
    state=models.TextField()

    R0 = models.FloatField()
    beta_scale = models.FloatField()
    tau = models.FloatField()
    kappa = models.FloatField()
    gamma = models.FloatField()
    chi = models.FloatField()
    rho = models.FloatField()
    nu = models.TextField()
    sigma = models.TextField()
    infectious_period = models.FloatField()
    immune_period = models.FloatField()

    initial_infected = models.TextField(null=True)
    npis = models.TextField(null=True)

    #antiviral_effectiveness = models.FloatField(null=True)
    #antiviral_wastage_factor = models.FloatField(null=True)
    #antiviral_stockpile = models.TextField(null=True)

    vaccine_model = models.TextField(blank=True)
    vaccine_priority_groups = models.TextField(blank=True)
    vaccine_capacity = models.FloatField(blank=True)
    vaccine_effectiveness_lag = models.FloatField(blank=True)
    vaccine_effectiveness = models.TextField(blank=True)
    vaccine_adherence = models.TextField(blank=True)
    vaccine_stockpile = models.TextField(blank=True)
    
    def __str__(self):
        return(f'{self.disease_name}, model_type={self.model_type}, state={self.state}') 

