from django.contrib import admin
from .models import VentaGarage
from .models import (
    DatosPersonales, ExperienciaLaboral, Reconocimientos, CursosRealizados,
    ProductosAcademicos, ProductosLaborales, VentaGarage
)

admin.site.register(DatosPersonales)
admin.site.register(ExperienciaLaboral)
admin.site.register(Reconocimientos)
admin.site.register(CursosRealizados)
admin.site.register(ProductosAcademicos)
admin.site.register(ProductosLaborales)

@admin.register(VentaGarage)
class VentaGarageAdmin(admin.ModelAdmin):
    list_display = ("nombreproducto", "valordelbien", "estadoproducto", "condicion", "activarparaqueseveaenfront")
    list_filter = ("estadoproducto", "condicion", "activarparaqueseveaenfront")
    search_fields = ("nombreproducto",)