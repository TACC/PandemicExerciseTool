from django.contrib import admin
from .models import PET


class PETAdmin(admin.ModelAdmin):
    list_displayed = ('disease_name', 
                      'R0', 
                      'beta_scale', 
                      'tau', 
                      'kappa', 
                      'gamma', 
                      'chi', 
                      'rho', 
                      'nu'
                      )

admin.site.register(PET, PETAdmin)

