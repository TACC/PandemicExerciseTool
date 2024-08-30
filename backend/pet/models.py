from django.db import models

# Create your models here.

class PET(models.Model):

    disease_name = models.CharField(max_length=100)
    reproduction_number = models.FloatField()
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

    def __str__(self):
        return(f'{self.disease_name}, R0={self.reproduction_number}, nu={self.nu}') 
