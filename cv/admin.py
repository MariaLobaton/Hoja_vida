from django.contrib import admin
from .models import (
    DatosPersonales, ExperienciaLaboral, Reconocimientos, CursosRealizados,
    ProductosAcademicos, ProductosLaborales, VentaGarage
)

admin.site.register(DatosPersonales)
admin.site.register(ExperienciaLaboral)
admin.site.register(Reconocimientos)
admin.site.register(CursosRealizados)
admin.site.register(ProductosLaborales)  # ✅ lo dejamos simple (sin decorator)

# ✅✅✅ AGREGADO: Admin personalizado para ProductosAcademicos
@admin.register(ProductosAcademicos)
class ProductosAcademicosAdmin(admin.ModelAdmin):
    # ✅ Forzamos a que aparezca el campo nuevo en el formulario del admin
    fields = (
        "perfil",
        "nombrerecurso",
        "clasificador",
        "descripcion",
        "fecharecurso",               # ✅ CAMPO NUEVO (debe aparecer)
        "activarparaqueseveaenfront",
        "rutacertificado",
    )

    # ✅ se ve en la lista
    list_display = ("nombrerecurso", "clasificador", "fecharecurso", "activarparaqueseveaenfront")
    list_filter = ("activarparaqueseveaenfront",)
    search_fields = ("nombrerecurso", "clasificador")


@admin.register(VentaGarage)
class VentaGarageAdmin(admin.ModelAdmin):
    list_display = ("nombreproducto", "valordelbien", "estadoproducto", "condicion", "activarparaqueseveaenfront")
    list_filter = ("estadoproducto", "condicion", "activarparaqueseveaenfront")
    search_fields = ("nombreproducto",)
