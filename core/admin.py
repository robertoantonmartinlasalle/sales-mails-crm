from django.contrib import admin

# Register your models here.
from .models import Empresa

admin.site.register(Empresa) # Para registrar el modelo empresa