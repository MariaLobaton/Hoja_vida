from django import forms
from .models import DatosPersonales


class DatosPersonalesForm(forms.ModelForm):
    class Meta:
        model = DatosPersonales
        fields = "__all__"
