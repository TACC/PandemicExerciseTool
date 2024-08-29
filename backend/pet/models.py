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
    nu = models.CharField(max_length=4, choices={'high':'high', 'low':'low'})

    vaccine_wastage_factor = models.IntegerField()
    antiviral_effectiveness = models.FloatField()
    antiviral_wastage_factor = models.IntegerField()

    phas = models.TextField(null=True)

    def __str__(self):
        return(f'{self.disease_name}, R0={self.R0}, nu={self.nu}') 
