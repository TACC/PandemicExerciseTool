from django.db import models


class PET(models.Model):

    disease_name = models.TextField()
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

