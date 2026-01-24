from django import forms
from .models import DatosPersonales

class DatosPersonalesForm(forms.ModelForm):
    class Meta:
        model = DatosPersonales
        fields = [
            "descripcionperfil",
            "apellidos",
            "nombres",
            "nacionalidad",
            "lugarnacimiento",
            "fechanacimiento",
            "numerocedula",
            "sexo",
            "estadocivil",
            "licenciaconducir",
            "telefonoconvencional",
            "telefonofijo",
            "direcciontrabajo",
            "direcciondomiciliaria",
            "sitioweb",
            "fotoperfil",
        ]
