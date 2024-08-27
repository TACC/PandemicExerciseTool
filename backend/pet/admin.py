from django.contrib import admin
from .models import PET


class PETAdmin(admin.ModelAdmin):
    list_displayed = ('disease_name', 
                      'reproduction_number', 
                      'beta_scale', 
                      'tau', 
                      'kappa', 
                      'gamma', 
                      'chi', 
                      'rho', 
                      'nu',
                      'vaccine_wastage_factor', 
                      'antiviral_effectiveness', 
                      'antiviral_wastage_factor'
                      )

admin.site.register(PET, PETAdmin)

