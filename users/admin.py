from django.contrib import admin

# Register your models here.
from .models import Rol
from .models import Usuario
admin.site.register(Rol)
admin.site.register(Usuario)